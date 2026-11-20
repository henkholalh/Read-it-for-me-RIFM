# Changelog

All notable changes to Read it For Me (RIFM) are listed here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-11-20

First public release.

### Added
- Upload PDF, Word (.docx), .txt, .md, .html, .csv and .json files: browse, drag and drop, or several at once
- Three voice options:
  - **Kokoro:** free, natural AI voice running on your own computer (54 voices, 9 languages)
  - **Built-in:** the system voices of macOS / Windows
  - **OpenAI:** expressive voices and accents (such as an Alabama Southern drawl), with the user's own API key
- "Now speaking" bar with sentence and word highlighting and a progress bar
- Natural pacing: pauses at headings, bullets and paragraphs, and PDF line wraps joined back into sentences
- Play, pause, stop, click a sentence to jump there, speed and pitch, and keyboard shortcuts
- Local server with ordered sentence preparation, cancellation of outdated requests, and a strict file allowlist
- One-click setup and launchers for macOS (`Read it For Me.command`) and Windows (`Read it For Me.bat`)
- Checksum-verified, retrying model download
- Command-line reader `speak.py` (macOS)
- Automated tests and CI on macOS, Windows and Linux

[Unreleased]: https://github.com/henkholalh/Read-it-for-me-RIFM/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/henkholalh/Read-it-for-me-RIFM/releases/tag/v1.0.0
