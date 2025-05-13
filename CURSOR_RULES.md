# Cursor Rules for SparFuchs.de

**WICHTIG: Antworte immer auf Deutsch.**

Du bist ein KI-Assistent, der bei der Entwicklung der Python-Webanwendung "SparFuchs.de" hilft.
Die Anwendung nutzt Streamlit für das Frontend (Chat-Interface) und interagiert mit einer KI (via OpenRouter), um Nutzern aktuelle Supermarkt-Angebote basierend auf natürlichsprachlichen Anfragen zu liefern.

## Allgemeine Beschreibung der Anwendung "SparFuchs.de"

Der SparFuchs.de AI Assistent ist ein spezialisierter virtueller Helfer für Preisvergleiche und Angebotssuche bei deutschen Supermärkten. Er verfügt über aktuelles Wissen zu Angeboten bei **Aldi, Lidl, Rewe, Edeka und Penny** und hilft Nutzern dabei, die besten Preise für ihre Einkäufe zu finden. Der Assistent ist darauf ausgelegt, sowohl einfache Produktanfragen als auch komplexere Preisvergleiche zu bearbeiten.

### Fähigkeiten und Eigenschaften
- **Umfassendes Angebotswissen:**
  - Aktuelle Informationen zu Preisen und Angeboten bei Aldi, Lidl, Rewe, Edeka und Penny.
  - Vergleichsmöglichkeiten zwischen verschiedenen Produkten und Supermärkten.
  - Detaillierte Angaben zu Preisen, Gültigkeitsdaten und Produktdetails.
- **Benutzerfreundliche Antworten:**
  - Klare und präzise Darstellung von Angebotsinformationen.
  - Formatierte Listen mit übersichtlichen Preisangaben und Supermarktinformationen.
  - Einfache Navigation durch komplexe Preisvergleiche.
- **Preisvergleichsfunktionen:**
  - Identifizierung der günstigsten Angebote für gesuchte Produkte.
  - Vergleich ähnlicher Produkte aus verschiedenen Kategorien.
  - Hervorhebung besonders guter Angebote und Sonderaktionen.
- **Einkaufsberatung:**
  - Vorschläge für preiswerte Alternativen zu gesuchten Produkten.
  - Hinweise auf zeitlich begrenzte Angebote.
  - Transparente Darstellung von Preis-Leistungs-Verhältnissen.

### Funktionen und Dienstleistungen der Anwendung
- **Angebotssuche:**
  - Schnelle Abfrage aktueller Angebote nach Produktnamen oder Kategorien.
  - Filterung von Angeboten nach Supermarkt, Preis oder Kategorie.
  - Hervorhebung besonders günstiger oder zeitlich begrenzter Angebote.
- **Preisvergleich:**
  - Direkte Gegenüberstellung ähnlicher Produkte aus verschiedenen Supermärkten.
  - Berechnung und Anzeige von Preisunterschieden.
  - Identifikation des besten Preis-Leistungs-Verhältnisses.
- **Kategorie-Übersichten:**
  - Zusammenfassung aller Angebote in bestimmten Produktkategorien.
  - Auflistung der günstigsten Optionen pro Kategorie.
  - Saisonale Angebotsübersichten für bestimmte Produktgruppen.
- **Einkaufslisten-Optimierung:**
  - Analyse mehrerer Produkte und Vorschläge für den günstigsten Einkauf.
  - Verteilung von Einkäufen auf verschiedene Supermärkte zur Kostenoptimierung.
  - Berücksichtigung von Gültigkeitszeiträumen bei Angeboten.

### Zielgruppe
- **Preisbewusste Einkäufer:** Verbraucher, Familien, Studenten.
- **Regelmäßige Supermarktkunden:** Stammkunden von Aldi, Lidl, etc.
- **Angebotsvergleicher:** Nutzer, die systematisch Preise vergleichen.

### Ziele und Vision der Anwendung
Der SparFuchs.de AI Assistent zielt darauf ab, Verbrauchern Zeit und Geld beim Einkaufen zu sparen, indem er aktuelle und genaue Informationen zu Supermarktangeboten bereitstellt. Durch präzise Preisvergleiche und benutzerfreundliche Darstellung hilft er Nutzern, informierte Einkaufsentscheidungen zu treffen und das beste Preis-Leistungs-Verhältnis zu erzielen.

## Kerntechnologien & Stack

- **Sprache:** Python 3.9+
- **Web Framework / UI:** Streamlit
  - Wichtige Komponenten: `st.chat_message` für Chat-Interface, `st.session_state` für Chatverlauf.
- **KI-Backend:** OpenAI-Modelle über OpenRouter API (API-Key in `.env` Datei)
- **Datenquelle:** CSV-Datei (`data/Angebote.csv`)
  - Hauptkategorien: Produktname, Preis, Supermarkt, Gültigkeitsdatum.
- **Datenverarbeitung:** Pandas (Standard für CSV in Python, siehe `src/data/product_data.py`)
  - Produktsuche basiert auf semantischer Ähnlichkeit und Kategorisierung.
  - Preisberechnungen und -vergleiche berücksichtigen Mengen- und Einheiteninformationen.
- **Styling:** CSS (`static/styles.dev.css`, `static/styles.min.css`), geladen/verwaltet über `src/ui/styling.py`. Responsives Design.
- **Abhängigkeiten:** Verwaltet in `requirements.txt`.

## Projektstruktur & Wichtige Module

Beachte die folgende Struktur und die Verantwortlichkeiten der Module:

- **`app.py`**: Haupt-Einstiegspunkt der Streamlit-Anwendung. Orchestriert UI und Logik.
- **`src/`**: Kernlogik der Anwendung.
  - **`ui/`**: Verantwortlich für UI-Komponenten (`layout.py`, Nutzung von `st.chat_message`, `st.session_state`) und Styling (`styling.py`). Nutzt Streamlit-Elemente.
  - **`data/`**: Lädt und verarbeitet Produktdaten aus der CSV (`product_data.py`). Beinhaltet Logik für semantische Suche, Kategorisierung und Preisberechnung unter Berücksichtigung von Mengen/Einheiten.
  - **`ai/`**: Beinhaltet die gesamte KI-Logik:
    - `client.py`: Kommunikation mit der OpenRouter API.
    - `context.py`: Erstellt den Kontext/Prompt für die KI basierend auf Nutzereingaben und Produktdaten.
    - `hallucination.py`: Logik zur Erkennung von KI-Halluzinationen.
  - **`utils/`**: Allgemeine Hilfsfunktionen (`helpers.py`).
- **`data/`**: Speicherort für Datendateien, primär `Angebote.csv`. Enthält Angebote für Aldi, Lidl, Rewe, Edeka, Penny.
- **`static/`**: Statische Dateien wie CSS.
- **`.env`**: Speichert Umgebungsvariablen (z.B. `OPENAI_API_KEY`). **Wichtig:** Darf nicht versioniert werden.

## Kernkonzepte & Domain

- **Fokus:** Aktuelle Angebote von **Aldi, Lidl, Rewe, Edeka und Penny**.
- **Interaktion:** Über ein Chat-Interface (Streamlit mit `st.chat_message` und `st.session_state`).
- **Suche:** Semantische, natürlichsprachliche Produktsuche; Filterung nach Supermarkt, Preis, Kategorie.
- **Daten:** Produktinformationen (Name, Preis, Supermarkt, Gültigkeitsdatum) und Preise aus der CSV. Mengen- und Einheiteninformationen sind relevant.
- **KI-Zuverlässigkeit:** Halluzinationserkennung ist ein wichtiger Aspekt (`src/ai/hallucination.py`).

## Coding Style & Konventionen

- Folge standardmäßigen Python Best Practices (PEP 8).
- Schreibe klaren, lesbaren und gut kommentierten Code, insbesondere in den `ai/` und `data/` Modulen.
- Nutze Type Hints zur Verbesserung der Codequalität und Verständlichkeit.
- Halte Streamlit-Komponenten in `src/ui/` modular.
- Achte auf sauberes Fehlerhandling, besonders bei API-Aufrufen (`ai/client.py`) und Datenzugriffen (`data/product_data.py`).

## Anweisungen für die KI-Assistenz

- **Kontext verstehen:** Beziehe dich bei Code-Analysen oder Änderungen immer auf die oben beschriebene Projektstruktur, die Anwendungsfunktionen und -ziele sowie die Zuständigkeiten der Module. Verstehe, dass die App Nutzern hilft, bei Aldi, Lidl, Rewe, Edeka und Penny zu sparen.
- **Fehlersuche:**
    - Wenn nach Fehlern gesucht wird, analysiere die relevanten Module basierend auf der beschriebenen Funktionalität (z.B. UI-Probleme in `src/ui/`, KI-Antwortprobleme in `src/ai/`, Datenladeprobleme in `src/data/`).
    - Erkläre die wahrscheinliche Ursache und schlage konkrete Code-Änderungen vor.
- **Code-Implementierung:**
    - Identifiziere die korrekten Module für neue Features gemäß der Projektstruktur und den beschriebenen Anwendungsfunktionen.
    - Halte dich an bestehende Code-Stile und Muster.
    - Wenn neue Abhängigkeiten nötig sind, erwähne, dass `requirements.txt` aktualisiert werden muss.
    - Stelle sicher, dass sensible Daten wie API-Keys über `.env` verwaltet und nicht fest im Code verankert werden.
- **Datenbezug:** Denke daran, dass die Kerndaten aus `data/Angebote.csv` stammen und sich auf Angebote von Aldi, Lidl, Rewe, Edeka und Penny beziehen. Berücksichtige die Datenstruktur (Produktname, Preis, Supermarkt, Gültigkeitsdatum) und die Bedeutung von Mengen-/Einheiteninformationen.
- **Framework-Nutzung:** Nutze die Funktionen von Streamlit für UI und App-Flow (z.B. `st.chat_message`, `st.session_state`). Verstehe, wie `app.py` die Komponenten verbindet.
- **Proaktive Unterstützung:** Wenn du Fragen zur Code-Struktur, Implementierungsdetails oder Erweiterungsmöglichkeiten der SparFuchs.de App hast, kannst du technische Erklärungen und Unterstützung anbieten, um die Entwicklung zu fördern.

Priorisiere bei Vorschlägen Klarheit, Wartbarkeit und die Einhaltung der Projektstruktur und -ziele. 