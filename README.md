# Read it For Me (RIFM)

*while I concentrate*

Upload a file and hear it read out loud right away, in the voice you choose. The word being spoken is highlighted as it goes.

- **Browse & upload** PDF, Word (.docx), .txt, .md, .html, .csv and .json files, several at once
- **Three kinds of voice**
  | | Kokoro 🎙 | Built-in 💻 | OpenAI ✨ |
  |---|---|---|---|
  | Sound | Natural, human-like | Robotic | Natural, expressive |
  | Cost | Free | Free | Paid, needs an API key |
  | Privacy | Runs on your computer | Runs on your computer | Text is sent to OpenAI |
  | Accents / styles | – | – | Yes, e.g. **Alabama Southern drawl** |
- **Follow along:** a sticky "Now speaking" bar, word-by-word highlighting, and a progress bar
- **Natural pacing:** pauses at headings, bullet points and paragraphs, and PDF line wraps are joined back into sentences
- Play / pause / stop, click any sentence to jump there, speed and pitch control
- Keyboard: <kbd>Space</kbd> pause/resume, <kbd>Esc</kbd> stop

## Requirements

- macOS or Linux
- Python 3.10–3.13 (or [uv](https://docs.astral.sh/uv/), which installs the right Python for you)
- About 500 MB of disk space for the Kokoro voice model
- A modern browser (Chrome, Safari, Edge or Firefox)

## Install

```bash
git clone <this-repo-url> rifm
cd rifm
./setup.sh
```

`setup.sh` creates a local Python environment in `.venv/`, installs the packages, and downloads the Kokoro model (~350 MB) into `models/`. The download is checked against a SHA-256 hash.

## Run

```bash
./start.sh
```

On macOS you can also double-click **`Read it For Me.command`**. The app opens at <http://127.0.0.1:8787>. Keep the terminal window open while you listen, and close it (or press <kbd>Ctrl</kbd>+<kbd>C</kbd>) to quit.

If `start.sh` finds that setup hasn't been done yet, it runs it first. The server only listens on `127.0.0.1`, so other computers can't reach it.

To use a different port: `RIFM_PORT=8788 ./start.sh`

### Without the server

You can also open `index.html` straight from the folder. The **Built-in** and **OpenAI** voices work this way; Kokoro needs the server.

### OpenAI voice (optional)

Choose **✨ OpenAI**, paste an API key from <https://platform.openai.com/api-keys>, then pick a style such as *Alabama* and a voice. The key is stored only in your browser's local storage. The app uses the `gpt-4o-mini-tts` model and sends one sentence at a time.

### Command line

`speak.py` reads a file using the macOS system voices (no setup needed):

```bash
./speak.py document.pdf -v Samantha        # read aloud
./speak.py document.pdf -v Daniel -r 200   # another voice, faster
./speak.py --voices en                     # list English voices
./speak.py document.pdf -o out.m4a         # save to an audio file
```

## Tests

```bash
node tests/test_text.mjs                          # text processing (sentence splitting, PDF line joining…)
.venv/bin/python -m unittest discover tests -v    # server (needs the model from setup.sh)
```

## Project layout

| Path | What it is |
|---|---|
| `index.html` | The whole web app (no build step) |
| `server.py` | Local server: serves the app and runs Kokoro |
| `setup.sh` / `start.sh` | One-time setup / start the app |
| `Read it For Me.command` | macOS double-click launcher |
| `speak.py` | Command-line reader using macOS voices |
| `vendor/` | Local copies of [pdf.js](https://mozilla.github.io/pdf.js/) and [mammoth.js](https://github.com/mwilliamson/mammoth.js) |
| `tests/` | Automated tests |

## Notes

- **Scanned PDFs** (photos of pages) contain no text, so they can't be read without OCR.
- **Speed:** on older Intel Macs, Kokoro may show "Preparing voice…" for a second or two near the start, then it keeps ahead of playback.
- **Word highlighting:** with Kokoro and OpenAI it is estimated from the audio timing; built-in voices report exact word positions.

## Credits

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) voice model (Apache-2.0), run with [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)
- [pdf.js](https://github.com/mozilla/pdf.js) (Apache-2.0) and [mammoth.js](https://github.com/mwilliamson/mammoth.js) (BSD-2-Clause)
