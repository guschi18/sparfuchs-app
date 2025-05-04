"""
Allgemeine Hilfsfunktionen für die SparFuchs.de Anwendung.

Dieses Modul enthält allgemeine Funktionen, die in verschiedenen Teilen
der Anwendung verwendet werden können.
"""
import time
import random
from pathlib import Path
import shutil
import os

def initialize_session_state(session_state):
    """
    Initialisiert den Streamlit-Sitzungsstatus mit Standardwerten.
    
    Args:
        session_state: Das Streamlit-Sitzungsobjekt
    """
    # Session State für Chatverlauf initialisieren
    if "messages" not in session_state:
        # Systemnachricht, die im Hintergrund verwendet wird
        session_state.messages = [
            {"role": "system", "content": "Du bist ein hilfreicher Einkaufsassistent für SparFuchs.de. " +
            "Benutze AUSSCHLIESSLICH die dir bereitgestellten Produktinformationen, um Anfragen zu beantworten. " +
            "EXTREM WICHTIG: Du darfst NUR Produkte erwähnen, die in den bereitgestellten Daten vorhanden sind. " +
            "ERFINDE NIEMALS Produkte oder Angebote. Wenn du ein Produkt nicht in den Daten findest, sage klar, " +
            "dass du keine Information darüber hast. " +
            "WICHTIG: Antworte IMMER auf Deutsch, unabhängig von der Sprache der Anfrage. " +
            "Wenn du nach Produkten gefragt wirst, die nicht in der Datenbank sind, sage deutlich, " +
            "dass du keine Informationen zu diesen Produkten hast. " +
            "WICHTIG: Verweise NIEMALS auf Angebotsbroschüren oder externe Quellen. " +
            "Antworte ausschließlich mit den Daten, die dir zur Verfügung gestellt werden. " + 
            "WICHTIG: Antworte erst, wenn du alle Informationen analysiert hast, um eine korrekte Antwort zu geben. " +
            "FORMATIERUNGSANWEISUNG: Formatiere deine Antworten zu Produkten immer mit dem HTML <br> Tag für Zeilenumbrüche."}
        ]

    # Initialisiere eine Key-Zähler-Variable für eindeutige Streamlit-Widget-Keys
    if "key_counter" not in session_state:
        session_state["key_counter"] = 0

    # Initialisiere previous_input für die Verfolgung von Benutzereingaben
    if "previous_input" not in session_state:
        session_state["previous_input"] = ""
        
    # Initialisiere eine Variable, die anzeigt, ob es die erste Eingabe ist
    if "is_first_input" not in session_state:
        session_state["is_first_input"] = True

    # Initialisiere einen direkten Übermittlungsflag für Vorschläge
    if "submit_text" not in session_state:
        session_state["submit_text"] = None

def add_simulated_delay(min_time=0.8, max_time=1.2):
    """
    Fügt eine simulierte Verzögerung hinzu, um menschlicheres Verhalten nachzuahmen.
    
    Args:
        min_time (float): Minimale Verzögerungszeit in Sekunden
        max_time (float): Maximale Verzögerungszeit in Sekunden
    """
    delay = random.uniform(min_time, max_time)
    time.sleep(delay)

def ensure_directories():
    """
    Stellt sicher, dass alle notwendigen Verzeichnisse vorhanden sind.
    
    Die Funktion erstellt die benötigten Verzeichnisse, falls sie noch nicht existieren.
    """
    # Liste der erforderlichen Verzeichnisse
    required_dirs = [
        Path("data"),
        Path("static")
    ]
    
    # Stelle sicher, dass alle Verzeichnisse existieren
    for directory in required_dirs:
        directory.mkdir(exist_ok=True)
    
    # Rufe die Funktion auf, um sicherzustellen, dass eine .env-Datei mit UTF-8-Kodierung existiert
    ensure_env_file_exists()

def copy_csv_if_missing():
    """
    Kopiert die CSV-Datei in das data-Verzeichnis, falls sie dort nicht vorhanden ist.
    
    Diese Funktion stellt sicher, dass die Angebotsdatei im korrekten Verzeichnis liegt.
    """
    source_path = Path("Angebote.csv")
    target_path = Path("data/Angebote.csv")
    
    if source_path.exists() and not target_path.exists():
        # Stelle sicher, dass das Zielverzeichnis existiert
        target_path.parent.mkdir(exist_ok=True)
        
        # Kopiere die Datei
        shutil.copy2(source_path, target_path)

def ensure_env_file_exists():
    """
    Stellt sicher, dass eine .env-Datei mit korrekter UTF-8-Kodierung existiert.
    
    Die Funktion überprüft, ob eine .env-Datei existiert und erstellt eine neue mit 
    UTF-8-Kodierung, falls sie nicht vorhanden ist oder möglicherweise eine falsche 
    Kodierung hat.
    """
    env_path = Path(".env")
    
    # Erstelle eine neue .env-Datei mit UTF-8-Kodierung, wenn sie nicht existiert
    if not env_path.exists():
        try:
            with open(env_path, "w", encoding="utf-8") as env_file:
                env_file.write("# SparFuchs.de Umgebungsvariablen\n\n")
                env_file.write("# API-Schlüssel für OpenRouter\n")
                env_file.write("OPENAI_API_KEY=\n\n")
                env_file.write("# Debug-Modus (aktiviert ausführliche Fehlermeldungen)\n")
                env_file.write("DEBUG=True\n")
        except Exception:
            pass
            
    # Überprüfe die Kodierung der vorhandenen .env-Datei
    else:
        try:
            # Versuche, die Datei mit UTF-8 zu lesen
            with open(env_path, "r", encoding="utf-8") as test_file:
                test_file.read()
        except UnicodeDecodeError:
            # Bei Kodierungsfehlern erstelle eine neue Datei mit UTF-8-Kodierung
            try:
                # Versuche, mit alternativen Kodierungen zu lesen
                content = None
                for encoding in ["utf-16", "latin-1", "cp1252"]:
                    try:
                        with open(env_path, "r", encoding=encoding) as file:
                            content = file.read()
                            break
                    except UnicodeDecodeError:
                        continue
                
                # Wenn Inhalt gelesen werden konnte, schreibe ihn in UTF-8 neu
                if content:
                    with open(env_path, "w", encoding="utf-8") as file:
                        file.write(content)
                else:
                    # Wenn keine Kodierung funktioniert hat, erstelle eine neue Datei
                    with open(env_path, "w", encoding="utf-8") as env_file:
                        env_file.write("# SparFuchs.de Umgebungsvariablen\n\n")
                        env_file.write("# API-Schlüssel für OpenRouter\n")
                        env_file.write("OPENAI_API_KEY=\n\n")
                        env_file.write("# Debug-Modus (aktiviert ausführliche Fehlermeldungen)\n")
                        env_file.write("DEBUG=True\n")
            except Exception:
                pass 