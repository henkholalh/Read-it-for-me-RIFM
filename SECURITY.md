# Security Policy

## Reporting a vulnerability

Please **do not** report security problems in public issues.

Report them privately through GitHub instead: go to the repository's **Security** tab and click **Report a vulnerability**, or use [this link](https://github.com/henkholalh/Read-it-for-me-RIFM/security/advisories/new).

Please include:
- what the problem is and what an attacker could do with it
- steps to reproduce it
- your OS, browser and RIFM version (or commit)

We aim to reply within 7 days and will keep you updated while we work on a fix. We're happy to credit you when the fix is released, unless you'd rather stay anonymous.

## Supported versions

Security fixes go into the latest version on the `main` branch. Please update to it before reporting.

## How RIFM protects you

- **Local only:** the RIFM server listens on `127.0.0.1`, so other computers on your network can't reach it.
- **Nothing else is shared:** the server only serves the app's own files (an allowlist). Your documents, models and other files are never served.
- **Your documents stay on your computer** with the Kokoro and Built-in voices. Text is sent only to OpenAI, and only if you choose the OpenAI voice and enter your own key.
- **API keys** are stored only in your browser's local storage on your own computer. They are never sent to RIFM's server.
- **Downloads are verified:** the voice model is checked against a SHA-256 checksum after download.
