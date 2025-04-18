# SparFuchs.de - KI-Assistent für Supermarkt-Angebote

## Projektübersicht
SparFuchs.de ist ein KI-gestützter Assistent, der Nutzern hilft, aktuelle Angebote von Aldi und Lidl zu finden und zu vergleichen. Die Anwendung nutzt Streamlit für die Benutzeroberfläche und OpenRouter für die KI-Generierung von Antworten basierend auf CSV-Produktdaten.

## Hauptfunktionen
- Chatbasierte Benutzeroberfläche für einfache Anfragen zu Angeboten
- Intelligente Produktsuche mit semantischem Verständnis von Kategorien
- Vergleich von Angeboten zwischen verschiedenen Supermärkten
- Responsive Design für optimale Nutzung auf verschiedenen Geräten

## Struktur der Anwendung

### app.py
Die Hauptanwendung enthält alle Streamlit-Funktionen und Logik für:
- Datenverarbeitung und CSV-Import
- KI-Modellintegration über OpenRouter
- Benutzeroberfläche und Chat-Funktionalität
- Prompting und Antwortgenerierung

Schlüsselfunktionen:
- `load_csv_data()`: Lädt Produktdaten aus der CSV-Datei
- `process_query()`: Verarbeitet Benutzeranfragen und bereitet KI-Prompts vor
- `get_filtered_products_context()`: Filtert relevante Produkte für Anfragen
- `detect_hallucinations()`: Überprüft KI-Antworten auf erfundene Produkte

### static/styles.dev.css
Diese Datei enthält alle CSS-Styles für die Anwendung:
- Farbschema und Design-Variablen
- Layout und Container-Strukturen
- Chat-Nachrichten-Styling
- Responsive Design für Mobile und Desktop
- Animationen und visuelle Effekte

Die CSS-Struktur verwendet:
- CSS-Variablen für konsistentes Theming
- Spezifische Selektoren für Streamlit-Komponenten
- Media Queries für responsives Design

## Verknüpfung zwischen Python und CSS
Die app.py verwendet an mehreren Stellen unsicheres HTML, um die CSS-Klassen anzuwenden:
- `apply_modern_supermarket_style()` lädt die CSS-Datei in die Anwendung
- `st.markdown()` mit `unsafe_allow_html=True` wird verwendet, um HTML-Elemente mit CSS-Klassen einzufügen
- Die Funktion `create_minified_css_file()` komprimiert die CSS-Datei für Produktionsumgebungen

## Datenstruktur
Die Anwendung verwendet eine CSV-Datei namens "Aldi_Lidl_Angebote.csv" mit folgenden Spalten:
- Produktname
- Kategorie
- Unterkategorie
- Preis_EUR
- Startdatum
- Enddatum
- Supermarkt

## Installation und Ausführung
1. Abhängigkeiten installieren: `pip install -r requirements.txt`
2. OpenAI API-Schlüssel in .env-Datei hinterlegen
3. Anwendung starten: `streamlit run app.py`
