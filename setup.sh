#!/bin/bash
# One-time setup: creates a Python environment and downloads the Kokoro voice model (~350 MB).
set -euo pipefail
cd "$(dirname "$0")"

MODEL_URL="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
MODEL_SHA="7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5"
VOICES_SHA="bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d"

sha256() { if command -v shasum >/dev/null; then shasum -a 256 "$1"; else sha256sum "$1"; fi | cut -d' ' -f1; }

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
    [ -n "$PY" ] || { echo "❌ Python 3.10–3.13 is required (or install uv: https://docs.astral.sh/uv/)"; exit 1; }
    "$PY" -m venv .venv
  fi
fi
echo "→ Installing packages…"
if command -v uv >/dev/null; then
  uv pip install --python .venv/bin/python -q -r requirements.txt
else
  .venv/bin/python -m pip install -q --upgrade pip
  .venv/bin/python -m pip install -q -r requirements.txt
fi

# 2. Voice model
mkdir -p models
fetch() {  # file sha
  local f="models/$1"
  if [ -f "$f" ] && [ "$(sha256 "$f")" = "$2" ]; then echo "✓ $1 already downloaded"; return; fi
  echo "→ Downloading $1…"
  curl -fL --retry 3 --progress-bar -o "$f.part" "$MODEL_URL/$1"
  [ "$(sha256 "$f.part")" = "$2" ] || { rm -f "$f.part"; echo "❌ $1 download is corrupted, please run setup again."; exit 1; }
  mv "$f.part" "$f"
}
fetch kokoro-v1.0.onnx "$MODEL_SHA"
fetch voices-v1.0.bin "$VOICES_SHA"

echo "✅ Setup complete. Start the app with ./start.sh (or double-click 'Read Aloud.command' on macOS)."
