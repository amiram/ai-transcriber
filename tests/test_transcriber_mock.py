"""Simple test for transcriber.transcribe_file in mock mode."""

from transcriber import transcribe_file
import os


def test_mock_transcription(tmp_path):
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"RIFF....")
    out = tmp_path / "out.txt"
    res = transcribe_file(str(audio), model_name="small", language="en", output_path=str(out), mock=True)
    assert res["output_file"] == str(out)
    assert "MOCK TRANSCRIPTION" in res["transcription"]

