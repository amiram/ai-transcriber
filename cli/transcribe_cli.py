"""
Simple CLI wrapper for batch transcription.

Usage:
  python -m cli.transcribe_cli --model small --lang en file1.mp3 file2.wav

Notes:
- If whisper/torch are not installed, use --mock to avoid requiring models.
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import List

# make local imports work when running as a module from project root
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from transcriber import transcribe_file, detect_device


def main(argv: List[str] | None = None):
    parser = argparse.ArgumentParser(description="Batch transcribe audio files")
    parser.add_argument("files", nargs="+", help="Audio files to transcribe")
    parser.add_argument("--model", default="large", help="Whisper model to use (tiny, base, small, medium, large)")
    parser.add_argument("--lang", default=None, help="Language code (e.g. en, he). Use auto or omit to let model detect language")
    parser.add_argument("--out-dir", default=None, help="Directory to place transcriptions (defaults to each file's dir)")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode (no real models required)")

    args = parser.parse_args(argv)

    for f in args.files:
        if not os.path.exists(f):
            print(f"File not found: {f}")
            continue
        out_dir = args.out_dir or os.path.dirname(f) or os.getcwd()
        base = os.path.splitext(os.path.basename(f))[0]
        out_name = os.path.join(out_dir, f"{base}_transcription_{args.model}.txt")
        try:
            res = transcribe_file(f, model_name=args.model, language=args.lang, output_path=out_name, mock=args.mock)
            print(f"Wrote: {res.get('output_file')}")
        except Exception as e:
            print(f"Error transcribing {f}: {e}")


if __name__ == "__main__":
    main()
