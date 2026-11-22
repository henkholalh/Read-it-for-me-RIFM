# Contributing to Read it For Me (RIFM)

Thanks for wanting to help! RIFM is a community project, and every contribution counts: bug reports, ideas, documentation, translations, testing on your laptop, and code.

By taking part you agree to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help (no coding needed)

- **Report a bug:** [open a bug report](https://github.com/henkholalh/Read-it-for-me-RIFM/issues/new?template=bug_report.yml). Tell us your OS, browser and voice option.
- **Suggest an idea:** [open a feature request](https://github.com/henkholalh/Read-it-for-me-RIFM/issues/new?template=feature_request.yml).
- **Test on your machine:** especially Windows, Linux and older Macs. Tell us what worked and what didn't.
- **Improve the docs:** if something in the README confused you, it will confuse others too. Fix it!
- **Share sample files** (with nothing private in them) that RIFM reads badly, such as unusual PDFs, tables or columns.

## Your first code contribution

1. Look for issues labelled [`good first issue`](https://github.com/henkholalh/Read-it-for-me-RIFM/labels/good%20first%20issue) or [`help wanted`](https://github.com/henkholalh/Read-it-for-me-RIFM/labels/help%20wanted), or pick something from the [Roadmap](README.md#-roadmap).
2. Comment on the issue to say you're working on it, so nobody duplicates the work.
3. Fork the repository, create a branch, make your change and open a pull request.

Never contributed to open source before? GitHub's guide [Contributing to a project](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) walks you through forks and pull requests.

## Development setup

You need **Python 3.10–3.13**, **git**, and, for the text tests, **Node.js 18+**.

```bash
git clone https://github.com/<your-username>/Read-it-for-me-RIFM.git
cd Read-it-for-me-RIFM
./setup.sh                 # Windows: setup.bat
./start.sh                 # Windows: start.bat   → http://127.0.0.1:8787
```

There is **no build step**. Edit `index.html` and reload the browser. If you change `server.py`, restart the server (<kbd>Ctrl</kbd>+<kbd>C</kbd>, then start it again).

### How the project fits together

```
Browser (index.html)
 ├─ reads files: pdf.js (PDF), mammoth.js (Word), plain text, Markdown, HTML
 ├─ splits text into sentences and adds pauses
 ├─ voices:
 │   ├─ Built-in → the browser's Web Speech API (exact word highlighting)
 │   ├─ Kokoro   → POST /api/kokoro on the local server → WAV audio
 │   └─ OpenAI   → OpenAI speech API, straight from the browser (user's own key)
 └─ highlights the current sentence and word, prepares upcoming sentences ahead of time

server.py (Python, 127.0.0.1 only)
 ├─ serves index.html and vendor/*.js (an allowlist, nothing else)
 └─ runs Kokoro, one sentence at a time, most urgent first; skips requests the page no longer needs
```

### Tests

Please run these before opening a pull request. They also run automatically on macOS, Windows and Linux for every pull request.

```bash
node tests/test_text.mjs                          # sentence splitting, PDF line joining, punctuation
.venv/bin/python -m unittest discover tests -v    # server (Windows: .venv\Scripts\python.exe -m unittest discover tests -v)
.venv/bin/python -m pip install ruff==0.8.6 && .venv/bin/ruff check .   # code style
```

If you add a feature, please add a test for it where it makes sense:
- `tests/test_text.mjs` for text processing in `index.html`
- `tests/test_server.py` for the server

### Try it by hand

The automatic tests can't listen to the audio, so please also check your change in a browser:
- Upload a PDF and a Word file. Try **Kokoro** and **Built-in** voices.
- Try **Pause**, **Stop**, clicking a sentence, and switching files while it's reading.
- If you can, check both a Mac and a Windows machine, or say in the pull request which one you couldn't test.

## Guidelines

- **Keep it simple to run.** Users double-click a file to start RIFM, so please avoid adding build tools, frameworks or system dependencies. A new Python package is fine if it installs cleanly on macOS, Windows and Linux.
- **Privacy first.** Kokoro and Built-in voices must keep working fully offline. Never send document text anywhere except to a service the user has explicitly chosen (such as OpenAI with their own key).
- **Accessibility matters.** Many people who use a read-aloud tool rely on it. Keep keyboard shortcuts working, keep good contrast in light and dark mode, and use clear wording.
- **Code style:** Python follows `ruff` (settings in `pyproject.toml`). For JavaScript, match the style of `index.html`: plain modern JS, no frameworks.
- **Small pull requests** are easier to review. One topic per pull request.
- **Commit messages:** a short summary line ("Fix PDF columns being read out of order"), then details if needed.
- **Changelog:** add a line under *Unreleased* in [CHANGELOG.md](CHANGELOG.md) for anything users will notice.

## Reporting security issues

Please don't open a public issue. See [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
