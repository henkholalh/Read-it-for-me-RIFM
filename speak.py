#!/usr/bin/env python3
"""Read a file aloud right away with a macOS voice of your choice.

Usage:
  ./speak.py FILE [-v VOICE] [-r WORDS_PER_MIN] [-o out.aiff]
  ./speak.py --voices [LANG]        list voices (optionally filter, e.g. en, de, fr)
  ./speak.py -                       read text from stdin

Supports .txt .md .html .csv .json .rtf .doc .docx (via macOS textutil)
and .pdf (needs `pip install pypdf`).
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path


def list_voices(lang=None):
    out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        m = re.match(r"^(.+?)\s+([a-z]{2}[_-][A-Z0-9]+)\s+#\s*(.*)$", line)
        if not m:
            continue
        name, code, sample = m.groups()
        if lang and not code.lower().startswith(lang.lower()):
            continue
        print(f"{name.strip():<28} {code:<8} {sample}")


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            return "\n\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
        except ImportError:
            pass
        # Fallback: macOS built-in PDFKit via JavaScript for Automation (no install needed)
        jxa = ('ObjC.import("PDFKit");'
               'function run(a){var d=$.PDFDocument.alloc.initWithURL($.NSURL.fileURLWithPath(a[0]));'
               'if(!d||d.isNil())throw "cannot open PDF";return ObjC.unwrap(d.string)||"";}')
        r = subprocess.run(["osascript", "-l", "JavaScript", "-e", jxa, str(path.resolve())],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"Could not read {path.name}: {r.stderr.strip()}")
        return r.stdout
    if ext in {".docx", ".doc", ".rtf", ".html", ".htm", ".odt"}:
        r = subprocess.run(["textutil", "-convert", "txt", "-stdout", str(path)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"Could not read {path.name}: {r.stderr.strip()}")
        return r.stdout
    text = path.read_text(errors="replace")
    if ext == ".md":
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
        text = re.sub(r"[*_`~>]", "", text)
    return text


def main():
    ap = argparse.ArgumentParser(description="Read a file aloud with a macOS voice.")
    ap.add_argument("file", nargs="?", help="file to read, or - for stdin")
    ap.add_argument("-v", "--voice", help="voice name, e.g. Samantha, Daniel, Karen")
    ap.add_argument("-r", "--rate", type=int, help="speed in words per minute (default ~175)")
    ap.add_argument("-o", "--output", help="save to an audio file (.aiff or .m4a) instead of playing")
    ap.add_argument("--voices", nargs="?", const="", metavar="LANG", help="list available voices")
    a = ap.parse_args()

    if a.voices is not None:
        list_voices(a.voices or None)
        return
    if not a.file:
        ap.print_help()
        return

    text = sys.stdin.read() if a.file == "-" else extract_text(Path(a.file).expanduser())
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        sys.exit("No readable text found.")

    cmd = ["say"]
    if a.voice:
        cmd += ["-v", a.voice]
    if a.rate:
        cmd += ["-r", str(a.rate)]
    if a.output:
        cmd += ["-o", a.output]
        if a.output.endswith(".m4a"):
            cmd += ["--data-format=aac"]
    print(f"🔊 Reading {len(text.split())} words" + (f" with {a.voice}" if a.voice else "") +
          " — Ctrl+C to stop", file=sys.stderr)
    try:
        subprocess.run(cmd, input=text, text=True, check=True)
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
    except subprocess.CalledProcessError:
        sys.exit("say failed — check the voice name with --voices")


if __name__ == "__main__":
    main()
