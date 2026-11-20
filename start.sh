#!/bin/bash
# Start Read it For Me (with the free Kokoro AI voice) and open it in the browser.
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ] || [ ! -f models/kokoro-v1.0.onnx ] || [ ! -f models/voices-v1.0.bin ]; then
  echo "First run: setting things up (one time only)…"
  ./setup.sh || { echo; read -n1 -rsp "Setup failed. Press any key to close."; exit 1; }
fi
.venv/bin/python server.py "$@"
status=$?
if [ $status -ne 0 ] && [ -t 0 ]; then echo; read -n1 -rsp "Press any key to close."; fi
exit $status
