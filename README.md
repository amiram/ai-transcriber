Transcriber (PyQt6 + Whisper)

Quick start (developer environment)

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
# For full transcription capability install torch and whisper as in the comments in requirements.txt
```

2. Run the GUI (developer mode):

```bash
python -m ui.main_window
```

3. Run the CLI (mock mode for testing without models):

```bash
python -m cli.transcribe_cli --mock sample.mp3
```

Packaging notes

- Recommended: PyInstaller single-file EXE + Inno Setup installer for Windows distribution. This will embed a Python runtime so end users don't need Python installed.
- We'll add the exact PyInstaller spec and Inno Setup script in the next iteration.

