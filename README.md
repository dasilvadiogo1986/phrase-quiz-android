# Phrase Quiz (Android)

Kivy version of the phrase-guessing quiz, packaged for Android.

## Get the APK (no Android Studio needed)

1. Create a new GitHub repo and push this folder's contents to it (the
   `.github/workflows/build-apk.yml` file must end up at that exact path).
2. On GitHub, go to the **Actions** tab -> **Build APK** -> **Run workflow**
   (or just push to `main`, which triggers it automatically).
3. Wait for the run to finish (first build takes ~15-25 min while it
   downloads the Android SDK/NDK; GitHub's runners have no time limit
   issue like a local sandbox would).
4. Open the completed run, scroll to **Artifacts**, download
   `phrase-quiz-apk`, unzip it to get `phrasequiz-0.1-arm64-v8a-debug.apk`.
5. Copy the APK to your phone and install it (enable "install unknown apps"
   for whatever app you use to open the file).

## Build it yourself instead (Linux/macOS/WSL, with Android SDK deps)

```
pip install buildozer cython
buildozer android debug
```

The APK will show up in `bin/`.

## Files

- `main.py` - the app (Kivy UI + same scoring logic as the desktop CLI)
- `phrases.json` - clue/phrase library, same format as the desktop version
- `buildozer.spec` - Android packaging config (app name, permissions, etc.)
