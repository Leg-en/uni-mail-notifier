#!/usr/bin/env python3
import imaplib
import time
import os
import sys
import subprocess
from config import Config
from datetime import datetime

def check_unread_emails():
    try:
        if Config.DEBUG:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Verbinde zu {Config.IMAP_SERVER}:{Config.IMAP_PORT}")
        
        mail = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
        mail.login(Config.USERNAME, Config.PASSWORD)
        mail.select('INBOX', readonly=True)
        
        status, response = mail.search(None, 'UNSEEN')
        unread_ids = response[0].split()
        
        subjects = []
        if Config.SHOW_SUBJECT_PREVIEW and unread_ids:
            for email_id in unread_ids[-3:]:  # Letzte 3 E-Mails
                status, msg_data = mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')
                if status == 'OK':
                    subject = msg_data[0][1].decode('utf-8', errors='ignore')
                    subject = subject.replace('Subject: ', '').strip()
                    if subject:
                        subjects.append(subject)
        
        mail.logout()
        return len(unread_ids), subjects
    except Exception as e:
        if Config.DEBUG:
            print(f"\nFehler beim E-Mail-Abruf: {e}")
        return -1, []

def play_notification():
    if not Config.SOUND_ENABLED:
        return
    
    if Config.CUSTOM_SOUND_PATH and os.path.exists(Config.CUSTOM_SOUND_PATH):
        sound_file = Config.CUSTOM_SOUND_PATH
    else:
        sound_file = None
    
    if sys.platform == "linux":
        if sound_file:
            subprocess.run(['paplay', '--volume', str(int(Config.NOTIFICATION_VOLUME * 65536)), sound_file], 
                         capture_output=True, check=False)
        else:
            try:
                subprocess.run(['paplay', '--volume', str(int(Config.NOTIFICATION_VOLUME * 65536)), 
                              '/usr/share/sounds/freedesktop/stereo/message.oga'], 
                              capture_output=True, check=False)
            except:
                print('\a')
    elif sys.platform == "darwin":  # macOS
        if sound_file:
            subprocess.run(['afplay', '-v', str(Config.NOTIFICATION_VOLUME), sound_file], check=False)
        else:
            subprocess.run(['afplay', '-v', str(Config.NOTIFICATION_VOLUME), 
                          '/System/Library/Sounds/Glass.aiff'], check=False)
    else:  # Windows
        try:
            import winsound
            winsound.MessageBeep()
        except:
            print('\a')

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
    except:
        pass

def main():
    print("Uni Münster E-Mail Notifier (Konfigurierbar)")
    print("=" * 45)
    
    if not Config.USERNAME or not Config.PASSWORD:
        print("\n❌ Fehler: Bitte UNI_USERNAME und UNI_PASSWORD in .env Datei setzen!")
        print("\nBeispiel .env Datei:")
        print("UNI_USERNAME=dein_benutzername")
        print("UNI_PASSWORD=dein_passwort")
        return
    
    print(f"\n✓ Angemeldet als: {Config.USERNAME}")
    print(f"✓ Server: {Config.IMAP_SERVER}:{Config.IMAP_PORT}")
    print(f"✓ Check-Intervall: {Config.CHECK_INTERVAL} Sekunden")
    print(f"✓ Sound: {'Aktiviert' if Config.SOUND_ENABLED else 'Deaktiviert'}")
    if Config.CUSTOM_SOUND_PATH:
        print(f"✓ Custom Sound: {Config.CUSTOM_SOUND_PATH}")
    print(f"✓ Desktop-Benachrichtigung: {'Aktiviert' if Config.SHOW_NOTIFICATION_POPUP else 'Deaktiviert'}")
    
    print("\nÜberwache E-Mails... (Strg+C zum Beenden)")
    
    last_count = 0
    first_run = True
    
    while True:
        current_count, subjects = check_unread_emails()
        
        if current_count == -1:
            print(f"\n⚠️  Verbindungsfehler. Neuer Versuch in {Config.RETRY_INTERVAL} Sekunden...")
            time.sleep(Config.RETRY_INTERVAL)
            continue
        
        if not first_run and current_count > last_count:
            new_emails = current_count - last_count
            message = f"{new_emails} neue E-Mail{'s' if new_emails > 1 else ''}!"
            
            print(f"\n🔔 {message} (Gesamt ungelesen: {current_count})")
            
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
        
        time.sleep(Config.CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Programm beendet.")