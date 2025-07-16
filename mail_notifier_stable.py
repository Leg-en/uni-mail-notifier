#!/usr/bin/env python3
import imaplib
import time
import os
import sys
import subprocess
import socket
import logging
from config import Config
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class MailChecker:
    def __init__(self):
        self.mail = None
        self.last_check = datetime.now()
        self.connection_retries = 0
        self.max_retries = 3
        
    def connect(self):
        """Erstellt eine neue IMAP-Verbindung mit Timeout"""
        try:
            # Setze Socket-Timeout für bessere Kontrolle
            socket.setdefaulttimeout(30)
            
            logger.debug(f"Verbinde zu {Config.IMAP_SERVER}:{Config.IMAP_PORT}")
            self.mail = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
            self.mail.login(Config.USERNAME, Config.PASSWORD)
            self.mail.select('INBOX', readonly=True)
            
            self.connection_retries = 0
            logger.debug("Verbindung erfolgreich hergestellt")
            return True
            
        except socket.timeout:
            logger.error("Verbindungs-Timeout nach 30 Sekunden")
            return False
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP-Fehler: {e}")
            return False
        except Exception as e:
            logger.error(f"Verbindungsfehler: {e}")
            return False
    
    def disconnect(self):
        """Trennt die IMAP-Verbindung sauber"""
        if self.mail:
            try:
                self.mail.close()
                self.mail.logout()
            except:
                pass
            self.mail = None
    
    def check_emails(self):
        """Prüft auf neue E-Mails mit robuster Fehlerbehandlung"""
        try:
            # Verbindung prüfen mit NOOP (Keep-Alive)
            if self.mail:
                try:
                    self.mail.noop()
                except:
                    logger.debug("Verbindung verloren, erstelle neue...")
                    self.disconnect()
                    
            # Neue Verbindung falls nötig
            if not self.mail:
                if not self.connect():
                    return -1, []
            
            # E-Mails abrufen
            status, response = self.mail.search(None, 'UNSEEN')
            if status != 'OK':
                logger.error(f"Suche fehlgeschlagen: {status}")
                return -1, []
                
            unread_ids = response[0].split()
            
            # Betreff-Vorschau
            subjects = []
            if Config.SHOW_SUBJECT_PREVIEW and unread_ids:
                for email_id in unread_ids[-3:]:
                    try:
                        status, msg_data = self.mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')
                        if status == 'OK' and msg_data[0]:
                            subject = msg_data[0][1].decode('utf-8', errors='ignore')
                            subject = subject.replace('Subject: ', '').strip()
                            if subject:
                                subjects.append(subject)
                    except:
                        pass
            
            return len(unread_ids), subjects
            
        except Exception as e:
            logger.error(f"Fehler beim E-Mail-Check: {e}")
            self.disconnect()
            return -1, []

def play_notification():
    if not Config.SOUND_ENABLED:
        return
    
    try:
        if Config.CUSTOM_SOUND_PATH and os.path.exists(Config.CUSTOM_SOUND_PATH):
            sound_file = Config.CUSTOM_SOUND_PATH
        else:
            sound_file = None
        
        if sys.platform == "linux":
            if sound_file:
                subprocess.run(['paplay', '--volume', str(int(Config.NOTIFICATION_VOLUME * 65536)), sound_file], 
                             capture_output=True, check=False, timeout=5)
            else:
                subprocess.run(['paplay', '--volume', str(int(Config.NOTIFICATION_VOLUME * 65536)), 
                              '/usr/share/sounds/freedesktop/stereo/message.oga'], 
                              capture_output=True, check=False, timeout=5)
        elif sys.platform == "darwin":  # macOS
            if sound_file:
                subprocess.run(['afplay', '-v', str(Config.NOTIFICATION_VOLUME), sound_file], 
                              check=False, timeout=5)
            else:
                subprocess.run(['afplay', '-v', str(Config.NOTIFICATION_VOLUME), 
                              '/System/Library/Sounds/Glass.aiff'], check=False, timeout=5)
        else:  # Windows
            import winsound
            winsound.MessageBeep()
    except subprocess.TimeoutExpired:
        logger.warning("Sound-Wiedergabe Timeout")
    except Exception as e:
        logger.debug(f"Sound-Fehler: {e}")
        print('\a')  # Fallback

def show_desktop_notification(title, message):
    if not Config.SHOW_NOTIFICATION_POPUP:
        return
    
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            timeout=10
        )
    except Exception as e:
        logger.debug(f"Desktop-Benachrichtigung fehlgeschlagen: {e}")

def main():
    print("Uni Münster E-Mail Notifier (Stabil)")
    print("=" * 38)
    
    if not Config.USERNAME or not Config.PASSWORD:
        print("\n❌ Fehler: Bitte UNI_USERNAME und UNI_PASSWORD in .env Datei setzen!")
        return
    
    print(f"\n✓ Angemeldet als: {Config.USERNAME}")
    print(f"✓ Server: {Config.IMAP_SERVER}:{Config.IMAP_PORT}")
    print(f"✓ Check-Intervall: {Config.CHECK_INTERVAL} Sekunden")
    print(f"✓ Sound: {'Aktiviert' if Config.SOUND_ENABLED else 'Deaktiviert'}")
    print(f"✓ Debug: {'Aktiviert' if Config.DEBUG else 'Deaktiviert'}")
    
    # Empfehlung bei zu niedrigem Intervall
    if Config.CHECK_INTERVAL < 120:
        print("\n⚠️  Hinweis: Check-Intervall unter 2 Minuten kann zu Verbindungsproblemen führen!")
        print("   Empfohlen: CHECK_INTERVAL=180 (3 Minuten) oder höher")
    
    print("\nÜberwache E-Mails... (Strg+C zum Beenden)")
    
    checker = MailChecker()
    last_count = 0
    first_run = True
    consecutive_errors = 0
    
    while True:
        try:
            current_count, subjects = checker.check_emails()
            
            if current_count == -1:
                consecutive_errors += 1
                
                # Exponentielles Backoff bei wiederholten Fehlern
                retry_wait = min(Config.RETRY_INTERVAL * (2 ** (consecutive_errors - 1)), 3600)
                
                print(f"\n⚠️  Verbindungsfehler #{consecutive_errors}. Neuer Versuch in {retry_wait} Sekunden...")
                logger.error(f"Fehler #{consecutive_errors}, warte {retry_wait}s")
                
                time.sleep(retry_wait)
                continue
            
            # Erfolgreich - Reset error counter
            consecutive_errors = 0
            
            if not first_run and current_count > last_count:
                new_emails = current_count - last_count
                message = f"{new_emails} neue E-Mail{'s' if new_emails > 1 else ''}!"
                
                print(f"\n🔔 {message} (Gesamt ungelesen: {current_count})")
                logger.info(message)
                
                if Config.SHOW_SUBJECT_PREVIEW and subjects:
                    print("   Neueste Betreff-Zeilen:")
                    for subject in subjects[-new_emails:]:
                        print(f"   • {subject[:60]}{'...' if len(subject) > 60 else ''}")
                
                play_notification()
                show_desktop_notification("Neue E-Mail", message)
            else:
                status_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Ungelesene E-Mails: {current_count}"
                print(f"\r{status_msg}", end='', flush=True)
            
            last_count = current_count
            first_run = False
            
            # Warte bis zum nächsten Check
            time.sleep(Config.CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Unerwarteter Fehler in Hauptschleife: {e}")
            time.sleep(30)
    
    # Cleanup
    checker.disconnect()
    print("\n\n✓ Programm beendet.")

if __name__ == "__main__":
    main()