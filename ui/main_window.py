"""
A basic PyQt6 main window for the Transcriber app.

This module exposes `main()` which launches the GUI. The window provides:
- audio file input (Browse)
- output path box (auto-filled)
- model dropdown
- language dropdown
- Start / Stop buttons
- progress bar
- log area

It uses `transcriber.transcribe_file` in a QThread to avoid blocking the UI. Mock mode can be enabled for testing by setting the environment variable TRANSCRIBER_MOCK to 1/true/yes.
"""
from __future__ import annotations

import sys
import os
import json
import threading
from typing import Optional

from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QFileDialog,
    QMessageBox,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextEdit,
    QProgressBar,
    QHBoxLayout,
)

# Local import
import transcriber

CONFIG_FILE_NAME = "transcriber_config.json"


class TranscribeWorker(QtCore.QThread):
    progress = QtCore.pyqtSignal(float)
    finished_success = QtCore.pyqtSignal(dict)
    finished_error = QtCore.pyqtSignal(str)

    def __init__(self, audio_path: str, model: str, language: Optional[str], output_path: str, mock: bool = False):
        super().__init__()
        self.audio_path = audio_path
        self.model = model
        self.language = language
        self.output_path = output_path
        self._stop_event = threading.Event()
        self.mock = mock

    def run(self):
        try:
            # transcribe_file handles device detection
            result = transcriber.transcribe_file(
                self.audio_path,
                model_name=self.model,
                language=self.language,
                output_path=self.output_path,
                stop_event=self._stop_event,
                mock=self.mock,
            )
            self.finished_success.emit(result)
        except Exception as e:
            self.finished_error.emit(str(e))

    def stop(self):
        self._stop_event.set()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._config = self._load_config()
        self._strings = self._load_locale()

        self.setWindowTitle(self._t("title"))
        self.resize(800, 420)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        # Audio path
        h1 = QHBoxLayout()
        self.audio_input = QLineEdit()
        btn_audio = QPushButton(self._t("browse"))
        btn_audio.clicked.connect(self.browse_audio)
        h1.addWidget(QLabel(self._t("audio_file")))
        h1.addWidget(self.audio_input)
        h1.addWidget(btn_audio)
        layout.addLayout(h1)

        # Output path
        h2 = QHBoxLayout()
        self.output_input = QLineEdit()
        btn_out = QPushButton(self._t("browse"))
        btn_out.clicked.connect(self.browse_output)
        h2.addWidget(QLabel(self._t("output_file")))
        h2.addWidget(self.output_input)
        h2.addWidget(btn_out)
        layout.addLayout(h2)

        # Model + Language
        h3 = QHBoxLayout()
        self.model_cb = QComboBox()
        self.model_cb.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_cb.setCurrentText(self._config.get("model", "small"))

        self.lang_cb = QComboBox()
        # try to populate languages from whisper if available
        try:
            import whisper as _wh
            languages = list(_wh.tokenizer.LANGUAGES.keys()) if hasattr(_wh, 'tokenizer') else []
        except Exception:
            languages = ["auto", "en", "he"]
        self.lang_cb.addItems(languages)
        self.lang_cb.setCurrentText(self._config.get("language", "auto"))

        h3.addWidget(QLabel(self._t("model")))
        h3.addWidget(self.model_cb)
        h3.addStretch()
        h3.addWidget(QLabel(self._t("language")))
        h3.addWidget(self.lang_cb)
        layout.addLayout(h3)

        # Start / Stop
        h4 = QHBoxLayout()
        self.start_btn = QPushButton(self._t("start"))
        self.stop_btn = QPushButton(self._t("stop"))
        self.stop_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_transcription)
        self.stop_btn.clicked.connect(self.stop_transcription)
        h4.addWidget(self.start_btn)
        h4.addWidget(self.stop_btn)
        layout.addLayout(h4)

        # Progress + log
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        layout.addWidget(self.progress)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        # Worker
        self.worker: Optional[TranscribeWorker] = None

        # Load last-used audio/output
        if self._config.get("last_audio"):
            self.audio_input.setText(self._config["last_audio"])
            if not self.output_input.text():
                self.output_input.setText(self._default_output_for(self._config["last_audio"], self.model_cb.currentText()))

        # wire model change => update default output suffix
        self.model_cb.currentTextChanged.connect(self._on_model_change)

    def _t(self, key: str, **kwargs) -> str:
        val = self._strings.get(key, key)
        try:
            return val.format(**kwargs)
        except Exception:
            return val

    def _load_locale(self) -> dict:
        # Decide locale: prefer explicit env TRANSCRIBER_LOCALE, otherwise try APP config language or system LANG
        prefer = os.getenv("TRANSCRIBER_LOCALE") or self._config.get("ui_locale") or os.getenv("LANG", "en")
        prefer = prefer.split(".")[0]  # strip encoding like en_US.UTF-8
        lang = "he" if prefer.lower().startswith("he") else "en"
        root = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(root, "locales", f"{lang}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # fallback to embedded defaults
            return {
                "title": "Transcriber",
                "audio_file": "Audio file:",
                "browse": "Browse...",
                "output_file": "Output file:",
                "model": "Model:",
                "language": "Language:",
                "start": "Start",
                "stop": "Stop",
                "missing_input": "Please select an audio file.",
                "not_found": "The selected audio file does not exist.",
                "overwrite_question": "Output file exists:\n{path}\nOverwrite?",
                "starting_transcription": "Starting transcription: {audio} -> {out} (model={model}, language={language}, mock={mock})",
                "done_wrote": "Done. Wrote: {path}",
                "error_transcription": "Transcription error",
                "overwrite_title": "Overwrite?",
                "select_audio_title": "Select audio file",
                "select_output_title": "Select output file",
            }

    def _on_model_change(self, model_name: str):
        if self.audio_input.text() and not self.output_input.text():
            self.output_input.setText(self._default_output_for(self.audio_input.text(), model_name))

    def _default_output_for(self, audio_path: str, model_name: str) -> str:
        base = os.path.splitext(os.path.basename(audio_path))[0]
        dirpath = os.path.dirname(audio_path) or os.getcwd()
        return os.path.join(dirpath, f"{base}_transcription_{model_name}.txt")

    def browse_audio(self):
        # Start browsing in last used directory (fallback to user's Documents)
        default_dir = self._config.get("last_dir") or os.path.join(os.path.expanduser("~"), "Documents")
        fname, _ = QFileDialog.getOpenFileName(self, self._t("select_audio_title"), default_dir)
        if fname:
            self.audio_input.setText(fname)
            # remember last directory and update config
            self._config["last_dir"] = os.path.dirname(fname)
            # set default output if empty
            if not self.output_input.text():
                self.output_input.setText(self._default_output_for(fname, self.model_cb.currentText()))
            self._save_config()

    def browse_output(self):
        # Start browsing in last used directory (fallback to user's Documents)
        default_dir = self._config.get("last_dir") or os.path.join(os.path.expanduser("~"), "Documents")
        fname, _ = QFileDialog.getSaveFileName(self, self._t("select_output_title"), default_dir, filter="Text files (*.txt);;All files (*)")
        if fname:
            self.output_input.setText(fname)
            # remember last directory and persist
            self._config["last_dir"] = os.path.dirname(fname)
            self._save_config()

    def _load_config(self) -> dict:
        # Try APPDATA first for Windows, otherwise use local folder
        appdata = os.getenv("APPDATA")
        if appdata:
            cfg_path = os.path.join(appdata, "Transcriber")
            try:
                os.makedirs(cfg_path, exist_ok=True)
            except Exception:
                cfg_path = os.getcwd()
        else:
            cfg_path = os.getcwd()
        full = os.path.join(cfg_path, CONFIG_FILE_NAME)
        if os.path.exists(full):
            try:
                with open(full, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        # Default last_dir -> user's Documents folder if available
        default_docs = os.path.join(os.path.expanduser("~"), "Documents")
        return {"model": "small", "language": "auto", "last_dir": default_docs}

    def _save_config(self):
        appdata = os.getenv("APPDATA")
        if appdata:
            cfg_dir = os.path.join(appdata, "Transcriber")
            try:
                os.makedirs(cfg_dir, exist_ok=True)
                cfg_file = os.path.join(cfg_dir, CONFIG_FILE_NAME)
                # persist last used folder (prefer explicit config value, otherwise derived from audio input)
                last_dir = self._config.get("last_dir") or (os.path.dirname(self.audio_input.text()) if self.audio_input.text() else os.getcwd())
                payload = {"model": self.model_cb.currentText(), "language": self.lang_cb.currentText(), "last_audio": self.audio_input.text(), "last_dir": last_dir}
                with open(cfg_file, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
            except Exception:
                # best-effort: ignore config save errors
                pass

    def start_transcription(self):
        audio = self.audio_input.text().strip()
        out = self.output_input.text().strip()
        if not audio:
            QMessageBox.warning(self, self._t("missing_input"), self._t("missing_input"))
            return
        if not os.path.exists(audio):
            QMessageBox.warning(self, self._t("not_found"), self._t("not_found"))
            return
        if not out:
            out = self._default_output_for(audio, self.model_cb.currentText())
            self.output_input.setText(out)

        # Overwrite handling
        if os.path.exists(out):
            ret = QMessageBox.question(self, self._t("overwrite_title"), self._t("overwrite_question", path=out), QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
            if ret == QMessageBox.StandardButton.Cancel:
                return
            if ret == QMessageBox.StandardButton.No:
                # create a new filename with suffix
                base, ext = os.path.splitext(out)
                i = 1
                while True:
                    candidate = f"{base} ({i}){ext}"
                    if not os.path.exists(candidate):
                        out = candidate
                        self.output_input.setText(out)
                        break
                    i += 1

        model = self.model_cb.currentText()
        language = self.lang_cb.currentText()

        # Save config
        self._save_config()

        # Mock mode via environment variable for predictable behavior in packaged apps and CI
        mock_env = os.getenv("TRANSCRIBER_MOCK", "").lower()
        mock = mock_env in ("1", "true", "yes")

        self.log.append(self._t("starting_transcription", audio=audio, out=out, model=model, language=language, mock=mock))
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress.setValue(0)

        self.worker = TranscribeWorker(audio, model, language, out, mock=mock)
        self.worker.finished_success.connect(self._on_success)
        self.worker.finished_error.connect(self._on_error)
        self.worker.start()

    def stop_transcription(self):
        if self.worker:
            self.worker.stop()
            self.log.append("Stop requested...")
            self.stop_btn.setEnabled(False)

    def _on_success(self, result: dict):
        self.log.append(self._t("done_wrote", path=result.get('output_file')))
        self.progress.setValue(100)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def _on_error(self, error: str):
        self.log.append(f"Error: {error}")
        QMessageBox.critical(self, self._t("error_transcription"), error)
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
