"""
Phrase Quiz - Android app (Kivy)
Same scoring logic as the desktop CLI version, wrapped in a minimal
touch UI: clue card, guess field, submit/next button, feedback + tally.
"""

import json
import random
import re
import string
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout

PHRASES_PATH = Path(__file__).parent / "phrases.json"

RATINGS = [
    (1.00, "PERFECT!", (0.35, 0.85, 0.55, 1)),
    (0.85, "Nailed it!", (0.45, 0.80, 0.55, 1)),
    (0.65, "So close!", (0.85, 0.75, 0.30, 1)),
    (0.45, "Getting there", (0.90, 0.60, 0.30, 1)),
    (0.25, "Cold", (0.85, 0.45, 0.35, 1)),
    (0.00, "Way off", (0.85, 0.35, 0.35, 1)),
]


def normalize(text: str) -> list[str]:
    text = text.lower().strip()
    text = text.translate(str.maketrans("", "", string.punctuation))
    return [w for w in re.split(r"\s+", text) if w]


def score_guess(guess: str, phrase: str):
    """Return (score 0-1, rating label, rgba color)."""
    guess_words = normalize(guess)
    phrase_words = normalize(phrase)

    if not guess_words:
        return (0.0,) + RATINGS[-1][1:]

    if guess_words == phrase_words:
        return (1.0,) + RATINGS[0][1:]

    credit = 0.0
    for word in phrase_words:
        if word in guess_words:
            credit += 1.0
        elif get_close_matches(word, guess_words, n=1, cutoff=0.8):
            credit += 0.5
    word_coverage = credit / len(phrase_words)

    order_similarity = SequenceMatcher(
        None, " ".join(guess_words), " ".join(phrase_words)
    ).ratio()

    final_score = 0.65 * word_coverage + 0.35 * order_similarity
    final_score = max(0.0, min(1.0, final_score))

    for threshold, label, color in RATINGS:
        if final_score >= threshold:
            return final_score, label, color
    return (final_score,) + RATINGS[-1][1:]


KV = """
<RootLayout>:
    orientation: "vertical"
    padding: dp(24)
    spacing: dp(14)
    canvas.before:
        Color:
            rgba: 0.07, 0.08, 0.10, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Label:
        text: "PHRASE QUIZ"
        font_size: "24sp"
        bold: True
        color: 0.40, 0.85, 0.60, 1
        size_hint_y: None
        height: dp(40)

    BoxLayout:
        size_hint_y: None
        height: dp(150)
        padding: dp(18)
        canvas.before:
            Color:
                rgba: 0.13, 0.15, 0.18, 1
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(16)]
        Label:
            text: root.clue_text
            font_size: "17sp"
            color: 0.92, 0.92, 0.94, 1
            halign: "center"
            valign: "middle"
            text_size: self.size

    TextInput:
        id: guess_input
        hint_text: "Type your guess..."
        multiline: False
        font_size: "16sp"
        size_hint_y: None
        height: dp(50)
        padding: [dp(14), dp(14)]
        background_normal: ""
        background_active: ""
        background_color: 0.15, 0.17, 0.20, 1
        foreground_color: 1, 1, 1, 1
        hint_text_color: 0.55, 0.57, 0.60, 1
        cursor_color: 0.40, 0.85, 0.60, 1
        disabled: root.answered
        on_text_validate: root.submit_guess()

    Button:
        text: "Next clue" if root.answered else "Submit guess"
        size_hint_y: None
        height: dp(52)
        background_normal: ""
        background_down: ""
        background_color: 0, 0, 0, 0
        color: 1, 1, 1, 1
        bold: True
        canvas.before:
            Color:
                rgba: (0.20, 0.45, 0.80, 1) if root.answered else (0.20, 0.65, 0.45, 1)
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [dp(12)]
        on_release: root.next_clue() if root.answered else root.submit_guess()

    Label:
        text: root.feedback_text
        font_size: "15sp"
        color: root.feedback_color
        size_hint_y: None
        height: dp(90)
        halign: "center"
        valign: "top"
        text_size: self.size

    Widget:

    Label:
        text: root.tally_text
        font_size: "13sp"
        color: 0.60, 0.62, 0.66, 1
        size_hint_y: None
        height: dp(24)
"""


class RootLayout(BoxLayout):
    clue_text = StringProperty("Loading...")
    feedback_text = StringProperty("")
    feedback_color = ListProperty([1, 1, 1, 1])
    tally_text = StringProperty("")
    answered = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open(PHRASES_PATH, "r", encoding="utf-8") as f:
            self.phrases = json.load(f)
        random.shuffle(self.phrases)
        self.index = -1
        self.total_score = 0.0
        self.rounds = 0
        self.next_clue()

    def _update_tally(self):
        if self.rounds:
            avg = round((self.total_score / self.rounds) * 100)
            self.tally_text = f"Rounds: {self.rounds}   Average: {avg}%"
        else:
            self.tally_text = "Rounds: 0"

    def next_clue(self):
        self.index += 1
        if self.index >= len(self.phrases):
            random.shuffle(self.phrases)
            self.index = 0
        self.current = self.phrases[self.index]
        self.clue_text = self.current["description"]
        self.feedback_text = ""
        self.answered = False
        self.ids.guess_input.text = ""
        self.ids.guess_input.focus = True

    def submit_guess(self):
        if self.answered:
            return
        guess = self.ids.guess_input.text.strip()
        score, label, color = score_guess(guess, self.current["phrase"])
        pct = round(score * 100)

        self.feedback_text = (
            f"Answer: {self.current['phrase']}\n"
            f"You said: {guess or '(nothing)'}\n"
            f"{pct}% - {label}"
        )
        self.feedback_color = list(color)

        self.total_score += score
        self.rounds += 1
        self._update_tally()
        self.answered = True


class PhraseQuizApp(App):
    def build(self):
        Builder.load_string(KV)
        return RootLayout()


if __name__ == "__main__":
    PhraseQuizApp().run()
