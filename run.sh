#!/bin/bash

# Aktiviere venv und starte den Mail Notifier

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Überprüfe ob venv existiert
if [ ! -d "venv" ]; then
    echo "❌ Virtual Environment nicht gefunden!"
    echo "Bitte führe zuerst aus: python3 -m venv venv --without-pip"
    exit 1
fi

# Überprüfe ob .env existiert
if [ ! -f ".env" ]; then
    echo "❌ .env Datei nicht gefunden!"
    echo "Erstelle .env mit: cp .env.example .env"
    echo "Dann trage deine Login-Daten ein."
    exit 1
fi

# Wähle Version basierend auf Parameter
if [ "$1" = "--stable" ]; then
    echo "🚀 Starte stabile Version..."
    source venv/bin/activate
    python mail_notifier_stable.py
else
    echo "📧 Starte Standard-Version..."
    echo "Tipp: Nutze './run.sh --stable' für die stabilere Version"
    source venv/bin/activate
    python mail_notifier_config.py
fi