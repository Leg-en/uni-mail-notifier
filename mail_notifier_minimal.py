#!/usr/bin/env python3
import imaplib
import getpass
import time
import subprocess
import sys

def check_unread_emails(username, password):
    try:
        mail = imaplib.IMAP4_SSL('imap.uni-muenster.de', 993)
        mail.login(username, password)
        mail.select('INBOX', readonly=True)
        
        status, response = mail.search(None, 'UNSEEN')
        unread_ids = response[0].split()
        
        mail.logout()
        return len(unread_ids)
    except Exception as e:
        print(f"Fehler beim E-Mail-Abruf: {e}")
        return -1

def play_notification():
    # Verschiedene Methoden für Ton-Benachrichtigung
    if sys.platform == "linux":
        try:
            subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/message.oga'], check=False)
        except:
            try:
                subprocess.run(['aplay', '-q', '/usr/share/sounds/sound-icons/percussion-10.wav'], check=False)
            except:
                print('\a')  # Terminal bell
    elif sys.platform == "darwin":  # macOS
        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=False)
    else:  # Windows
        import winsound
        winsound.MessageBeep()

def main():
    print("Uni Münster E-Mail Notifier (Minimal)")
    print("-" * 38)
    
    username = input("Uni-Benutzername: ")
    password = getpass.getpass("Passwort: ")
    
    print("\nÜberwache E-Mails... (Strg+C zum Beenden)")
    
    last_count = 0
    first_run = True
    
    while True:
        current_count = check_unread_emails(username, password)
        
        if current_count == -1:
            print("Verbindungsfehler. Neuer Versuch in 5 Minuten...")
            time.sleep(300)
            continue
        
        if not first_run and current_count > last_count:
            new_emails = current_count - last_count
            print(f"\n🔔 {new_emails} neue E-Mail(s)! (Gesamt ungelesen: {current_count})")
            play_notification()
        else:
            print(f"Ungelesene E-Mails: {current_count}", end='\r')
        
        last_count = current_count
        first_run = False
        
        time.sleep(60)  # Überprüfung alle 60 Sekunden

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgramm beendet.")