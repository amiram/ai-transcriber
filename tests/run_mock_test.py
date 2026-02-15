"""Run mock tests locally without needing external pytest runner.
This script imports the test function and runs it.
"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from tests.test_transcriber_mock import test_mock_transcription


def run():
    import tempfile
    from pathlib import Path
    tmp = Path(tempfile.mkdtemp())
    try:
        test_mock_transcription(tmp)
        print("OK: mock test passed")
    except AssertionError as e:
        print("FAIL: mock test failed:", e)
        raise

if __name__ == '__main__':
    run()

