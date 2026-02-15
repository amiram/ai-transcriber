AI Implementation Plan


4. Iterate on edge cases and add packaging scripts (PyInstaller spec, Inno Setup) in the next change.
3. Run the mock unit test to verify the core logic and UI import.
2. Run static error checks on the new Python files.
1. Create the files above (core, UI, CLI, test, docs).

Next steps (implementation milestones)

- Whisper models are optional at development time; code handles missing dependencies gracefully and offers a mock path for quick tests.
- PyQt6 chosen for the GUI.
- Windows-only packaging (PyInstaller single EXE + Inno Setup installer + portable ZIP).

Assumptions & choices

- Add `requirements.txt` listing runtime dependencies and `README.md` with quick start and packaging notes.
- Add a small test `tests/test_transcriber_mock.py` that runs the core in mock mode for CI verification without heavy model downloads.
- Provide a CLI wrapper `cli/transcribe_cli.py` for batch processing and scripting.
- Build a simple but functional PyQt6 UI in `ui/main_window.py` with: audio input, output path autofill, model selector, language selector, Start/Stop buttons, progress bar, and a log area. Persist last-used model/language in a JSON config in `%APPDATA%` (Windows) with a portable fallback.
- Provide a reusable core module `transcriber.py` that detects device (CUDA/CPU), loads Whisper when available, and falls back to a mock mode when not available.

Scope for this first implementation

Build a Windows-only desktop application (PyQt6) and CLI that uses Whisper (or a local fallback) to transcribe audio files. The app must bundle a Python runtime for distribution (PyInstaller single EXE + installer + portable ZIP). The UI will not expose a GPU toggle: device selection will be automatic.

Goal


