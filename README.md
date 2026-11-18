<div align="center">

# Email-Check

**Local IMAP Gmail reader with Gemini-powered categorization and summarization.**

[![CI](https://github.com/doducanhkhoi-ops/Email-Check/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/doducanhkhoi-ops/Email-Check/actions/workflows/ci.yml)
[![Security Audit](https://github.com/doducanhkhoi-ops/Email-Check/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/doducanhkhoi-ops/Email-Check/actions/workflows/security.yml)
[![CodeQL](https://github.com/doducanhkhoi-ops/Email-Check/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/doducanhkhoi-ops/Email-Check/actions/workflows/codeql.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/doducanhkhoi-ops/Email-Check)](./LICENSE)

</div>

---

Fetches recent Gmail messages over `imap.gmail.com` (SSL), groups them into categories via `google-genai` (`gemini-3.5-flash-lite`), and summarizes individual threads in a local Flask UI.

---

## Feature Overview

| Component | Behavior |
| --- | --- |
| **IMAP Client** (`app.py`) | Connects via `IMAP4_SSL`, fetches up to 50 recent messages by date window |
| **MIME Decoder** | Decodes UTF-8 headers and extracts plain-text / HTML bodies |
| **Classifier** (`POST /api/emails`) | Categorizes fetched messages into structured JSON groups |
| **Summarizer** (`POST /api/summarize`) | Generates concise bullet-point summaries with HTML preview |
| **Multi-account Config** | Reads `accounts.json` with fallback to `GMAIL_USER` / `GMAIL_APP_PASSWORD` |

---

## Quick Start

### 1. Install

```bash
git clone https://github.com/doducanhkhoi-ops/Email-Check.git
cd Email-Check
pip install -r requirements.txt
```

### 2. Configure credentials

Copy `accounts.example.json` to `accounts.json` (or set `GMAIL_USER` and `GMAIL_APP_PASSWORD` in your environment) and export `GEMINI_API_KEY`:

```bash
cp accounts.example.json accounts.json
export GEMINI_API_KEY="your_gemini_api_key"
```

### 3. Run

```bash
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

---

## Testing & Security

```bash
python -m unittest discover -s tests -v
```

| Check | Tool | Scope |
| --- | --- | --- |
| **Unit & Route Tests** | `pytest` (`3.10`, `3.11`, `3.12`) | MIME decoding, multipart body parsing, credential fallback, Flask routes |
| **SAST** | GitHub CodeQL | Static vulnerability analysis on Python source |
| **Security & CVE Audit** | `bandit` + `ruff` + `pip-audit` | Exception hygiene, Flask debug defaults, dependency CVEs |

---

## License

[Apache License 2.0](./LICENSE)
