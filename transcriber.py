"""
transcriber.py

Core transcription utilities. Responsible for device detection and single-file transcription.
This module prefers to use `whisper` (and `torch`) when available. If not available, it can run in
`mock` mode for quick testing (no model downloads required).

API:
- detect_device() -> str
- transcribe_file(audio_path, model_name, language, output_path, progress_callback=None, stop_event=None, mock=False) -> dict

Behavior:
- Attempts to import whisper and torch. If missing and mock=False, raises ImportError with instructions.
- If mock=True, writes a tiny dummy transcription output and returns a result dict.

"""

from __future__ import annotations

import os
import json
import time
import sys
from typing import Callable, Optional, Dict, Any
import threading


def detect_device() -> str:
    """Detects whether a CUDA-capable GPU is available and returns the device to use ('cuda' or 'cpu').
    Falls back to 'cpu' if torch is not installed or CUDA is not available.
    """
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    return "cpu"


def _format_paragraphs_from_segments(segments: list[Dict[str, Any]]) -> str:
    paragraphs = []
    current_paragraph = []
    for i, segment in enumerate(segments):
        text = segment.get("text", "").strip()
        if not text:
            continue
        current_paragraph.append(text)
        if len(current_paragraph) >= 3 or (i < len(segments) - 1 and segments[i+1].get("start", 0) - segment.get("end", 0) > 2.0):
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    return "\n\n".join(paragraphs)


def transcribe_file(
    audio_path: str,
    model_name: str = "large",
    language: Optional[str] = None,
    output_path: Optional[str] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
    stop_event: Optional[threading.Event] = None,
    mock: bool = False,
) -> Dict[str, Any]:
    """Transcribe a single audio file.

    Returns a result dict with keys: `model`, `device`, `transcription`, `output_file`.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    device = detect_device()

    if mock:
        # Produce a small deterministic fake transcription for tests and CI
        text = f"[MOCK TRANSCRIPTION for {os.path.basename(audio_path)} with model={model_name} language={language}]"
        time.sleep(0.3)  # simulate work
        formatted = text
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Model: {model_name}\nDevice: {device}\n\n")
                f.write(formatted)
        return {"model": model_name, "device": device, "transcription": formatted, "output_file": output_path}

    # Real mode - try to use whisper (and torch)
    try:
        # Try importing whisper; support potential alternate package names
        try:
            import whisper
        except Exception:
            try:
                import openai_whisper as whisper  # some installs may alias differently
            except Exception:
                whisper = None

        try:
            import torch
        except Exception:
            torch = None

        if whisper is None or torch is None:
            raise ImportError("missing")
    except ImportError as e:
        # Build helpful diagnostics so users can install into the same Python environment
        exe = sys.executable or "python"
        msg_lines = [
            "whisper and/or torch not available in this Python environment.",
            "Details:",
            f"  sys.executable: {exe}",
            f"  sys.path: {sys.path}",
            "Recommendation:",
            f"  Install inside this Python: {exe} -m pip install -U openai-whisper",
            "  For torch, follow the official install instructions: https://pytorch.org/ (choose correct CUDA/cpu build).",
            "If you are running the GUI or a packaged exe, ensure the runtime includes these packages or use mock mode.",
            "To run a quick test without models, call transcribe_file(..., mock=True).",
        ]
        raise ImportError("\n".join(msg_lines)) from e

    # Load model
    model = whisper.load_model(model_name)
    try:
        # move model to device if possible
        if device == "cuda":
            model.to("cuda")
    except Exception:
        # best-effort, continue on CPU
        device = "cpu"

    # Transcribe
    # whisper.transcribe will do its own progress printing; we call it and then postprocess
    result = model.transcribe(audio_path, language=language, fp16=False)
    segments = result.get("segments", [])
    formatted = _format_paragraphs_from_segments(segments)

    # Save
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"Model: {model_name}\nDevice: {device}\n\n")
            f.write(formatted)

    return {"model": model_name, "device": device, "transcription": formatted, "output_file": output_path}


if __name__ == "__main__":
    # Simple CLI quick-run for local dev
    import argparse

    parser = argparse.ArgumentParser(description="Transcribe a single audio file (dev helper)")
    parser.add_argument("audio_file")
    parser.add_argument("--model", default="small")
    parser.add_argument("--lang", default=None)
    parser.add_argument("--out", default=None)
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no model required)")

    args = parser.parse_args()
    out = args.out or os.path.splitext(args.audio_file)[0] + "_transcription_" + args.model + ".txt"
    res = transcribe_file(args.audio_file, model_name=args.model, language=args.lang, output_path=out, mock=args.mock)
    print("Wrote:", res.get("output_file"))
