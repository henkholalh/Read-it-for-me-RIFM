#!/usr/bin/env python3
"""Download the Kokoro voice model (~350 MB) into ./models and verify it.

Used by setup.sh (macOS/Linux) and setup.bat (Windows). Safe to run again:
files that are already present and intact are skipped.
"""
import hashlib
import sys
import time
import urllib.request
from pathlib import Path

BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = {
    "kokoro-v1.0.onnx": "7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5",
    "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
}
MODELS = Path(__file__).resolve().parent / "models"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(name: str, expected: str) -> None:
    dest = MODELS / name
    if dest.is_file() and sha256(dest) == expected:
        print(f"OK  {name} already downloaded")
        return
    part = dest.with_name(name + ".part")
    for attempt in range(1, 4):
        try:
            print(f"Downloading {name}…")
            with urllib.request.urlopen(BASE + name, timeout=60) as r, open(part, "wb") as out:
                total = int(r.headers.get("Content-Length") or 0)
                done, last = 0, 0.0
                while chunk := r.read(1 << 20):
                    out.write(chunk)
                    done += len(chunk)
                    if total and time.time() - last > 0.5:
                        last = time.time()
                        print(f"\r  {done * 100 // total:3d}%  ({done >> 20} of {total >> 20} MB)", end="", flush=True)
            print()
            if sha256(part) != expected:
                raise ValueError("checksum mismatch (download corrupted)")
            part.replace(dest)
            print(f"OK  {name}")
            return
        except Exception as e:  # noqa: BLE001
            print(f"\n  attempt {attempt} failed: {e}")
            part.unlink(missing_ok=True)
            time.sleep(2 * attempt)
    sys.exit(f"ERROR: could not download {name}. Check your internet connection and run setup again.")


if __name__ == "__main__":
    MODELS.mkdir(exist_ok=True)
    for n, h in FILES.items():
        download(n, h)
