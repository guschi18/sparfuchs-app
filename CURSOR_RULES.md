# Cursor Rules for SparFuchs.de

Du bist ein KI-Assistent, der bei der Entwicklung der Python-Webanwendung "SparFuchs.de" hilft.
Die Anwendung nutzt Streamlit für das Frontend (Chat-Interface) und interagiert mit einer KI (via OpenRouter), um Nutzern aktuelle Supermarkt-Angebote basierend auf natürlichsprachlichen Anfragen zu liefern.

## Kerntechnologien & Stack

- **Sprache:** Python 3.x
- **Web Framework / UI:** Streamlit
- **KI-Backend:** OpenAI-Modelle über OpenRouter API (API-Key in `.env` Datei)
- **Datenquelle:** CSV-Datei (`data/Angebote.csv`)
- **Datenverarbeitung:** Vermutlich Pandas (Standard für CSV in Python, siehe `src/data/product_data.py`)
- **Styling:** CSS (`static/styles.dev.css`, `static/styles.min.css`), geladen/verwaltet über `src/ui/styling.py`.
- **Abhängigkeiten:** Verwaltet in `requirements.txt`.

## Projektstruktur & Wichtige Module

Beachte die folgende Struktur und die Verantwortlichkeiten der Module:

- **`app.py`**: Haupt-Einstiegspunkt der Streamlit-Anwendung. Orchestriert UI und Logik.
- **`src/`**: Kernlogik der Anwendung.
  - **`ui/`**: Verantwortlich für UI-Komponenten (`layout.py`) und Styling (`styling.py`). Nutzt Streamlit-Elemente.
  - **`data/`**: Lädt und verarbeitet Produktdaten aus der CSV (`product_data.py`).
  - **`ai/`**: Beinhaltet die gesamte KI-Logik:
    - `client.py`: Kommunikation mit der OpenRouter API.
    - `context.py`: Erstellt den Kontext/Prompt für die KI basierend auf Nutzereingaben und Produktdaten.
    - `hallucination.py`: Logik zur Erkennung von KI-Halluzinationen.
  - **`utils/`**: Allgemeine Hilfsfunktionen (`helpers.py`).
- **`data/`**: Speicherort für Datendateien, primär `Angebote.csv`.
- **`static/`**: Statische Dateien wie CSS.
- **`.env`**: Speichert Umgebungsvariablen (z.B. `OPENAI_API_KEY`). **Wichtig:** Darf nicht versioniert werden.

## Kernkonzepte & Domain

- **Fokus:** Aktuelle Angebote von Aldi und Lidl.
- **Interaktion:** Über ein Chat-Interface (Streamlit).
- **Suche:** Semantische, natürlichsprachliche Produktsuche.
- **Daten:** Produktinformationen und Preise aus der CSV.
- **KI-Zuverlässigkeit:** Halluzinationserkennung ist ein wichtiger Aspekt (`src/ai/hallucination.py`).

## Coding Style & Konventionen

- Folge standardmäßigen Python Best Practices (PEP 8).
- Schreibe klaren, lesbaren und gut kommentierten Code, insbesondere in den `ai/` und `data/` Modulen.
- Nutze Type Hints zur Verbesserung der Codequalität und Verständlichkeit.
- Halte Streamlit-Komponenten in `src/ui/` modular.
- Achte auf sauberes Fehlerhandling, besonders bei API-Aufrufen (`ai/client.py`) und Datenzugriffen (`data/product_data.py`).

## Anweisungen für die KI-Assistenz

- **Kontext verstehen:** Beziehe dich bei Code-Analysen oder Änderungen immer auf die oben beschriebene Projektstruktur und die Zuständigkeiten der Module.
- **Fehlersuche:**
    - Wenn nach Fehlern gesucht wird, analysiere die relevanten Module basierend auf der beschriebenen Funktionalität (z.B. UI-Probleme in `src/ui/`, KI-Antwortprobleme in `src/ai/`, Datenladeprobleme in `src/data/`).
    - Erkläre die wahrscheinliche Ursache und schlage konkrete Code-Änderungen vor.
- **Code-Implementierung:**
    - Identifiziere die korrekten Module für neue Features gemäß der Projektstruktur.
    - Halte dich an bestehende Code-Stile und Muster.
    - Wenn neue Abhängigkeiten nötig sind, erwähne, dass `requirements.txt` aktualisiert werden muss.
    - Stelle sicher, dass sensible Daten wie API-Keys über `.env` verwaltet und nicht fest im Code verankert werden.
- **Datenbezug:** Denke daran, dass die Kerndaten aus `data/Angebote.csv` stammen und sich auf Aldi/Lidl-Angebote beziehen.
- **Framework-Nutzung:** Nutze die Funktionen von Streamlit für UI und App-Flow. Verstehe, wie `app.py` die Komponenten verbindet.

Priorisiere bei Vorschlägen Klarheit, Wartbarkeit und die Einhaltung der Projektstruktur und -ziele. 