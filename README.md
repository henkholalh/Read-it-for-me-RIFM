# 📖 Read it For Me (RIFM)

*while I concentrate*

[![CI](https://github.com/henkholalh/Read-it-for-me-RIFM/actions/workflows/ci.yml/badge.svg)](https://github.com/henkholalh/Read-it-for-me-RIFM/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Platforms](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Give it a document, a web page or an email, and it reads it out loud in a natural voice.**
Each sentence and word lights up as it's spoken, so you can follow along, or look away and just listen.

✅ Free &nbsp;·&nbsp; ✅ Works on Mac and Windows &nbsp;·&nbsp; ✅ Private: your files stay on your computer

**Jump to:** [What it can do](#-what-it-can-do) · [Install on Mac](#-install-on-a-mac) · [Install on Windows](#-install-on-windows) · [How to use it](#-how-to-use-it) · [Help](#-help-something-isnt-working) · [Contributing](#-contributing)

---

## ✨ What it can do

| | |
|---|---|
| 📂 **Read your documents** | PDF, Word (.docx), text, Markdown, HTML, CSV and JSON. Drop in several at once. |
| 🔗 **Read web pages** | Paste a link and it reads the article, without the menus, ads and footers. |
| 📧 **Read your email** | One click on a bookmark reads the email you have open. Works with Gmail, Outlook and others. |
| 📄 **Page by page** | See one page at a time, jump to any page, or click any sentence to start there. The page turns by itself as it reads. |
| 🗣 **Sounds like a person** | Reads *e.g.* as "for example", *Q1* as "Question 1" and *yes/no* as "yes or no", and pauses at headings and paragraphs. |
| ⏯ **Easy controls** | Play, Pause and Stop stay at the top of the screen. Change the speed whenever you like. |

### Pick a voice

| | 🎙 **Kokoro** (recommended) | 💻 **Built-in** | ✨ **OpenAI** |
|---|---|---|---|
| Sound | Natural, human-like | Robotic | Natural and expressive |
| Cost | Free | Free | About 1–2¢ per minute |
| Privacy | Stays on your computer | Stays on your computer | Text is sent to OpenAI |
| Works offline | ✅ | ✅ | ❌ |
| Extras | 54 voices in 9 languages | Your computer's own voices | Accents and styles, like an **Alabama Southern drawl** |

---

## 🍎 Install on a Mac

**You need:** macOS 12 or newer, about 1 GB of free space, and internet for the first setup.

**Step 1: Install Python** (skip this if you already have Python 3.10–3.13)
Download the installer from <https://www.python.org/downloads/macos/> and run it.

**Step 2: Download Read it For Me**
At the top of this page, click the green **Code** button, then **Download ZIP**. Unzip it, for example into your *Documents* folder.

**Step 3: Start it**
Open the folder and double-click **`Read it For Me.command`**. The app opens in your browser.

> 💡 **First time only:**
> - If macOS says the file *"is from an unidentified developer"*, right-click the file, choose **Open**, then click **Open** again.
> - The first start downloads the voice (about 350 MB) and takes a few minutes. After that it starts in seconds.

**Every time after that:** double-click **`Read it For Me.command`** again. Keep the Terminal window open while you listen, and close it when you're done.

> ⭐ **Tip:** drag `Read it For Me.command` onto your Dock, next to the Trash, to start the app with one click.

---

## 🪟 Install on Windows

**You need:** Windows 10 or 11, about 1 GB of free space, and internet for the first setup.

**Step 1: Install Python** (skip this if you already have Python 3.10–3.13)
Download the installer from <https://www.python.org/downloads/windows/>. On the first screen, **tick "Add python.exe to PATH"**, then install.

**Step 2: Download Read it For Me**
At the top of this page, click the green **Code** button, then **Download ZIP**. Right-click the ZIP file, choose **Extract All…**, and extract it, for example into *Documents*.

**Step 3: Start it**
Open the folder and double-click **`Read it For Me.bat`**. The app opens in your browser.

> 💡 **First time only:**
> - If Windows says *"Windows protected your PC"*, click **More info**, then **Run anyway**.
> - If Windows Firewall asks about Python, click **Cancel**. The app only talks to your own computer.
> - The first start downloads the voice (about 350 MB) and takes a few minutes. After that it starts in seconds.

**Every time after that:** double-click **`Read it For Me.bat`** again. Keep the black window open while you listen, and close it when you're done.

---

## 🎧 How to use it

The app runs in your browser at **<http://127.0.0.1:8787>** while it's started.

### Read a document
Click **📂 Browse & Upload Files**, or drag files onto the page. Reading starts right away.

### Read a web page
Paste a link into the box under the upload button and click **🔗 Read link**.
You can also drag a link from your browser straight onto the app.

### Read an email (or any page you're logged in to)
Set it up once:
1. In the app, click **📌 Read emails and other pages you're logged in to**.
2. Show your browser's bookmarks bar: <kbd>⌘ Cmd</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd> on a Mac, <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>B</kbd> on Windows.
3. Drag the **📖 Read it For Me** button onto the bookmarks bar.

Then open any email and click **📖 Read it For Me** on your bookmarks bar.
To read just part of a page, select that text first.

> 🔒 The app never sees your password. The bookmark only passes on the text of the page you already have open.

### While it's reading
- **Pause, Stop and Speed** are always at the top of the screen.
- **◀ Page ▶** moves between pages. **Play** starts from the top of the page you're looking at.
- **Click any sentence** to start reading from there.
- **Click another file** in the list to switch to it.

**Keyboard shortcuts:** <kbd>Space</kbd> play/pause · <kbd>Esc</kbd> stop · <kbd>←</kbd> <kbd>→</kbd> previous/next page

### Choosing a voice
- **🎙 Kokoro:** the ★ voices sound best. Try *Michael*, *Fenrir*, *Heart* or *Bella*.
- **💻 Built-in:** to get better voices for free:
  - *Mac:* System Settings → Accessibility → Spoken Content → System Voice → Manage Voices (pick "Enhanced" or "Premium")
  - *Windows:* Settings → Time & language → Speech → Add voices
- **✨ OpenAI:** paste an API key from <https://platform.openai.com/api-keys> (the account needs a little credit), then pick a style such as **Alabama** and a voice.

---

## 🆘 Help, something isn't working

<details>
<summary><b>The app says "Kokoro isn't running", or the page won't open</b></summary>

Start the app by double-clicking `Read it For Me.command` (Mac) or `Read it For Me.bat` (Windows), and keep its window open.
Opening `index.html` directly doesn't work.
</details>

<details>
<summary><b>"Python 3.10–3.13 is required"</b></summary>

Install Python 3.12 (see Step 1 above). On Windows, make sure you ticked **Add python.exe to PATH**.
Newer Python versions aren't supported by the voice engine yet.
</details>

<details>
<summary><b>"Port 8787 is used by another program"</b></summary>

Another program is using that port. Start the app on a different one:
- Mac: `RIFM_PORT=8788 ./start.sh`
- Windows: `set RIFM_PORT=8788 && start.bat`
</details>

<details>
<summary><b>The voice download failed or stopped</b></summary>

Run setup again: `./setup.sh` (Mac) or `setup.bat` (Windows). It continues where it left off.
</details>

<details>
<summary><b>A web link says "The website refused", or reads very little</b></summary>

Some websites need a login, block apps like this one, or only show their text after it loads in a browser.
Open the page in your browser and use the **📖 Read it For Me** bookmark instead, or copy the text and paste it into the app.
</details>

<details>
<summary><b>The 📖 Read it For Me bookmark does nothing</b></summary>

- Make sure the app is running.
- If your browser blocks the pop-up, allow pop-ups for that website and click again.
- If it says *"not set up"*, drag a fresh bookmark from the app.
</details>

<details>
<summary><b>A PDF says "No readable text found"</b></summary>

It's a scanned PDF: the pages are pictures, not text. It needs text recognition (OCR) first.
</details>

<details>
<summary><b>There's a short "Preparing voice…" pause at the start</b></summary>

That's normal on older computers. Kokoro prepares the first sentences, then stays ahead.
</details>

<details>
<summary><b>OpenAI says "rate limit" or "no credit"</b></summary>

Add credit to your OpenAI account, or switch to Kokoro, which is free.
</details>

Still stuck? [Report a problem](https://github.com/henkholalh/Read-it-for-me-RIFM/issues/new?template=bug_report.yml) or [ask a question](https://github.com/henkholalh/Read-it-for-me-RIFM/discussions).

---

## 🔒 Privacy

- With **Kokoro** or **Built-in** voices, everything stays on your computer.
- With **OpenAI**, the text being read is sent to OpenAI.
- **Web links** are downloaded by the app on your computer. For safety it only opens public websites, never your own computer or home network.
- The app only accepts requests from its own page, so other websites can't use it.

---

## 🤝 Contributing

Everyone is welcome: code, documentation, testing, bug reports or ideas. You don't need to be an expert.

- 📖 Start with the **[Contributing guide](CONTRIBUTING.md)**
- 🐞 [Report a bug](https://github.com/henkholalh/Read-it-for-me-RIFM/issues/new?template=bug_report.yml) · 💡 [Suggest a feature](https://github.com/henkholalh/Read-it-for-me-RIFM/issues/new?template=feature_request.yml) · 💬 [Join the discussions](https://github.com/henkholalh/Read-it-for-me-RIFM/discussions)
- 🤝 Please follow our [Code of Conduct](CODE_OF_CONDUCT.md)
- 🔒 Found a security issue? Please report it privately, see [SECURITY.md](SECURITY.md)

Every pull request is automatically tested on macOS, Windows and Linux.

<details>
<summary><b>For developers: files, tests and settings</b></summary>

| Path | What it is |
|---|---|
| `index.html` | The whole web app (no build step) |
| `server.py` | Local server: serves the app, runs Kokoro and fetches web links (listens on `127.0.0.1` only) |
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

**Install with git or the Terminal instead**

```bash
git clone https://github.com/henkholalh/Read-it-for-me-RIFM.git
cd Read-it-for-me-RIFM
./setup.sh     # one time (Windows: setup.bat)
./start.sh     # every time (Windows: start.bat)
```

**Command-line reader (Mac only)**

```bash
./speak.py document.pdf -v Samantha        # read a file aloud
./speak.py --voices en                     # list English voices
./speak.py document.pdf -o out.m4a         # save as an audio file
```
</details>

---

## 🗺 Roadmap

Ideas we'd love help with. Pick one, open an issue to say you're on it, and go!

**Reading**
- [x] Read a web page from its link, and logged-in pages with a bookmark
- [x] Start from a chosen page
- [ ] Remember where you stopped in each file
- [ ] OCR for scanned PDFs (pictures of pages)
- [ ] Read PDF columns and tables in the right order
- [ ] More file types: EPUB e-books, PowerPoint (.pptx), RTF

**Listening**
- [ ] Export the whole document as an MP3 or WAV audiobook
- [ ] Skip forward/back by sentence or paragraph
- [ ] A pronunciation dictionary for names and abbreviations
- [ ] More free local voices and accents

**App**
- [ ] Installable app (PWA) and a menu-bar / system-tray launcher
- [ ] Translations of the app's interface
- [ ] Larger text / dyslexia-friendly reading mode and focus mode
- [ ] Faster Kokoro on Apple Silicon and NVIDIA GPUs

---

## 🙏 Credits

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) voice model (Apache-2.0), run with [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)
- [pdf.js](https://github.com/mozilla/pdf.js) (Apache-2.0) and [mammoth.js](https://github.com/mwilliamson/mammoth.js) (BSD-2-Clause)

## 📜 License

Read it For Me is released under the [MIT License](LICENSE): you're free to use, copy, modify and share it.
The voice model and bundled libraries listed above keep their own licenses.
