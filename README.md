# Read it For Me (RIFM)

*while I concentrate*

Upload a document and RIFM reads it out loud straight away, in the voice you choose. The sentence and word being spoken are highlighted as it goes, so you can follow along or look away and just listen.

Works on **Mac** and **Windows** laptops.

---

## What it does

- 📂 **Browse & upload** PDF, Word (.docx), .txt, .md, .html, .csv and .json files, several at once, or drag and drop them
- 🔊 **Starts reading immediately** and highlights each sentence and word in a "Now speaking" bar
- 🗣 **Pick your voice** from three kinds:

  | | 🎙 Kokoro | 💻 Built-in | ✨ OpenAI |
  |---|---|---|---|
  | Sounds | Natural, human-like | Robotic | Natural and expressive |
  | Cost | Free | Free | Paid (about 1–2¢ per minute), needs an API key |
  | Privacy | Stays on your laptop | Stays on your laptop | Text is sent to OpenAI |
  | Works offline | ✅ | ✅ | ❌ |
  | Accents and styles | – | – | ✅ e.g. **Alabama Southern drawl**, storyteller, newsreader |
  | Languages | English (US/UK), Spanish, French, Italian, Hindi, Japanese, Portuguese, Chinese | Whatever your system has | Many |

- ⏯ Play, pause and stop, click any sentence to jump there, and adjust speed (and pitch for built-in voices)
- 🧠 Natural pacing: it pauses at headings, bullet points and paragraphs, and joins lines that a PDF wraps mid-sentence

---

## Install and run on a Mac

**You need:** macOS 12 or newer, about 1 GB of free space, and an internet connection for the first setup.

1. **Install Python 3.12** (skip this if you already have Python 3.10–3.13).
   Download the macOS installer from <https://www.python.org/downloads/macos/> and run it.

2. **Download RIFM.** On this GitHub page click the green **Code** button, then **Download ZIP**. Unzip it, for example into your *Documents* folder.
   (Or, if you use git: `git clone https://github.com/henkholalh/Read-it-for-me-RIFM.git`)

3. **Start it.** Open the folder and double-click **`Read it For Me.command`**.
   - The first time, macOS may say it *"cannot be opened because it is from an unidentified developer"*. Right-click (or Control-click) the file, choose **Open**, then **Open** again. You only need to do this once.
   - The first launch sets everything up automatically and downloads the voice model (~350 MB). This takes a few minutes. Later launches take a few seconds.

4. The app opens in your browser at **<http://127.0.0.1:8787>**. Keep the Terminal window open while you listen, and close it when you're done.

<details>
<summary>Prefer the Terminal?</summary>

```bash
cd ~/Documents/Read-it-for-me-RIFM-main   # the folder you unzipped
./setup.sh     # one time
./start.sh     # every time
```
</details>

---

## Install and run on Windows

**You need:** Windows 10 or 11, about 1 GB of free space, and an internet connection for the first setup.

1. **Install Python 3.12** (skip this if you already have Python 3.10–3.13).
   Download the Windows installer from <https://www.python.org/downloads/windows/>, run it, and **tick "Add python.exe to PATH"** on the first screen.

2. **Download RIFM.** On this GitHub page click the green **Code** button, then **Download ZIP**. Right-click the ZIP, choose **Extract All…**, and extract it, for example into *Documents*.
   (Or, if you use git: `git clone https://github.com/henkholalh/Read-it-for-me-RIFM.git`)

3. **Start it.** Open the folder and double-click **`Read it For Me.bat`**.
   - If Windows shows *"Windows protected your PC"*, click **More info**, then **Run anyway**.
   - The first launch sets everything up automatically and downloads the voice model (~350 MB). This takes a few minutes. Later launches take a few seconds.
   - If Windows Firewall asks about Python, you can click **Cancel**. RIFM only talks to your own laptop.

4. The app opens in your browser at **<http://127.0.0.1:8787>**. Keep the black command window open while you listen, and close it when you're done.

<details>
<summary>Prefer the command prompt?</summary>

```bat
cd %USERPROFILE%\Documents\Read-it-for-me-RIFM-main
setup.bat      &rem one time
start.bat      &rem every time
```
</details>

---

## How to use it

1. Click **📂 Browse & Upload Files** and pick one or more documents, or drag them onto the page.
2. It starts reading the first file right away. Click another file in the list to switch to it.
3. Choose a voice at the top:
   - **🎙 Kokoro:** pick a voice from the list. The ★ ones sound best (try *Michael*, *Fenrir*, *Heart* or *Bella*).
   - **💻 Built-in:** your computer's own voices. To add better ones:
     - *Mac:* System Settings → Accessibility → Spoken Content → System Voice → Manage Voices (choose "Enhanced" or "Premium" voices)
     - *Windows:* Settings → Time & language → Speech → Add voices
   - **✨ OpenAI:** paste an API key from <https://platform.openai.com/api-keys> (you'll need a little credit on the account), then choose a style such as **Alabama** and a voice. You can also write your own description of how it should sound.
4. Use **Pause**, **Stop** and the **Speed** slider, or click any sentence to jump there.

**Keyboard shortcuts:** <kbd>Space</kbd> pause/resume · <kbd>Esc</kbd> stop

---

## Troubleshooting

| Problem | Fix |
|---|---|
| *"Python 3.10–3.13 is required"* | Install Python 3.12 (see the steps above). On Windows, tick **Add python.exe to PATH**. Newer Python versions aren't supported by the voice engine yet. |
| *"Kokoro isn't running"* in the app | Start the app with `Read it For Me.command` (Mac) or `Read it For Me.bat` (Windows), not by opening `index.html` directly. |
| *"Port 8787 is used by another program"* | Another program is using that port. Mac: `RIFM_PORT=8788 ./start.sh`. Windows: `set RIFM_PORT=8788 && start.bat` |
| The download failed or stopped | Run setup again: `./setup.sh` (Mac) or `setup.bat` (Windows). It continues where it left off and checks the files. |
| A PDF says *"No readable text found"* | It's a scanned PDF (pictures of pages). It needs OCR text recognition first. |
| There's a short "Preparing voice…" at the start | Normal on older laptops. Kokoro prepares the first sentences, then stays ahead. |
| OpenAI says *rate limit* or *no credit* | Add credit to your OpenAI account, or use Kokoro (free). |

---

## For developers

| Path | What it is |
|---|---|
| `index.html` | The whole web app (no build step) |
| `server.py` | Local server: serves the app and runs Kokoro (listens on `127.0.0.1` only) |
| `download_models.py` | Downloads and checksum-verifies the Kokoro model |
| `setup.sh` / `setup.bat` | One-time setup for macOS/Linux / Windows |
| `start.sh` / `start.bat` | Start the app (runs setup first if needed) |
| `Read it For Me.command` / `.bat` | Double-click launchers for Mac / Windows |
| `speak.py` | Command-line reader using the macOS `say` voices (Mac only) |
| `vendor/` | Local copies of pdf.js and mammoth.js, so the app works offline |
| `tests/` | Automated tests |

**Run the tests**

```bash
node tests/test_text.mjs                          # text processing
.venv/bin/python -m unittest discover tests -v    # server (Windows: .venv\Scripts\python.exe -m unittest discover tests -v)
```

**Settings (environment variables):** `RIFM_PORT` (default `8787`), `RIFM_MODEL`, `RIFM_VOICES` (model file paths).

**Command-line reader (Mac only)**

```bash
./speak.py document.pdf -v Samantha        # read a file aloud
./speak.py --voices en                     # list English voices
./speak.py document.pdf -o out.m4a         # save as an audio file
```

---

## Credits

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) voice model (Apache-2.0), run with [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)
- [pdf.js](https://github.com/mozilla/pdf.js) (Apache-2.0) and [mammoth.js](https://github.com/mwilliamson/mammoth.js) (BSD-2-Clause)

## License

RIFM is released under the [MIT License](LICENSE): you're free to use, copy, modify and share it.
The voice model and bundled libraries listed above keep their own licenses.
