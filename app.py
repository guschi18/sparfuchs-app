import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import random
import time
from datetime import datetime, timedelta
import re

# Umgebungsvariablen laden
load_dotenv()

# OpenAI Client konfigurieren (für OpenRouter)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"  # OpenRouter API-Basis-URL
)

# CSS für modernes Design
def apply_modern_supermarket_style():
    # Kritisches CSS (minimale Stile für das anfängliche Rendering)
    critical_css = """
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    :root{--text-color:#2A2A2A;--bg-color:#FDFDFD;--primary:#28A745;--secondary:#FF6600;--border:#E0E0E0}
    html,body,.stApp,[class*="css"]{font-family:'Poppins',sans-serif;color:var(--text-color);background-color:var(--bg-color)!important}
    """

    # Restliches minimiertes CSS laden
    try:
        with open("static/styles.min.css", "r") as f:
            minified_css = f.read()
    except FileNotFoundError:
        # Fallback auf inline CSS, wenn die Datei nicht existiert
        minified_css = get_minified_css()

    # Stile anwenden
    st.markdown(f"<style>{critical_css}{minified_css}</style>", unsafe_allow_html=True)

# Funktion, die minimiertes CSS als Fallback bereitstellt
def get_minified_css():
    return """footer,[data-testid="InputFooterHelperText"],[data-testid="InputInstructions"],[data-testid="InputHelpText"],[data-testid="stChatInputFooter"],.streamlit-footer,.stTextInput+div small,.stTextInput+small,.stTextInput~small,small.st-emotion-cache-16txtl3,.st-emotion-cache-16txtl3{display:none!important;visibility:hidden!important;height:0!important;padding:0!important;margin:0!important;opacity:0!important}[data-testid="stForm"] [data-baseweb="input"] div,.stChatInput div,.stChatInput,[data-testid="stChatInput"]{margin-bottom:0!important}.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlock"],.stApp>header,.stApp>[class*='block-container']{background-color:#FDFDFD!important}[data-testid="stChatInput"]{border-radius:10px!important;overflow:hidden!important;background-color:#FFF!important;border:1px solid #E0E0E0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05)!important;display:flex!important}[data-testid="stChatInput"]>div{background-color:#FFF!important;flex-grow:1!important}[data-testid="stChatInput"] input{color:#2A2A2A!important;background-color:#FFF!important;padding-left:15px!important;border:none!important}[data-testid="stChatInput"] input::placeholder{color:#BBB!important}[data-testid="stChatInput"] button,[data-testid="stChatInput"] [data-testid="baseButton-primaryFormSubmit"]{background-color:#2A2A2A!important;border-radius:0 10px 10px 0!important;color:white!important;min-width:50px!important;height:100%!important;padding:10px!important;border:none!important}[data-testid="stChatInput"] button:hover,[data-testid="stChatInput"] [data-testid="baseButton-primaryFormSubmit"]:hover{background-color:#28A745!important;border:none!important}[data-testid="stChatInput"] button svg,[data-testid="stChatInput"] [data-testid="baseButton-primaryFormSubmit"] svg{fill:white!important;color:white!important}.chat-container{background-color:#FDFDFD!important;border-radius:10px!important}[data-testid="baseButton-secondary"]{background-color:#F8F9FA!important;border:1px solid #E0E0E0!important;border-radius:10px!important;color:#2A2A2A!important;font-size:14px!important;box-shadow:none!important}h1,h2,h3,h4{font-weight:600!important;color:#2A2A2A!important}h1{font-size:26px!important;margin-bottom:20px!important}.main .block-container{padding:25px;max-width:700px;margin:0 auto;background:transparent}.stChatMessage{background:#FFF!important;border-radius:10px!important;padding:18px!important;border:1px solid #E0E0E0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05);margin-bottom:20px!important;color:#000!important;transition:all 0.3s ease}.stChatMessage:hover{box-shadow:0 4px 8px rgba(0,0,0,0.1)}.stChatMessage.user{background:#F5F8FF!important;border:1px solid #E0E8FF!important;color:#000!important}.stMarkdown{color:#000!important}.stMarkdown p,.stMarkdown li,.stMarkdown div,.stMarkdown code{color:#000!important;font-weight:500!important}[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]>p,[data-testid="stChatMessage"] .stMarkdown>p{color:#000!important;font-weight:500!important;font-size:16px!important;line-height:1.6!important;margin-bottom:12px!important}.stChatMessage p,.stChatMessage span,.stChatMessage div,.stChatMessage li,.stChatMessage a,.stChatMessage code{color:#000!important;font-weight:500!important}[data-testid="stChatMessageContent"],[data-testid="stChatMessageContent"] *{color:#000!important;font-weight:500!important}[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] span,[data-testid="stMarkdownContainer"] div,[data-testid="stMarkdownContainer"] li,[data-testid="stMarkdownContainer"] a,[data-testid="stMarkdownContainer"] code,[data-testid="stMarkdownContainer"] *{color:#000!important;font-weight:500!important}.main .block-container [data-testid="stChatMessage"] *,.main .block-container [data-testid="stChatMessageContent"] *,.element-container .stMarkdownContainer p,.element-container .stMarkdownContainer span{color:#000!important;font-weight:500!important}[data-testid="stChatMessage"]{background-color:#FFF!important;border:1px solid #E0E0E0!important}[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]{color:#000!important}[data-testid="stSidebar"]{background:#FFF;border-right:1px solid #E0E0E0!important}[data-testid="stSidebar"] h2{color:#2A2A2A;font-size:20px!important;margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid #E0E0E0}button[kind="primary"]{background:#34C759!important;border-radius:10px!important;padding:8px 16px!important;border:none!important;color:white!important;font-weight:500!important;box-shadow:0 2px 5px rgba(52,199,89,0.3)!important;transition:all 0.3s ease!important}button[kind="primary"]:hover{transform:translateY(-2px);background:#28A745!important;box-shadow:0 4px 8px rgba(52,199,89,0.4)!important}button[kind="secondary"]{background:#FFF!important;border-radius:10px!important;padding:8px 16px!important;border:none!important;color:white!important;font-weight:500!important;box-shadow:0 2px 5px rgba(255,102,0,0.3)!important;transition:all 0.3s ease!important}button[kind="secondary"]:hover{transform:translateY(-2px);background:#E55C00!important;box-shadow:0 4px 8px rgba(255,102,0,0.4)!important}.stAlert{border-radius:10px!important;border:1px solid #E0E0E0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05)!important;background-color:#FFF!important}.logo-text{font-size:38px!important;font-weight:700!important;color:#2A2A2A!important;display:inline-block!important;margin-bottom:8px!important;line-height:1.2!important}.logo-highlight{color:#FF6600!important;font-weight:inherit!important}.chat-reset-button{border-radius:10px;background-color:#f8f9fa;border:1px solid #E0E0E0;color:#2A2A2A;padding:8px 12px;text-align:center;text-decoration:none;font-size:14px;cursor:pointer;transition:all 0.3s ease}.chat-reset-button:hover{background-color:#e9ecef;border-color:#ced4da}.prompt-suggestion{background:#FFF;border-radius:8px;padding:10px 15px;margin:10px 5px;border:1px solid #E0E0E0;cursor:pointer;transition:all 0.3s ease;color:#121111;display:inline-block;box-shadow:0 2px 5px rgba(0,0,0,0.05);animation:fadeIn 0.5s ease}.prompt-suggestion:hover{background:#E6F9E6;border-color:#C5E8C5;transform:scale(1.05);box-shadow:0 4px 8px rgba(0,0,0,0.1)}.prompt-icon{color:#28A745;margin-right:5px;font-size:16px;transform:scale(1);transition:transform 0.3s ease}.prompt-suggestion:hover .prompt-icon{transform:scale(1.1)}@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}@media (max-width:768px){.main .block-container{padding:15px}h1{font-size:22px!important;margin-bottom:15px!important}.logo-text{font-size:22px}.prompt-suggestion{max-width:100%;font-size:14px;padding:10px}.stChatMessage{padding:15px!important}button[kind="primary"]{padding:10px!important}}[data-testid="stTextArea"]{border:1px solid #E0E0E0!important;border-radius:10px!important;background-color:#FFF!important;padding:0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05)!important}[data-testid="stTextArea"]>div{background-color:#FFF!important}[data-testid="stTextArea"] textarea{padding:12px 15px!important;font-size:14px!important;color:#0d0d0c!important;background-color:#FFF!important;min-height:100px!important;resize:vertical!important;font-size:18px!important;font-weight:500!important}[data-testid="stTextArea"] textarea::placeholder{color:#0d0d0c!important;font-size:18px!important;font-weight:500!important}[data-testid="stTextArea"]:focus-within{border-color:#34C759!important;box-shadow:0 0 0 1px #34C759!important;outline:none!important}[data-testid="stTextArea"] textarea:focus{box-shadow:none!important;outline:none!important;border-color:transparent!important}[data-testid="stForm"] [data-baseweb="textarea"]:focus-within,[data-baseweb="textarea"]:focus,[data-baseweb="textarea"]:focus-within,[data-baseweb="base-input"]:focus,[data-baseweb="base-input"]:focus-within{border-color:#34C759!important;box-shadow:0 0 0 1px #34C759!important;outline-color:#34C759!important}:focus{outline-color:#34C759!important}textarea:focus{border-color:#34C759!important;box-shadow:0 0 0 1px #34C759!important;outline-color:#34C759!important}[data-testid="baseButton-primary"]{margin-top:10px!important;height:45px!important;font-size:24px!important;background-color:#34C759!important;border-radius:10px!important;color:white!important;padding:0!important;border:none!important;box-shadow:0 2px 5px rgba(52,199,89,0.3)!important;max-width:100%!important}[data-testid="baseButton-primary"]:hover{background-color:#28A745!important;box-shadow:0 4px 8px rgba(52,199,89,0.4)!important}[data-testid="baseButton-secondary"]{margin-top:10px!important;max-width:100%!important}.stTextArea{max-width:100%!important}"""

# Eine neue Datei mit dem minimierten CSS erstellen
def create_minified_css_file():
    # Sicherstellen, dass das static-Verzeichnis existiert
    import os
    if not os.path.exists("static"):
        os.makedirs("static")

    # Das minimierte CSS in eine Datei schreiben
    with open("static/styles.min.css", "w") as f:
        f.write(get_minified_css())

    print("Minimierte CSS-Datei wurde unter static/styles.min.css erstellt")

# Beispielprodukte hinzufügen falls keine CSV-Datei vorhanden ist
def create_sample_data():
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
    context += "- 'Nudeln' umfasst auch Pasta, Tortelloni, Farfalle, Spaghetti, und andere Pasta-Varianten - jegliche Art von Pasta ist eine Form von Nudeln.\n"
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

# Prompt-Vorschläge erstellen und anzeigen
def display_prompt_suggestion(text, icon="✨"):
    # Erstelle einen Button mit dem Vorschlagstext
    button_id = f"suggestion_{hash(text)}"
    
    # Erstelle HTML mit stilvollem Button ohne JavaScript
    html = f"""
    <div class="prompt-suggestion-container">
        <button class="prompt-suggestion" id="{button_id}">
            <span class="prompt-icon">{icon}</span> {text}
        </button>
    </div>
    """
    
    # Füge den Button als HTML hinzu
    st.markdown(html, unsafe_allow_html=True)
    
    # Füge den regulären Streamlit-Button hinzu, aber mache ihn unsichtbar
    # Dieser dient nur dazu, die Aktion auszulösen
    if st.button(text, key=button_id, label_visibility="collapsed"):
        # Text ins Textfeld kopieren UND direkt Anfrage senden
        st.session_state.preset_input = text
        st.session_state.submit_text = text
        # Löse Rerun aus, um die Verarbeitung zu starten
        st.rerun()
    
    # CSS für die Buttons (anstelle von JavaScript)
    st.markdown("""
    <style>
    /* Verstecke die eigentlichen Streamlit-Buttons */
    [data-testid="baseButton-secondary"] {
        display: none !important;
    }
    
    /* Style für die Button-Container */
    .prompt-suggestion-container {
        display: inline-block;
        margin: 5px;
        background: #FFFFFF;
    }
    
    /* Style für die Prompt-Suggestion-Buttons */
    .prompt-suggestion {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 10px 15px;
        border: 1px solid #E0E0E0;
        cursor: pointer;
        transition: all 0.3s ease;
        color: #121111;
        display: inline-block;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        animation: fadeIn 0.5s ease;
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
        font-size: 14px;
    }
    
    .prompt-suggestion:hover {
        background: #E6F9E6;
        border-color: #C5E8C5;
        transform: scale(1.05);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    .prompt-icon {
        color: #28A745;
        margin-right: 5px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)

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

# Streamlit Seitenkonfiguration
st.set_page_config(
    page_title="SparFuchs.de", 
    page_icon="🛒",
    layout="centered"
)

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
    # Ein komplett neuer Ansatz mit verschiedenen Styles und mehreren Techniken
    html_code = """
    <div style="margin-bottom: 0px; display: flex; align-items: center;">
        <span style="font-size: 38px; font-weight: 700; color: #2A2A2A; text-shadow: 0 0 1px #2A2A2A; letter-spacing: -0.02em;">🛒 SparFuchs</span>
        <span id="orange-text" style="font-size: 38px; font-weight: 700; color: #FF6600 !important; text-shadow: 0 0 1px #FF6600; letter-spacing: -0.02em;" color="#FF6600">.de</span>
    </div>
    <style>
        #orange-text {
            color: #FF6600 !important;
            font-weight: 700 !important;
            -webkit-text-stroke: 0.3px #FF6600;
        }
    </style>
    <p style="font-size: 18px; color: #666666; margin-bottom: 0px; margin-top: 0px;">Dein KI-Assistent für Supermarkt-Angebote</p>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# Chat-Container mit verbessertem Erscheinungsbild
st.markdown('<div class="chat-container" style="margin-top: 5px;">', unsafe_allow_html=True)

# Chatverlauf anzeigen (nur user und assistant Nachrichten)
for message in [m for m in st.session_state.messages if m["role"] != "system"]:
    # Benutzerdefinierte Icons für user und assistant
    if message["role"] == "user":
        avatar = "⌨️"  # Tastatur für den Benutzer
    else:
        avatar = "🛒"  # Einkaufswagen für den Assistenten
    
    with st.chat_message(message["role"], avatar=avatar):
        # Text mit aktiviertem Markdown für Formatierungen
        st.markdown(message["content"], unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Container für den Reset-Button und chat_input
chat_container = st.container()

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

# CSS-Styling für verschobenes Layout und verringerter Abstand zum Titel
st.markdown("""
<style>
    /* Container-Styling */
    .stTextArea {
        max-width: 100% !important;
    }
    
    /* Verbesserter fett formatierter Text in den Chat-Nachrichten */
    [data-testid="stChatMessage"] strong,
    [data-testid="stMarkdownContainer"] strong,
    .stMarkdown strong {
        color: #28A745 !important;
        font-weight: 700 !important;
    }
    
    /* Metainformationen - Gültig vom und Supermarkt */
    [data-testid="stChatMessage"] strong.meta-info,
    [data-testid="stMarkdownContainer"] strong.meta-info,
    .stMarkdown strong.meta-info {
        color: #000 !important;
        font-weight: 700 !important;
    }
    
    /* Zusätzlicher Abstand nach den Produktinformationen */
    [data-testid="stChatMessage"] p {
        margin-bottom: 6px !important;
    }
    
    /* Primary Button (Senden-Button) */
    [data-testid="baseButton-primary"] {
        margin-top: 10px !important;
        height: 45px !important;
        font-size: 24px !important;
        background-color: #28A745 !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(40, 167, 69, 0.3) !important;
        max-width: 100% !important;
    }
    
    [data-testid="baseButton-primary"]:hover {
        background-color: #218838 !important;
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.4) !important;
    }
    
    /* Secondary Button (Reset-Button) */
    [data-testid="baseButton-secondary"] {
        margin-top: 10px !important;
        max-width: 100% !important;
    }
    
    /* Verringerter Abstand für Titel und Untertitel */
    .main .block-container {
        padding-top: 0rem !important;
    }
    
    h1, p {
        margin-bottom: 0rem !important;
    }
    
    /* Abstand zwischen Elementen generell verringern */
    .element-container {
        margin-bottom: 0rem !important;
    }
    
    /* Abstand vor dem Texteingabefeld verringern */
    div[data-testid="column"]:has(.stTextArea) {
        margin-top: 0rem !important;
    }
    
    /* Aggressivere Reduzierung der Abstände */
    .main > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Spezifischer Selektor für den Container des Titels */
    .main .block-container > div:first-child {
        margin-bottom: 0 !important;
    }
    
    /* Container für Spalten nach dem Titel */
    .main .block-container > div:nth-child(2) {
        margin-top: 0 !important;
    }
    
    /* Generelles Padding für den Hauptcontainer entfernen */
    .main .block-container {
        padding: 0 25px !important;
    }
    
    /* AppView Container Padding entfernen */
    [data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
    }
    
    /* Mobile Anpassungen */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
            margin-top: -20px !important;
        }

        h1 {
            font-size: 22px !important;
            margin-top: 0 !important;
            margin-bottom: 5px !important;
        }

        .logo-text {
            font-size: 22px;
            margin-top: 0 !important;
        }

        /* Den gesamten Header nach oben verschieben */
        .main > div:first-child {
            margin-top: -20px !important;
            padding-top: 0 !important;
        }
        
        /* Streamlit Hauptcontainer noch weiter nach oben verschieben */
        [data-testid="stAppViewContainer"] {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Block-Container nach oben verschieben */
        .stApp > [class*='block-container'] {
            padding-top: 0 !important;
            margin-top: 0 !important;
        }

        /* Weniger Abstand zwischen Header und Inhalt */
        .main .block-container > div:first-child {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Abstand zwischen Textfeld und KI-Antwort verringern */
        .stChatMessage {
            margin-bottom: 0 !important;
            padding: 8px !important;
        }
        
        /* Extrem reduzierte Abstände zwischen allen Elementen */
        .element-container {
            margin-bottom: 0 !important;
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        
        /* Chat zurücksetzen Button weniger Abstand */
        [data-testid="baseButton-secondary"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            height: auto !important;
            padding: 5px !important;
        }
        
        /* Abstand zwischen Chat zurücksetzen und grünem Button */
        [data-testid="baseButton-secondary"] + div {
            margin-top: 0 !important;
        }
        
        /* Abstand vor "Du kannst mich auch fragen" reduzieren */
        p[style*="text-align: center"] {
            margin-top: 15px !important;
            margin-bottom: 5px !important;
        }
        
        /* Verkleinere den Abstand zwischen den Buttons/Vorschlägen */
        button[type="secondary"] {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
            padding: 5px !important;
        }
        
        /* Container für die Vorschläge kompakter */
        .prompt-suggestion {
            margin: 2px !important;
            padding: 5px 8px !important;
        }
        
        /* Verringere den Abstand nach dem Texteingabefeld */
        [data-testid="stTextArea"] {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        /* Grüner Button weniger Abstand nach oben */
        [data-testid="baseButton-primary"] {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            height: 40px !important;
        }
        
        /* Abstand für Spalten reduzieren */
        [data-testid="column"] {
            padding: 0 !important;
            gap: 0 !important;
        }
        
        /* Chat-Nachrichten kompakter machen */
        [data-testid="stChatMessageContent"] {
            padding: 3px !important;
        }
        
        /* Chat-Container Abstände reduzieren */
        .chat-container {
            margin: 0 !important;
            padding: 0 !important;
        }
        
        /* Abstände zwischen allen Chat-Elementen minimieren */
        [data-testid="stChatInput"] {
            margin: 0 !important;
        }
        
        /* Fußzeile kompakter machen */
        div[style*="position: fixed; bottom"] {
            bottom: 2px !important;
        }
        
        /* Alle Abstände zwischen Elementen minimieren */
        div, p, span, section {
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }
        
        /* Speziell für den Abstand zwischen letzter KI-Antwort und Textfeld */
        .stChatMessage + div {
            margin-top: -5px !important;
        }
        
        /* Für die Positionierung des Chat zurücksetzen Buttons direkt unter dem grünen Button */
        /* Verstecke regulären Abstand */
        #reset_chat, [data-testid="baseButton-secondary"] {
            margin-top: -5px !important;
            position: relative !important;
            z-index: 10 !important;
        }
        
        /* Container für Reset-Button */
        #reset_chat {
            margin-top: 0 !important;
        }
        
        /* Die Container der Buttons besser positionieren */
        button#reset_chat {
            margin-top: 0 !important;
        }
        
        /* Für bessere Ausrichtung des grünen Buttons und Reset-Buttons */
        [data-testid="baseButton-primary"] + div, 
        [id="reset_chat"] {
            margin-top: 0 !important;
        }
        
        /* VERBESSERT: Abstand zwischen Untertitel und Textfeld verringern */
        /* Direktere Selektoren, die auf die Streamlit-Struktur abzielen */
        .main .block-container > div:nth-child(1) {
            margin-bottom: -25px !important;
        }
        
        /* VERBESSERT: Abstände zwischen Texteingabe und vorigen Elementen */
        .stTextArea {
            margin-top: -15px !important;
        }
        
        /* Abstand zwischen Logo und erstem Element reduzieren */
        .main .block-container > div:first-child + div {
            margin-top: -10px !important;
        }
        
        /* VERBESSERT: Abstand vom grünen Button zu Willkommenstext verringern */
        h3[style*="text-align: center"] {
            margin-top: -20px !important;
        }
        
        /* VERBESSERT: Den Willkommenstext und die Vorschläge näher zum grünen Button bringen */
        [data-testid="baseButton-primary"] + div + div h3,
        [data-testid="baseButton-primary"] ~ h3 {
            margin-top: -20px !important;
            padding-top: 0 !important;
        }
        
        /* Aggressivere Reduzierung aller Abstände zwischen allen Elementen */
        .element-container + .element-container {
            margin-top: -10px !important;
        }
        
        /* Willkommenstext und Vorschläge extrem nah am grünen Button */
        .element-container:has([data-testid="baseButton-primary"]) + .element-container {
            margin-top: -20px !important;
        }
        
        /* NEU: Abstand zwischen "Suche nach passenden Angeboten..." und dem Textfeld */
        div:has(> div > .stChatInput),
        div:has(> span:contains("Suche nach")),
        div[class*="stChatMessageContent"],
        .stAlert,
        div[data-testid="stChatInput"] {
            margin-bottom: 10px !important;
        }
        
        /* Sicherstellen, dass der Abstand vor dem Textfeld erhalten bleibt */
        .stTextArea {
            margin-top: 10px !important; 
        }
    </style>
    """, unsafe_allow_html=True)

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
    user_input = st.text_area("Chat-Eingabe", value=initial_value, placeholder="Was möchtest du kaufen? (z.B. Obst, Nudeln, Fleisch, etc...)", 
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
        
        # AI-Antwort generieren
        message_placeholder = st.empty()
        full_response = ""
        
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
                <div style="text-align: center; margin-bottom: 12px; font-weight: bold; color: #FF6600; 
                            background-color: #FFF8F0; padding: 8px; border-radius: 8px; 
                            border: 1px solid #FFE0C0; box-shadow: 0 2px 4px rgba(255, 102, 0, 0.1);">
                    <div class="loader-container">
                        <span style="margin-right: 8px;">🔍</span> 
                        <span class="loading-text">Suche nach passenden Angeboten</span>
                        <span class="loading-dots">...</span>
                    </div>
                </div>
                <style>
                    @keyframes pulse {
                        0% { opacity: 0.8; }
                        50% { opacity: 1; }
                        100% { opacity: 0.8; }
                    }
                    .loader-container {
                        display: inline-flex;
                        align-items: center;
                    }
                    .loading-text, .loading-dots {
                        animation: pulse 1.5s infinite;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                # Gemini 2.0 Flash Experimental Modell verwenden
                model_variants = [
                    "google/gemini-2.0-flash-exp:free",  # Gemini 2.0 Flash Experimental (Free)
                ]
                
                success = False
                error_messages = []
                
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
    with cols[1]:
        if st.button("💰 Welche Backwaren sind bei Lidl im Angebot?", type="secondary"):
            st.session_state.preset_input = "Welche Backwaren sind bei Lidl im Angebot?"
            st.session_state.submit_text = "Welche Backwaren sind bei Lidl im Angebot?"
            st.rerun()
    with cols[0]:
        if st.button("🥗 Gib mir 10 vegetarische Produkte, hauptsächlich bitte Gemüse", type="secondary"):
            st.session_state.preset_input = "Gib mir 10 vegetarische Produkte, hauptsächlich bitte Gemüse"
            st.session_state.submit_text = "Gib mir 10 vegetarische Produkte, hauptsächlich bitte Gemüse"
            st.rerun()
    with cols[2]:
        if st.button("⚖️ Vergleiche Äpfel und Orangen", type="secondary"):
            st.session_state.preset_input = "Vergleiche Äpfel und Orangen"
            st.session_state.submit_text = "Vergleiche Äpfel und Orangen"
            st.rerun()
    

# Kleine Info am Seitenende für Mobilgeräte
st.markdown(
    "<div style='position: fixed; bottom: 10px; left: 0; width: 100%; text-align: center; font-size: 12px; color: #999999;'>"
    "© SparFuchs.de • AI Agent Made in Germany"
    "</div>",
    unsafe_allow_html=True
)

