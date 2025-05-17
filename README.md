# SparFuchs.de

SparFuchs.de ist ein KI-gestützter Assistent für Supermarkt-Angebote. Die Anwendung ermöglicht Nutzern, aktuelle Angebote von Aldi, Lidl, Rewe, Edeka und Penny per Chat-Interface abzufragen.

## Funktionen

- **KI-gestützte Produktsuche**: Finde Angebote von Aldi, Lidl, Rewe, Edeka und Penny durch natürlichsprachliche Anfragen
- **Semantische Suche**: Intelligente Erkennung von Produktkategorien und -beziehungen
- **Preisvergleiche**: Vergleiche Preise zwischen verschiedenen Supermärkten
- **Modernes UI**: Responsive Benutzeroberfläche mit Chat-Interface
- **Rezeptsuche mit Angebotsintegration**: Finde Rezepte (aus `data/More_Rezepte.csv`) und erhalte automatisch passende Angebote für die benötigten Zutaten.

## Installation

1. Klone dieses Repository
2. Installiere die erforderlichen Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```
3. Erstelle eine `.env` Datei im Hauptverzeichnis mit folgendem Inhalt:
   ```
   OPENROUTER_API_KEY=dein_openrouter_api_key_hier
   ```
4. Stelle sicher, dass die Produktdaten-CSV im `data/` Verzeichnis vorhanden ist.

## Verwendung

Starte die Anwendung mit:

```
streamlit run app.py
```

Die Anwendung ist dann unter http://localhost:8501 erreichbar.

## Projektstruktur

```
sparfuchs/
├── app.py                  # Hauptanwendung
├── .env                    # Umgebungsvariablen (API-Keys etc.)
├── requirements.txt        # Abhängigkeiten
├── README.md               # Dokumentation
├── static/                 # Statische Dateien
│   ├── styles.dev.css      # Entwicklungs-CSS
│   └── styles.min.css      # Minimiertes CSS
├── data/                   # Datendateien
│   ├── Angebote.csv
│   └── More_Rezepte.csv    # Rezepte-Datenbank (More)
└── src/                    # Quellcode
    ├── __init__.py
    ├── ui/                 # UI-Komponenten
    │   ├── __init__.py
    │   ├── layout.py       # Layout-Funktionen
    │   ├── styling.py      # CSS-Verarbeitung
    │   └── market_toggles.py # UI-Element für Supermarkt-Auswahl und Rezept-Toggle
    ├── data/               # Datenverarbeitung
    │   ├── __init__.py
    │   └── product_data.py # CSV-Ladelogik
    ├── ai/                 # KI-Komponenten
    │   ├── __init__.py
    │   ├── client.py       # OpenRouter-Client
    │   ├── context.py      # Kontextgenerierung
    │   └── hallucination.py # Hallucinationserkennung
    └── utils/              # Hilfsfunktionen
        ├── __init__.py
        ├── helpers.py      # Allgemeine Hilfsfunktionen
        └── ingredient_parser.py # Parser für Zutatenlisten
```

## Lizenz

© SparFuchs.de - Alle Rechte vorbehalten

## Author

SparFuchs.de Team 