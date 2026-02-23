#!/usr/bin/env zsh
# transcribe_audio_mac.sh
# macOS / zsh wrapper to run transcribe_hebrew.py with a chosen Python interpreter
# Usage: ./transcribe_audio_mac.sh /path/to/audio.wav [extra args]

set -euo pipefail

echo "\n================================"
echo "Starting transcription..."
echo "================================\n"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/audio [extra args]"
  exit 2
fi

AUDIO="$1"
shift

# Locate the transcribe_hebrew.py script: prefer $HOME/transcribe_hebrew.py, then script directory, then cwd
if [ -f "$HOME/transcribe_hebrew.py" ]; then
  SCRIPT="$HOME/transcribe_hebrew.py"
elif [ -f "$(dirname "$0")/transcribe_hebrew.py" ]; then
  SCRIPT="$(cd "$(dirname "$0")" && pwd)/transcribe_hebrew.py"
elif [ -f "./transcribe_hebrew.py" ]; then
  SCRIPT="$(pwd)/transcribe_hebrew.py"
else
  echo "Error: cannot find transcribe_hebrew.py in $HOME, script dir, or current dir."
  echo "Place transcribe_hebrew.py in one of those locations or set TRANSCRIBER_SCRIPT env var."
  exit 3
fi

# Choose python interpreter
if [ -n "${TRANSCRIBER_PYTHON:-}" ]; then
  PY="$TRANSCRIBER_PYTHON"
else
  if command -v python3 >/dev/null 2>&1; then
    PY=python3
  elif command -v python >/dev/null 2>&1; then
    PY=python
  else
    echo "Error: no python executable found (python3 or python). Set TRANSCRIBER_PYTHON to override."
    exit 4
  fi
fi

# If the project has a .venv next to the script, prefer it
VENV_PY="$(dirname "$SCRIPT")/.venv/bin/python"
if [ -x "$VENV_PY" ]; then
  echo "Using virtualenv python: $VENV_PY"
  PY="$VENV_PY"
fi

# Show chosen interpreter
echo "Using Python: $PY"

# Run the transcription script with all remaining args forwarded
# Quote paths to tolerate spaces
"$PY" "$SCRIPT" "$AUDIO" "$@"
STATUS=$?

echo "\n================================"
echo "Done! (exit $STATUS)"
echo "================================\n"

exit $STATUS

