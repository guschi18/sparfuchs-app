"""
SparFuchs.de - KI-gestützter Assistent für Supermarkt-Angebote.

Diese Anwendung ermöglicht Nutzern, aktuelle Angebote von Aldi und Lidl per Chat-Interface
abzufragen. Die App nutzt Streamlit für die Benutzeroberfläche, eine CSV-Datei für die
Produktdaten und OpenRouter für die KI-Antwortgenerierung.

Hauptfunktionen:
- Laden und Filtern von Produktdaten
- Chat-Interface für Benutzeranfragen
- KI-gestützte Antwortgenerierung
- Erkennung von KI-Halluzinationen
- Modernes UI mit responsivem Design

Autor: SparFuchs.de Team
"""
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import random
import time
from datetime import datetime, timedelta
import re
from pathlib import Path

# HINWEIS: st.set_page_config muss vor allen anderen st-Aufrufen stehen
# Streamlit Seitenkonfiguration
st.set_page_config(
    page_title="SparFuchs.de", 
    page_icon="🛒",
    layout="centered"
)

# Deploy-Button, Menü und Header ausblenden (nach set_page_config)
st.markdown("""
<style>
.stDeployButton {visibility: hidden;}
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}

/* Manage App Balken ausblenden */
[data-testid="manage-app-button"],
.stToolbar,
.st-emotion-cache-h5rgaw,
section[data-testid="stToolbar"],
[data-testid="stToolbar"] {
    display: none !important;
    visibility: hidden !important;
}

/* Zusätzliche Sicherheit für alle festen Elemente am unteren Bildschirmrand */
div[style*="position: fixed; bottom"] {
    display: none !important;
    visibility: hidden !important;
    height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
}
</style>
""", unsafe_allow_html=True)

# Umgebungsvariablen laden
load_dotenv()

# OpenAI Client konfigurieren (für OpenRouter)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"  # OpenRouter API-Basis-URL
)

# CSS für modernes Design
def apply_modern_supermarket_style():
    """
    Lädt die CSS-Styles aus der minimfizierten CSS-Datei und wendet sie auf die Streamlit-App an.
    
    Die Funktion stellt sicher, dass der 'static'-Ordner existiert und dass die CSS-Datei
    vorhanden ist. Falls die minimierte CSS-Datei nicht existiert, wird sie erstellt.
    """
    # Stelle sicher, dass der static-Ordner existiert
    static_dir = Path("static")
    if not static_dir.exists():
        static_dir.mkdir(exist_ok=True)
    
    css_file_path = static_dir / "styles.min.css"
    
    # Prüfe, ob die minimierte CSS-Datei existiert
    if not css_file_path.exists():
        create_minified_css_file()
    
    # CSS aus der Datei laden und anwenden
    with open(css_file_path, "r", encoding="utf-8") as f:
        css = f.read()
    
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Eine neue Datei mit dem minimierten CSS erstellen
def create_minified_css_file():
    """
    Erstellt eine minimierte Version der CSS-Datei für bessere Performance.
    
    Die Funktion liest die Entwicklungs-CSS-Datei (styles.dev.css), minimiert deren Inhalt
    durch Entfernung von Kommentaren und unnötigen Leerzeichen und speichert das Ergebnis als
    styles.min.css. Wenn die Entwicklungsdatei nicht existiert, wird eine Basisdatei erstellt.
    """
    # Stelle sicher, dass der static-Ordner existiert
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Entwicklungs-CSS-Datei lesen
    dev_css_path = static_dir / "styles.dev.css"
    if dev_css_path.exists():
        with open(dev_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        
        # Einfache CSS-Minimierung (Entfernung von Kommentaren und Leerzeichen)
        # In einer produktiven Umgebung könnte man hier ein richtiges CSS-Minimierungstool verwenden
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)  # Kommentare entfernen
        css_content = re.sub(r'\s+', ' ', css_content)  # Mehrfach-Leerzeichen zu einem reduzieren
        css_content = css_content.strip()
        
        # Speichern der minimierten CSS-Datei
        min_css_path = static_dir / "styles.min.css"
        with open(min_css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
    else:
        # Fallback: Wenn keine styles.dev.css existiert, erstelle eine leere CSS-Datei
        # und gib eine Warnung aus
        min_css_path = static_dir / "styles.min.css"
        with open(min_css_path, "w", encoding="utf-8") as f:
            f.write("/* Automatisch generierte leere CSS-Datei. Bitte static/styles.dev.css erstellen und neu laden. */")
        
        # Gib eine Warnung im UI aus
        st.warning("Die CSS-Entwicklungsdatei 'static/styles.dev.css' wurde nicht gefunden. Bitte erstellen Sie diese Datei für ein besseres UI-Design.")
        
        # Erstelle eine Basis-Entwicklungsdatei als Vorlage
        with open(dev_css_path, "w", encoding="utf-8") as f:
            f.write("""/* == Basis-CSS-Vorlage == */
:root {
  --text-color: #2A2A2A;
  --bg-color: #FDFDFD;
  --white: #FFF;
  --primary-color: #28A745;
  --secondary-color: #FF6600;
  --border-color: #E0E0E0;
  --border-radius: 10px;
}

/* Geben Sie hier Ihre CSS-Anpassungen ein */
""")

# Beispielprodukte hinzufügen falls keine CSV-Datei vorhanden ist
def create_sample_data():
    """
    Erstellt Beispieldaten für Produkte, falls keine CSV-Datei vorhanden ist.
    
    Returns:
        DataFrame: Ein Pandas DataFrame mit Beispielprodukten, inklusive zufällig
                  generierter Gültigkeitsdaten.
    """
    # Beispielprodukte
    products = [
        {"Produktname": "Bio Äpfel", "Kategorie": "Obst & Gemüse", "Unterkategorie": "Obst", "Preis_EUR": 2.99, "Supermarkt": "Aldi"},
        {"Produktname": "Rinderhackfleisch", "Kategorie": "Lebensmittel", "Unterkategorie": "Fleisch", "Preis_EUR": 5.49, "Supermarkt": "Aldi"},
        {"Produktname": "Bio Vollmilch", "Kategorie": "Lebensmittel", "Unterkategorie": "Milchprodukte", "Preis_EUR": 1.29, "Supermarkt": "Lidl"},
        {"Produktname": "Mehrkornbrot", "Kategorie": "Lebensmittel", "Unterkategorie": "Backwaren", "Preis_EUR": 2.19, "Supermarkt": "Lidl"},
        {"Produktname": "Mascarpone", "Kategorie": "Lebensmittel", "Unterkategorie": "Milchprodukte/Käse", "Preis_EUR": 1.79, "Supermarkt": "Aldi"},
        {"Produktname": "Spanische Orangen", "Kategorie": "Lebensmittel", "Unterkategorie": "Obst", "Preis_EUR": 3.49, "Supermarkt": "Lidl"},
        {"Produktname": "Lachsfilet", "Kategorie": "Lebensmittel", "Unterkategorie": "Fisch/Meeresfrüchte", "Preis_EUR": 8.99, "Supermarkt": "Aldi"},
        {"Produktname": "Avocado", "Kategorie": "Lebensmittel", "Unterkategorie": "Obst", "Preis_EUR": 1.99, "Supermarkt": "Lidl"}
    ]
    
    # Zufällige Gültigkeitsdaten generieren
    today = datetime.today()
    
    for product in products:
        valid_from = today - timedelta(days=random.randint(0, 5))
        valid_to = today + timedelta(days=random.randint(3, 14))
        product["Startdatum"] = valid_from.strftime("%d.%m.%Y")
        product["Enddatum"] = valid_to.strftime("%d.%m.%Y")
    
    return pd.DataFrame(products)

# CSV-Datei laden
@st.cache_data
def load_csv_data():
    """
    Lädt die Produktdaten aus der CSV-Datei oder erstellt Beispieldaten, wenn die Datei nicht existiert.
    
    Die Funktion ist mit @st.cache_data dekoriert, um Mehrfachladungen zu vermeiden und die
    Performance zu verbessern.
    
    Returns:
        DataFrame: Ein Pandas DataFrame mit den Produktdaten.
    """
    try:
        df = pd.read_csv("Aldi_Lidl_Angebote.csv")
        if df.empty:
            return create_sample_data()
        return df
    except Exception as e:
        # Wenn ein Fehler auftritt, verwenden wir Beispieldaten
        return create_sample_data()

# Funktion zum Überprüfen, ob die Antwort Produkte enthält, die nicht in der CSV sind
def detect_hallucinations(response, df):
    """
    Prüft, ob die KI-Antwort möglicherweise halluzinierte Produkte enthält.
    
    Die Funktion analysiert die KI-Antwort und vergleicht erwähnte Produkte mit den
    tatsächlich in der Datenbank vorhandenen Produkten, um Halluzinationen zu erkennen.
    
    Args:
        response (str): Die Antwort des KI-Modells
        df (DataFrame): Der Produktdatensatz
    
    Returns:
        bool: True, wenn die Antwort wahrscheinlich halluzinierte Produkte enthält
    """
    # Wenn die Antwort einen Hinweis enthält, dass Produkte nicht gefunden wurden
    if "keine Informationen" in response.lower() or "nicht gefunden" in response.lower() or "keine aktuellen angebote" in response.lower():
        return False
    
    # Extrahiere Produktnamen aus der CSV
    produktnamen = df['Produktname'].str.lower().tolist()
    
    # Füge Kategorien und Unterkategorien als erlaubte Begriffe hinzu
    kategorien = df['Kategorie'].str.lower().unique().tolist()
    unterkategorien = []
    for uk in df['Unterkategorie'].dropna():
        # Unterkategorien können mehrere Begriffe mit "/" enthalten, diese aufteilen
        if isinstance(uk, str):
            unterkategorien.extend([u.strip().lower() for u in uk.split('/')])
    unterkategorien = list(set(unterkategorien))  # Duplikate entfernen
    
    # Extrahiere alle Produktnamenteile für flexibleres Matching
    produktteile = []
    for name in produktnamen:
        teile = name.split()
        for teil in teile:
            if len(teil) > 3:  # Nur längere Begriffe verwenden
                produktteile.append(teil.lower())
    produktteile = list(set(produktteile))  # Duplikate entfernen
    
    # Füge Supermarktnamen und weitere allgemeine Begriffe hinzu
    allgemeine_begriffe = ['aldi', 'lidl', 'supermarkt', 'angebot', 'preis', 'euro', '€', 
                          'gültig', 'von', 'bis', 'startdatum', 'enddatum', 'preisvergleich',
                          'getränke', 'lebensmittel', 'hier sind', 'aktuell', 'im angebot',
                          'rum', 'vodka', 'whiskey', 'bier', 'wein', 'gin', 'likör', 'spirituosen',
                          'alkohol', 'mineralwasser', 'cola', 'saft', 'ja', 'nein', 'leider', 'finden',
                          'diese', 'woche', 'club', 'havana']
    
    erlaubte_begriffe = produktnamen + kategorien + unterkategorien + allgemeine_begriffe + produktteile
    
    # Extrahiere alle fettgedruckten Texte (wahrscheinlich Produktnamen)
    bold_products = re.findall(r'\*\*(.*?)\*\*', response)
    
    # Wenn es keine fettgedruckten Texte gibt (z.B. bei kategorie-basierten Anfragen ohne konkretes Produkt)
    if not bold_products:
        return False
    
    # Prüfe jeden fettgedruckten Text, ob er ein tatsächliches Produkt sein könnte
    for product in bold_products:
        # Entferne Zusatzinformationen in Klammern und Preis-Suffix
        clean_product = re.sub(r'\s*\(.*?\)', '', product).split(':')[0].strip().lower()
        
        # Prüfe, ob das Produkt einer Variation eines CSV-Produkts ähnelt
        found = False
        for erlaubter_begriff in erlaubte_begriffe:
            # Prüfe auf teilweise Übereinstimmung (z.B. "Äpfel" vs. "Bio Äpfel")
            if clean_product in erlaubter_begriff or erlaubter_begriff in clean_product:
                found = True
                break
            
            # Bei zusammengesetzten Begriffen prüfen, ob Teile übereinstimmen
            parts = clean_product.split()
            for part in parts:
                if len(part) > 3 and (part in erlaubter_begriff or erlaubter_begriff in part):
                    found = True
                    break
            if found:
                break
        
        if not found and len(clean_product) > 3:  # Ignoriere sehr kurze Begriffe
            print(f"Mögliche Halluzination gefunden: {clean_product}")  # Debug-Info
            return True
    
    return False

# Daten in String umwandeln für den Kontext
def get_products_context():
    """
    Wandelt die Produktdaten in einen formatierten Textstring für den KI-Kontext um.
    
    Die Funktion lädt die Produktdaten und formatiert sie als Textstring, der als
    Kontext für die KI-Anfragen verwendet wird.
    
    Returns:
        str: Formatierter Text mit allen Produktinformationen
    """
    df = load_csv_data()
    if df.empty:
        return "Keine Produktdaten verfügbar."
    
    # Filtere Produkte mit Preis 0.0 oder leeren Preisen heraus
    df = df[df['Preis_EUR'] != 0.0]
    
    context = "Aktuelle Aldi und Lidl Angebote:\n\n"
    for _, row in df.iterrows():
        # Zugriff auf die deutschen Spaltenbezeichnungen
        produkt = row.get('Produktname', 'N/A')
        kategorie = row.get('Kategorie', 'N/A')
        unterkategorie = row.get('Unterkategorie', 'N/A')
        preis = row.get('Preis_EUR', 'N/A')
        start_datum = row.get('Startdatum', 'N/A')
        end_datum = row.get('Enddatum', 'N/A')
        supermarkt = row.get('Supermarkt', 'N/A')
        
        # Format angepasst, um einfacher in das gewünschte Ausgabeformat umgewandelt werden zu können
        product_info = (
            f"Produkt: {produkt}\n"
            f"Kategorie: {kategorie}\n"
            f"Unterkategorie: {unterkategorie}\n"
            f"Preis: {preis}\n"
            f"Startdatum: {start_datum}\n"
            f"Enddatum: {end_datum}\n"
            f"Supermarkt: {supermarkt}\n\n"
        )
        
        context += product_info
    
    return context

# Funktion, die Produkte nach Kategorie filtert (für Kontext-Optimierung)
def get_filtered_products_context(user_query):
    """
    Filtert die Produktdaten basierend auf der Benutzeranfrage und erstellt einen optimierten Kontext.
    
    Die Funktion analysiert die Benutzeranfrage semantisch, um relevante Produkte zu identifizieren,
    und erstellt einen optimierten Kontext für die KI. Sie berücksichtigt dabei:
    - Semantische Gruppen von Produkten (z.B. "Nudeln" umfasst verschiedene Pasta-Arten)
    - Spezifische Supermarkt-Filter
    - Kategorie-basierte Filter
    
    Args:
        user_query (str): Die Anfrage des Benutzers
        
    Returns:
        str: Optimierter Kontext mit gefilterten Produktinformationen
    """
    df = load_csv_data()
    if df.empty:
        return "Keine Produktdaten verfügbar."
    
    # Filtere Produkte mit Preis 0.0 oder leeren Preisen heraus
    df = df[df['Preis_EUR'] != 0.0]
    
    # Wichtige Produktkategorien für semantische Erweiterungen
    semantic_groups = {
        "nudeln": ["pasta", "nudel", "tortelloni", "farfalle", "spaghetti", "penne", "fusilli", "lasagne"],
        "getränke": ["wasser", "saft", "limo", "limonade", "cola", "bier", "wein", "schnaps", "alkohol", "mineralwasser", "eistee"],
        "obst": ["apfel", "banane", "orange", "birne", "trauben", "beeren", "früchte"],
        "gemüse": ["salat", "gurke", "tomate", "kartoffel", "möhre", "paprika", "zwiebel", "karotte", "zucchini"],
        "fleisch": ["rind", "schwein", "hähnchen", "hühnchen", "pute", "lamm", "wurst"],
        "süßigkeiten": ["schoko", "schokolade", "bonbon", "keks", "kuchen", "süßware", "gebäck", "riegel"],
        "milchprodukte": ["käse", "joghurt", "quark", "sahne", "milch", "butter"]
    }
    
    # Liste der möglichen Kategorien - nur für grundlegendste Filterung
    kategorie_mapping = {
        "getränk": "Getränke",
        "getränke": "Getränke",
        "lebensmittel": "Lebensmittel",
        "drogerie": "Drogerie",
        "haushalt": "Haushalt",
        "kleidung": "Kleidung",
        "garten": ["Garten/Pflanzen", "Garten", "Pflanzen"]
    }
    
    # Normalisiere den Suchbegriff
    user_query_lower = user_query.lower()
    
    # Supermarkt filtern
    supermarkt_filter = None
    if "aldi" in user_query_lower and "lidl" not in user_query_lower:
        supermarkt_filter = "Aldi"
    elif "lidl" in user_query_lower and "aldi" not in user_query_lower:
        supermarkt_filter = "Lidl"
    
    # Extrahiere alle Wörter mit mindestens 3 Zeichen als potenzielle Suchbegriffe
    query_words = [word for word in re.findall(r'\b\w+\b', user_query_lower) if len(word) >= 3]
    
    # Erstelle eine Liste aller möglichen Suchbegriffe
    search_terms = set(query_words)
    
    # Erweitere Suchbegriffe mit semantisch ähnlichen Begriffen
    expanded_search_terms = set(search_terms)
    
    # Prüfe für jeden Begriff in der Anfrage, ob er in einer semantischen Gruppe ist
    for word in search_terms:
        for category, related_terms in semantic_groups.items():
            # Wenn der Begriff in den verwandten Begriffen ist oder der Kategorienname selbst
            if word in related_terms or word == category:
                # Füge die Kategorie und alle verwandten Begriffe hinzu
                expanded_search_terms.add(category)
                expanded_search_terms.update(related_terms)
                break
    
    # Kategorie aus Anfrage extrahieren (wird nur als Fallback verwendet)
    kategorie_filter = None
    for key, value in kategorie_mapping.items():
        if key in user_query_lower:
            kategorie_filter = value
            break
    
    # Wir versuchen eine breitere Suche mit den erweiterten Begriffen
    if expanded_search_terms:
        # Initialisiere leere Maske
        mask = pd.Series(False, index=df.index)
        
        # Erweitere die Maske mit jedem Suchbegriff
        for term in expanded_search_terms:
            # Suche in Produktnamen, Kategorie und Unterkategorie
            name_mask = df['Produktname'].str.contains(term, case=False, na=False)
            kat_mask = df['Kategorie'].str.contains(term, case=False, na=False)
            unterkat_mask = df['Unterkategorie'].str.contains(term, case=False, na=False)
            
            # Kombiniere die Masken mit OR
            mask = mask | name_mask | kat_mask | unterkat_mask
        
        filtered_df = df[mask]
        
        # Wenn nichts gefunden wurde, versuchen wir es mit nur den originalen Suchbegriffen
        if filtered_df.empty:
            mask = pd.Series(False, index=df.index)
            for term in search_terms:
                name_mask = df['Produktname'].str.contains(term, case=False, na=False)
                kat_mask = df['Kategorie'].str.contains(term, case=False, na=False)
                unterkat_mask = df['Unterkategorie'].str.contains(term, case=False, na=False)
                mask = mask | name_mask | kat_mask | unterkat_mask
            filtered_df = df[mask]
        
        # Wenn immer noch nichts gefunden wurde, versuchen wir es mit einer lediglich nach Kategorie gefilterten Ansicht
        if filtered_df.empty and kategorie_filter:
            # Nach Kategorie filtern
            if isinstance(kategorie_filter, list):
                mask = pd.Series(False, index=df.index)
                for kat in kategorie_filter:
                    kat_mask = df['Kategorie'].str.contains(kat, case=False, na=False)
                    unterkat_mask = df['Unterkategorie'].str.contains(kat, case=False, na=False)
                    mask = mask | kat_mask | unterkat_mask
                filtered_df = df[mask]
            else:
                kat_mask = df['Kategorie'].str.contains(kategorie_filter, case=False, na=False)
                unterkat_mask = df['Unterkategorie'].str.contains(kategorie_filter, case=False, na=False)
                filtered_df = df[kat_mask | unterkat_mask]
        
        # Wenn immer noch nichts gefunden wurde, geben wir den vollständigen Kontext zurück
        if filtered_df.empty:
            return get_products_context()
            
        # Nach Supermarkt filtern, wenn angegeben
        if supermarkt_filter and not filtered_df.empty:
            temp_df = filtered_df[filtered_df['Supermarkt'] == supermarkt_filter]
            # Nur filtern, wenn Ergebnisse vorhanden sind
            if not temp_df.empty:
                filtered_df = temp_df
    
    # Alle Produkte einbeziehen, wenn keine spezifische Kategorie oder Produkt erwähnt wird
    else:
        # Vollständigen Kontext zurückgeben
        return get_products_context()
    
    # Wenn keine passenden Produkte gefunden wurden, alle Produkte zurückgeben
    if filtered_df.empty:
        return get_products_context()
    
    # Kontext erstellen mit Suchbegriffen und Hinweisen für die KI
    context = f"Gefilterte Angebote basierend auf der Anfrage '{user_query}':\n\n"
    
    # Hinzufügen von hilfreichen Informationen für die KI zur semantischen Verarbeitung
    context += "WICHTIG FÜR SEMANTISCHE INTERPRETATION: Berücksichtige, dass die folgenden Produkte für die Anfrage relevant sein könnten, auch wenn sie nicht exakt dem Suchbegriff entsprechen. Denke über mögliche semantische Beziehungen nach, wie z.B.:\n"
    context += "- 'Nudeln' umfasst auch Pasta, Tortelloni, Farfalle, Spaghetti, Penne usw. - jegliche Art von Pasta ist eine Form von Nudeln.\n"
    context += "- 'Getränke' umfasst Wasser, Saft, Limonade, Cola, Bier, Wein, etc.\n"
    context += "- 'Süßigkeiten' umfasst Schokolade, Kekse, Fruchtgummi, etc.\n"
    context += "- 'Fleisch' umfasst verschiedene Fleischsorten wie Rind, Schwein, Geflügel, etc.\n"
    context += "- 'Bio-Pasta' und ähnliche Produkte sind definitiv Nudeln, auch wenn sie unter einer speziellen Marke (wie GUT BIO) verkauft werden.\n\n"
    context += "Verwende dein Wissen über Lebensmittelkategorien, um relevante Produkte zu identifizieren, auch wenn sie nicht exakt mit dem Suchbegriff übereinstimmen. Schau über Marken und Unterkategorien hinweg und konzentriere dich auf das eigentliche Produkt.\n\n"
    context += "HIER SIND DIE PRODUKTE:\n\n"
    
    for _, row in filtered_df.iterrows():
        produkt = row.get('Produktname', 'N/A')
        kategorie = row.get('Kategorie', 'N/A')
        unterkategorie = row.get('Unterkategorie', 'N/A')
        preis = row.get('Preis_EUR', 'N/A')
        start_datum = row.get('Startdatum', 'N/A')
        end_datum = row.get('Enddatum', 'N/A')
        supermarkt = row.get('Supermarkt', 'N/A')
        
        product_info = (
            f"Produkt: {produkt}\n"
            f"Kategorie: {kategorie}\n"
            f"Unterkategorie: {unterkategorie}\n"
            f"Preis: {preis}\n"
            f"Startdatum: {start_datum}\n"
            f"Enddatum: {end_datum}\n"
            f"Supermarkt: {supermarkt}\n\n"
        )
        
        context += product_info
    
    return context

# AI-Antwort generieren
def process_query(prompt):
    """
    Verarbeitet eine Benutzeranfrage und bereitet den Kontext für die KI-Antwort vor.
    
    Die Funktion erstellt einen system_prompt und einen context_message für die KI-Anfrage,
    basierend auf der Benutzeranfrage und den gefilterten Produktdaten.
    
    Args:
        prompt (str): Die Anfrage des Benutzers
        
    Returns:
        tuple: (system_prompt, context_message, products_context)
               - system_prompt: Systemnachricht für die KI
               - context_message: Kontextnachricht mit Produktdaten
               - products_context: Gefilterte Produktdaten als Text
    """
    try:
        # OpenAI API-Aufruf mit neuer Syntax und erweitertem Kontext
        # Systemnachricht immer direkt verwenden (auch wenn sie im Session State geändert wurde)
        system_prompt = {
            "role": "system", 
            "content": "Du bist ein hilfreicher Einkaufsassistent für SparFuchs.de mit fundiertem Wissen über Lebensmittel und Produktkategorien. " +
            "Benutze die dir bereitgestellten Produktinformationen, um Anfragen zu beantworten. " +
            "WICHTIG: Du darfst NUR Produkte erwähnen, die in den bereitgestellten Daten vorhanden sind. " +
            "ERFINDE NIEMALS Produkte oder Angebote. Wenn du ein Produkt nicht in den Daten findest, sage klar, " +
            "dass du keine Information darüber hast. " +
            "SEMANTISCHE INTERPRETATION - SEHR WICHTIG: Wende dein volles Verständnis über Lebensmittelkategorien an. " +
            "PRODUKTBEZIEHUNGEN ERKENNEN: " +
            "- Wenn der Nutzer nach 'Nudeln' fragt, berücksichtige ALLE verschiedenen Arten wie: Pasta, Tortelloni, Farfalle, Spaghetti, Penne usw. " +
            "- Wenn 'Bio-Pasta' in den Daten steht, ist dies eine Art von Nudeln! " +
            "- Produktmarken (wie 'GUT BIO', 'CUCINA NOBILE') sind nur Markennamen, fokussiere dich auf die Produktart dahinter. " +
            "- Selbst wenn Produkte in unterschiedlichen Kategorien oder Unterkategorien aufgeführt sind, nutze dein Wissen, " +
            "  um zu erkennen, was sie wirklich sind (z.B. können Tortelloni unter 'Fertiggerichte' kategorisiert sein, sind aber trotzdem Nudeln). " +
            "WICHTIG: Nutze dein eigenes Wissen über Lebensmittel, um Produkte zu klassifizieren, unabhängig davon, " +
            "wie sie im Datensatz kategorisiert sind. " +
            "VOLLSTÄNDIGE ANTWORTEN: Bei Kategorie-Anfragen (z.B. 'Welche Getränke...' oder 'Welche Nudeln...') liste ALLE passenden Produkte auf, " +
            "die in den Daten vorhanden sind und zur semantischen Kategorie passen. Suche aktiv nach ALLEN relevanten Produkten. " +
            "WICHTIG: Antworte IMMER auf Deutsch, unabhängig von der Sprache der Anfrage. " +
            "WICHTIG: Verweise NIEMALS auf Angebotsbroschüren oder externe Quellen. " +
            "Antworte ausschließlich mit den Daten, die dir zur Verfügung gestellt werden. " + 
            "WICHTIG: Antworte erst, wenn du alle Informationen analysiert hast, um eine korrekte Antwort zu geben. " +
            "FORMATIERUNGSANWEISUNG: Formatiere deine Antworten zu Produkten immer in folgendem Format: " +
            "1. Beginne mit einer kurzen einleitenden Antwort, die die Frage beantwortet. " +
            "2. Liste dann jedes gefundene Produkt in folgendem klaren Format auf: " +
            "\n**Produktname** (mit Details wie Gewicht, Sorte, etc.): Preis €<br>" +
            "\n<strong class=\"meta-info\">Gültig:</strong> [DD.MM.YYYY] bis [DD.MM.YYYY]<br>" +
            "\n<strong class=\"meta-info\">Supermarkt:</strong> [Supermarktname]" +
            "\n\n" +
            "3. Bei Preisvergleichen oder Zusammenfassungen, nutze einen abschließenden Absatz mit einer klaren Kennzeichnung: " +
            "\n**Preisvergleich:** Das günstigste Produkt ist X für Y € (Z € pro kg/Stück)." +
            "\n\n" +
            "4. Wenn ein gesuchtes Produkt nicht verfügbar ist, teile dies explizit mit: " +
            "\n**Hinweis:** Bei [Produkt] habe ich leider keine aktuellen Angebote bei [Supermarkt] gefunden." +
            "\n\n" +
            "5. Verwende fettgedruckten Text für Hervorhebungen der Struktur-Elemente wie oben gezeigt." +
            "6. WICHTIG: Setze nach JEDEM Element einen HTML-Zeilenumbruch mit <br>. Jedes Element (Produktname, Gültig vom, Supermarkt) MUSS auf einer eigenen Zeile stehen!" +
            "7. EXTREM WICHTIG: Verwende das explizite HTML-Tag <br> nach jeder Zeile, anstatt nur Markdown-Zeilenumbrüche, damit die Elemente klar voneinander getrennt angezeigt werden." +
            "\n\n" +
            "Beispiel: " +
            "\nJa, bei Aldi gibt es aktuell Kartoffeln und Nudeln im Angebot:\n" +
            "\n**Speisefrühkartoffeln** (1,5 kg): 2,79 €<br>" +
            "\n<strong class=\"meta-info\">Gültig:</strong> 24.04.2025 bis 26.04.2025<br>" +
            "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi" +
            "\n\n" +
            "**CUCINA NOBILE Farfalle Fantasia** (versch. Sorten, 250 g): 1,49 €<br>" +
            "\n<strong class=\"meta-info\">Gültig:</strong> 22.04.2025 bis 26.04.2025<br>" +
            "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi" +
            "\n\n" +
            "**Hinweis:** Bei Reis habe ich leider keine aktuellen Angebote bei Aldi gefunden."
        }
        
        # Kontext aus der CSV-Datei holen
        products_context = get_filtered_products_context(prompt)
        
        # Erweitere die Systemnachricht mit dem aktuellen Kontext
        context_message = {"role": "system", "content": f"Hier sind die aktuellen Produktinformationen. Du DARFST NUR diese Produkte in deinen Antworten verwenden und KEINE anderen:\n\n{products_context}\n\nWICHTIG: DENKE AKTIV und GRÜNDLICH über die Anfrage und Produktkategorien nach. Erkenne semantische Beziehungen zwischen verschiedenen Produktbezeichnungen und Kategorien. Wenn z.B. ein 'GUT BIO Bio-Pasta' Produkt in den Daten enthalten ist und jemand nach 'Nudeln' fragt, dann ist dieses Produkt definitiv relevant und sollte genannt werden. Bei Pasta/Nudeln-Produkten achte auf alle Varianten wie Tortelloni, Farfalle, Spaghetti etc. - alle diese Produkte gehören zur Kategorie 'Nudeln'. Denke selbständig und nutze dein Lebensmittelwissen.\n\nWICHTIG: Verweise in deinen Antworten NIEMALS auf Angebotsbroschüren, Flyer oder andere externe Quellen. Verwende ausschließlich die oben aufgeführten Produktdaten."}
        
        return system_prompt, context_message, products_context
        
    except Exception as e:
        return None, None, str(e)


# Zusätzliche Funktion, die Vorschläge in einer Reihe anzeigt
def display_suggestions_row(suggestions):
    """
    Zeigt mehrere Vorschläge in einer Reihe an.
    
    Args:
        suggestions: Liste von Tupeln (text, icon)
    """
    # Container für die Vorschläge
    for text, icon in suggestions:
        # Erstelle einen Button mit einer eindeutigen ID
        button_id = f"suggestion_{hash(text)}"
        
        # Wenn der Button geklickt wird
        if st.button(f"{icon} {text}", key=button_id, type="secondary", use_container_width=True):
            # Text ins Textfeld kopieren UND direkt Anfrage senden
            st.session_state.preset_input = text
            st.session_state.submit_text = text
            # Löse Rerun aus, um die Verarbeitung zu starten
            st.rerun()

# CSS direkt am Anfang der Anwendung einfügen (KRITISCH: Dies muss vor allem anderen sein)
st.markdown("""
<style>
/* Container sind weiß mit beigen Seitenrändern */
.main .block-container {
    background-color: #ffffff !important;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    margin: 0 auto;
    max-width: 800px;
    padding: 20px;
}

/* Hintergrund der App bleibt beige */
body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stAppViewBlock"] {
    background-color: #E8E0D0 !important;
}

/* Chat-Nachrichten haben beige Hintergründe für einheitliches Design */
.stChatMessage, 
[data-testid="stChatMessage"] {
    background-color: #F2EEE5 !important;
    border: 1px solid #E0D8C8 !important;
    color: #333 !important;
}
.stChatMessage.user {
    background-color: #F7F3EA !important;
    border: 1px solid #E5DFD0 !important;
}
</style>
""", unsafe_allow_html=True)

# CSS-Datei neu kompilieren bei jedem Start
create_minified_css_file()

# Modernes Supermarkt-Design anwenden
apply_modern_supermarket_style()

# Session State für Chatverlauf initialisieren
if "messages" not in st.session_state:
    st.session_state.messages = [
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
        "FORMATIERUNGSANWEISUNG: Formatiere deine Antworten zu Produkten immer in folgendem Format: " +
        "1. Beginne mit einer kurzen einleitenden Antwort, die die Frage beantwortet. " +
        "2. Liste dann jedes gefundene Produkt in folgendem klaren Format auf: " +
        "\n**Produktname** (mit Details wie Gewicht, Sorte, etc.): Preis €<br>" +
        "\n<strong class=\"meta-info\">Gültig:</strong> [DD.MM.YYYY] bis [DD.MM.YYYY]<br>" +
        "\n<strong class=\"meta-info\">Supermarkt:</strong> [Supermarktname]" +
        "\n\n" +
        "3. Bei Preisvergleichen oder Zusammenfassungen, nutze einen abschließenden Absatz mit einer klaren Kennzeichnung: " +
        "\n**Preisvergleich:** Das günstigste Produkt ist X für Y € (Z € pro kg/Stück)." +
        "\n\n" +
        "4. Wenn ein gesuchtes Produkt nicht verfügbar ist, teile dies explizit mit: " +
        "\n**Hinweis:** Bei [Produkt] habe ich leider keine aktuellen Angebote bei [Supermarkt] gefunden." +
        "\n\n" +
        "5. Verwende fettgedruckten Text für Hervorhebungen der Struktur-Elemente wie oben gezeigt." +
        "6. WICHTIG: Setze nach JEDEM Element einen HTML-Zeilenumbruch mit <br>. Jedes Element (Produktname, Gültig vom, Supermarkt) MUSS auf einer eigenen Zeile stehen!" +
        "7. EXTREM WICHTIG: Verwende das explizite HTML-Tag <br> nach jeder Zeile, anstatt nur Markdown-Zeilenumbrüche, damit die Elemente klar voneinander getrennt angezeigt werden." +
        "\n\n" +
        "Beispiel: " +
        "\nJa, bei Aldi gibt es aktuell Kartoffeln und Nudeln im Angebot:\n" +
        "\n**Speisefrühkartoffeln** (1,5 kg): 2,79 €<br>" +
        "\n<strong class=\"meta-info\">Gültig:</strong> 24.04.2025 bis 26.04.2025<br>" +
        "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi" +
        "\n\n" +
        "**CUCINA NOBILE Farfalle Fantasia** (versch. Sorten, 250 g): 1,49 €<br>" +
        "\n<strong class=\"meta-info\">Gültig:</strong> 22.04.2025 bis 26.04.2025<br>" +
        "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi" +
        "\n\n" +
        "**Hinweis:** Bei Reis habe ich leider keine aktuellen Angebote bei Aldi gefunden."
        }
    ]

# Seitentitel mit Logo-Effekt
col1, col2 = st.columns([5, 1])
with col1:
    # Logo mit CSS-Klassen aus der externen Datei
    html_code = """
    <div class="logo-container">
        <span class="logo-main" style="font-size: 38px !important; font-weight: 800 !important; color: var(--text-color) !important;">🛒 SparFuchs</span>
        <span id="orange-text" style="font-size: 38px !important; color: #FF6600 !important; font-weight: 800 !important; display: inline-block !important; text-shadow: 0 0 1px #FF6600 !important; -webkit-text-stroke: 0.5px #FF6600 !important;">.de</span>
    </div>
    <p class="logo-subtitle">Dein KI-Assistent für Supermarkt-Angebote</p>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# Chat-Container mit verbessertem Erscheinungsbild
st.markdown('<div class="chat-container" style="margin-top: 5px; background-color: transparent !important;">', unsafe_allow_html=True)

# Chatverlauf anzeigen (nur user und assistant Nachrichten)
for message in [m for m in st.session_state.messages if m["role"] != "system"]:
    # Benutzerdefinierte Icons für user und assistant
    if message["role"] == "user":
        avatar = "⌨️"  # Tastatur für den Benutzer
    else:
        avatar = "🛒"  # Einkaufswagen für den Assistenten
    
    # Verwende die normale Streamlit-Chat-Komponente für beide Nachrichtentypen
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Initialisiere eine Key-Zähler-Variable, wenn sie noch nicht existiert
if "key_counter" not in st.session_state:
    st.session_state["key_counter"] = 0

# Initialisiere previous_input nur einmal beim Start der App
if "previous_input" not in st.session_state:
    st.session_state["previous_input"] = ""
    
# Initialisiere eine Variable, die anzeigt, ob es die erste Eingabe ist
if "is_first_input" not in st.session_state:
    st.session_state["is_first_input"] = True

# Initialisiere einen direkten Übermittlungsflag
if "submit_text" not in st.session_state:
    st.session_state["submit_text"] = None

# Textfeld-Container - nur eine Ebene von Spalten
textfield_cols = st.columns([1, 20, 3])  # Weniger leere Spalte links, breiteres Textfeld

# Placeholder für Spinner über dem Texteingabefeld
with textfield_cols[1]:
    # Platzhalter für Spinner festlegen
    spinner_placeholder = st.empty()

# Textfeld in der mittleren Spalte
with textfield_cols[1]:
    current_key = f"custom_chat_input_{st.session_state.key_counter}"
    initial_value = st.session_state.get("preset_input", "")
    user_input = st.text_area("Chat-Eingabe", value=initial_value, placeholder="Wonach suchst du? (Obst, Rezeptideen, Preisvergleiche, etc.. ) ", 
                          label_visibility="collapsed", key=current_key, height=95)
    
    # Verfolge Änderungen im Textfeld
    if user_input and st.session_state.get("last_input_value") != user_input:
        st.session_state["last_input_value"] = user_input
    
    # Preset-Wert nach Verwendung zurücksetzen
    if "preset_input" in st.session_state:
        # Setze den Text auch in last_input_value, um doppelte Verarbeitung zu vermeiden
        st.session_state["last_input_value"] = st.session_state.get("preset_input", "")
        del st.session_state.preset_input

# Button-Container - getrennte Spaltenreihe
button_cols = st.columns([3, 14, 3, 2])  # Weniger leere Spalte links

# Button in der zweiten Spalte statt der dritten für weniger Rechtsverschiebung
with button_cols[1]:
    # Wenn der Button geklickt wird, setze submit_text auf den aktuellen Wert von user_input
    if st.button("→", type="primary", use_container_width=True, 
            key=f"submit_button_{st.session_state.key_counter}"):
        if user_input and user_input.strip():
            st.session_state["submit_text"] = user_input.strip()
            st.rerun()
    
    # Reset-Button direkt unter dem Send-Button platzieren (nur wenn es AI-Antworten gibt)
    has_ai_responses = any(message["role"] == "assistant" for message in st.session_state.messages)
    if has_ai_responses:
        if st.button("🔄 Chat zurücksetzen", key="reset_chat", type="secondary", use_container_width=True):
            system_message = st.session_state.messages[0]
            st.session_state.messages = [system_message]
            st.rerun()

# Wenn ein Text zur Übermittlung oder ein Vorschlag ausgewählt wurde
submitted_text = st.session_state.get("submit_text")
if submitted_text:
    prompt = submitted_text
    
    # Zurücksetzen des Übermittlungsflags
    st.session_state["submit_text"] = None
    
    # Prüfe ob der Prompt nicht leer ist
    if not prompt:
        st.warning("Bitte gib eine Frage oder einen Suchbegriff ein.")
    else:
        # Markiere, dass die erste Eingabe verarbeitet wurde
        st.session_state["is_first_input"] = False
        
        # Speichern der aktuellen Eingabe für Vergleich beim nächsten Mal
        st.session_state["previous_input"] = prompt
        
        # Erhöhe den Key-Zähler, um beim nächsten Rendering ein leeres Eingabefeld zu erzeugen
        st.session_state["key_counter"] += 1
        
        # Benutzernachricht zum Verlauf hinzufügen
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        try:
            # Hole systemnachricht und kontext mit unserer neuen Methode
            system_prompt, context_message, products_context = process_query(prompt)
            
            # Erstelle die Nachrichtenliste mit garantierter Systemnachricht
            messages_with_context = [system_prompt, context_message]
            # Füge nur user und assistant Nachrichten hinzu
            messages_with_context.extend([m for m in st.session_state.messages if m["role"] != "system"])
            
            # Hier verwenden wir den vorbereiteten Platzhalter für den Spinner über dem Textfeld
            with spinner_placeholder:
                # Zeige nur unsere benutzerdefinierte Meldung ohne den Standard-Spinner
                st.markdown("""
                <div class="search-spinner-box">
                    <div class="loader-container">
                        <span class="search-icon">🔍</span> 
                        <span class="loading-text">Suche nach passenden Angeboten</span>
                        <span class="loading-dots">...</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gemini 2.0 Flash Experimental Modell verwenden
                model_variants = [
                    "google/gemini-2.0-flash-exp:free",  # Gemini 2.0 Flash Experimental (Free)
                ]
                
                success = False
                error_messages = []
                full_response = ""  # Initialisierung der Variable vor der Verwendung
                
                # Gib dem System mehr Zeit, um die Anfrage zu verarbeiten
                time.sleep(1.5)  # Erhöhte Verzögerung für bessere Stabilität
                
                for model_name in model_variants:
                    retry_count = 0
                    max_retries = 2
                    
                    while retry_count <= max_retries and not success:
                        try:
                            # Zusätzliche Verzögerung zwischen Versuchen
                            if retry_count > 0:
                                time.sleep(2)  # Längere Verzögerung bei weiteren Versuchen
                            
                            stream = client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {"role": m["role"], "content": m["content"]} 
                                    for m in messages_with_context
                                ],
                                extra_headers={
                                    "HTTP-Referer": "https://sparfuchs.streamlit.app/",
                                    "X-Title": "SparFuchs.de"
                                },
                                temperature=0.2,  # Leicht erhöhte Temperatur für bessere Antworten
                                max_tokens=4000,  # Erhöht, um vollständige Antworten zu ermöglichen
                                stream=True
                            )
                            
                            for chunk in stream:
                                content = chunk.choices[0].delta.content
                                if content is not None:
                                    full_response += content
                            
                            success = True
                            break  # Bei Erfolg Schleife beenden
                        except Exception as e:
                            error_messages.append(f"Fehler mit {model_name}: {str(e)}")
                            retry_count += 1
                            continue
                
                if not success:
                    # Debug-Modus aktivieren (in Produktion später entfernen oder durch Umgebungsvariable steuern)
                    debug_mode = True
                    
                    if debug_mode:
                        # Detaillierte Fehlermeldungen anzeigen
                        error_details = "\n\n".join(error_messages)
                        full_response = f"Entschuldigung, ich konnte Ihre Anfrage nicht bearbeiten. Technische Details:\n\n{error_details}"
                    else:
                        full_response = "Entschuldigung, ich konnte Ihre Anfrage nicht bearbeiten. Bitte versuchen Sie es später erneut."
            
            # Nach dem API-Aufruf den Spinner entfernen
            spinner_placeholder.empty()
            
        except Exception as e:
            full_response = "Entschuldigung, ein unerwarteter Fehler ist aufgetreten."
        
        # Überprüfe, ob die Antwort halluzinierte Produkte enthält
        df = load_csv_data()
        
        # Prüfe, ob es sich um eine Kategorie-Anfrage handelt
        is_category_query = False
        kategorie_begriffe = ["getränke", "obst", "gemüse", "lebensmittel", "produkte", "angebote", "tiefkühlkost", 
                              "backwaren", "milchprodukte", "fleisch", "wurst", "kategorie", "alle"]
        
        produkt_begriffe = ["rum", "vodka", "whiskey", "whisky", "bier", "wein", "sekt", "chips", "schokolade", "kaffee", 
                           "nudeln", "reis", "milch", "käse", "joghurt", "fleisch", "wurst", "gemüse", "obst",
                           "cola", "fanta", "sprite", "limonade", "wasser", "havana"]
        
        is_product_query = False
        for begriff in produkt_begriffe:
            if begriff in prompt.lower():
                is_product_query = True
                break
        
        for begriff in kategorie_begriffe:
            if begriff in prompt.lower():
                is_category_query = True
                break
        
        # Wenn es eine Kategorie-Anfrage oder Produktanfrage ist und keine offensichtlichen Fehler vorliegen, 
        # überspringen wir die Halluzinationsprüfung
        if (is_category_query or is_product_query) and not ("kein" in full_response.lower() and "nicht" in full_response.lower()):
            # Halluzinationsprüfung überspringen
            pass
        else:
            if detect_hallucinations(full_response, df):
                # Ersetze die Antwort durch eine Warnung
                full_response = (
                    "Entschuldigung, ich kann zu dieser Anfrage keine genauen Informationen finden. "
                    "Ich kann nur Informationen zu Produkten geben, die tatsächlich in den aktuellen Angeboten von Aldi und Lidl vorhanden sind.\n\n"
                    "**Hinweis:** Bitte versuchen Sie eine andere Anfrage zu Produkten, die in den aktuellen Angeboten enthalten sein könnten."
                )
        
        # Nur erfolgreiche Antworten zum Verlauf hinzufügen
        if full_response:
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        
        # Eingabefeld zurücksetzen
        st.session_state["input_value"] = ""
            
        # Nach der Antwortgenerierung die Seite neu laden, um den aktualisierten Chat anzuzeigen
        st.rerun()

# Wenn der Chat noch leer ist, zeige Prompt-Vorschläge an
if len([m for m in st.session_state.messages if m["role"] != "system"]) == 0:
    st.markdown("<h3 style='margin-top: 30px; text-align: center; color: #2A2A2A; font-size: 18px;'>👋 Willkommen! Hier sind einige Vorschläge:</h3>", unsafe_allow_html=True)
    
    # Neue Methode ohne JavaScript-Abhängigkeit
    col1, col2 = st.columns(2)
    
    with col1:
        display_suggestions_row([
            ("Wo ist Coca Cola im Angebot?", "🔍"),
            ("Wo ist diese Woche Hackfleisch am günstigsten?", "🥩")
        ])
        
    with col2:        
        display_suggestions_row([
             ("Welche Obst Angebote gibt es aktuell bei Aldi?", "🍎"),
            ("Gibt es bei Aldi Reis, Nudeln oder Kartoffeln im Angebot?", "🔍")
            
        ])

# Zusätzliche Ideen für Anfänger unten anzeigen
if len([m for m in st.session_state.messages if m["role"] != "system"]) <= 2:
    st.markdown("<p style='margin-top: 20px; text-align: center; font-size: 14px; color: #666666;'>Du kannst mich auch fragen:</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[2]:
        if st.button("💰 Welche Backwaren sind bei Lidl im Angebot?", type="secondary", use_container_width=True):
            st.session_state.preset_input = "Welche Backwaren sind bei Lidl im Angebot?"
            st.session_state.submit_text = "Welche Backwaren sind bei Lidl im Angebot?"
            st.rerun()
    with cols[0]:
        if st.button("🥗 Gib mir 10 vegetarische Produkte, hauptsächlich bitte Gemüse", type="secondary", use_container_width=True):
            st.session_state.preset_input = "Gib mir 10 vegetarische Produkte, hauptsächlich bitte Gemüse"
            st.session_state.submit_text = "Gib mir 10 vegetarische Produkte, hauptsächlich bitte Gemüse"
            st.rerun()
    with cols[1]:
        if st.button("⚖️ Vergleiche Äpfel und Orangen", type="secondary", use_container_width=True):
            st.session_state.preset_input = "Vergleiche Äpfel und Orangen"
            st.session_state.submit_text = "Vergleiche Äpfel und Orangen"
            st.rerun()
    

# Kleine Info am Seitenende für Mobilgeräte
st.markdown(
    "<div class='app-footer'>© SparFuchs.de • AI Agent Made in Germany</div>",
    unsafe_allow_html=True
)

