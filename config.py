import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # IMAP Einstellungen
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.uni-muenster.de')
    IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))
    
    # Login-Daten
    USERNAME = os.getenv('UNI_USERNAME', '')
    PASSWORD = os.getenv('UNI_PASSWORD', '')
    
    # Überwachungseinstellungen
    CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '60'))  # Sekunden
    RETRY_INTERVAL = int(os.getenv('RETRY_INTERVAL', '300'))  # 5 Minuten bei Fehler
    
    # Benachrichtigungseinstellungen
    SOUND_ENABLED = os.getenv('SOUND_ENABLED', 'true').lower() == 'true'
    CUSTOM_SOUND_PATH = os.getenv('CUSTOM_SOUND_PATH', '')
    NOTIFICATION_VOLUME = float(os.getenv('NOTIFICATION_VOLUME', '1.0'))
    
    # Anzeigeeinstellungen
    SHOW_NOTIFICATION_POPUP = os.getenv('SHOW_NOTIFICATION_POPUP', 'false').lower() == 'true'
    SHOW_SUBJECT_PREVIEW = os.getenv('SHOW_SUBJECT_PREVIEW', 'false').lower() == 'true'
    
    # Debug
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'