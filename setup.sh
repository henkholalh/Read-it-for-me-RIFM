#!/bin/bash
# One-time setup (macOS / Linux): creates a Python environment and downloads the Kokoro voice model (~350 MB).
set -euo pipefail
cd "$(dirname "$0")"

# 1. Python environment (onnxruntime needs Python 3.10–3.13)
if [ ! -x .venv/bin/python ]; then
  echo "→ Creating Python environment…"
  if command -v uv >/dev/null; then
    uv venv --python 3.12 .venv
  else
    PY=""
    for v in python3.12 python3.13 python3.11 python3.10 python3; do
      if command -v "$v" >/dev/null && "$v" -c 'import sys; exit(not (3,10) <= sys.version_info[:2] <= (3,13))'; then PY="$v"; break; fi
    done
    [ -n "$PY" ] || { echo "❌ Python 3.10–3.13 is required. Install Python 3.12 from https://www.python.org/downloads/ (or install uv: https://docs.astral.sh/uv/)"; exit 1; }
    "$PY" -m venv .venv
  fi
fi

# 2. Packages
echo "→ Installing packages…"
if command -v uv >/dev/null; then
  uv pip install --python .venv/bin/python -q -r requirements.txt
else
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -r requirements.txt
fi

# 3. Voice model (downloaded and checksum-verified)
.venv/bin/python download_models.py

echo "✅ Setup complete. Start the app with ./start.sh (or double-click 'Read it For Me.command' on macOS)."
