# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based email notification system for University of Münster (Uni Münster) IMAP email accounts. It monitors for new emails and provides sound/desktop notifications.

## Development Commands

### Setup and Run
```bash
# Initial setup
cp .env.example .env  # Then edit with your credentials
python3 -m venv venv --without-pip
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && venv/bin/python get-pip.py && rm get-pip.py
venv/bin/pip install -r requirements.txt

# Run the notifier
./run.sh           # Standard configurable version
./run.sh --stable  # Stable version with enhanced error handling

# Or manually
source venv/bin/activate
python mail_notifier_config.py  # or mail_notifier_stable.py
```

### Git Operations
```bash
# The repository is already initialized and connected to GitHub
git add -A
git commit -m "Your message"
git push
```

## Architecture

The project has four Python script versions with progressive complexity:

1. **mail_notifier.py** - Basic hardcoded version
2. **mail_notifier_minimal.py** - Cross-platform without external sound dependencies  
3. **mail_notifier_config.py** - Full-featured with environment configuration
4. **mail_notifier_stable.py** - Production-ready with connection pooling and advanced error handling

All configurable versions read settings from `.env` via `config.py`. The stable version includes:
- Connection keep-alive with NOOP commands
- Exponential backoff for retries
- Socket timeout management
- Comprehensive logging

## Key Configuration Options

From `.env.example`:
- `CHECK_INTERVAL`: Seconds between checks (recommend 180+ to avoid rate limiting)
- `RETRY_INTERVAL`: Base retry interval on errors
- `SOUND_ENABLED`: Toggle sound notifications
- `SHOW_NOTIFICATION_POPUP`: Enable desktop notifications (requires plyer)
- `SHOW_SUBJECT_PREVIEW`: Show email subjects in notifications
- `DEBUG`: Enable debug logging (stable version)

## Important Notes

- CHECK_INTERVAL below 120 seconds can cause connection issues due to server rate limiting
- The IMAP connection is read-only for safety
- Credentials must be stored in `.env` (never commit this file)
- The stable version is recommended for long-running use