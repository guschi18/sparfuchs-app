import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd
import random
import time
from datetime import datetime, timedelta

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
    :root{--text-color:#2A2A2A;--bg-color:#FDFDFD;--primary:#34C759;--secondary:#FF6600;--border:#E0E0E0}
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
    return """footer,[data-testid="InputFooterHelperText"],[data-testid="InputInstructions"],[data-testid="InputHelpText"],[data-testid="stChatInputFooter"],.streamlit-footer,.stTextInput+div small,.stTextInput+small,.stTextInput~small,small.st-emotion-cache-16txtl3,.st-emotion-cache-16txtl3{display:none!important;visibility:hidden!important;height:0!important;padding:0!important;margin:0!important;opacity:0!important}[data-testid="stForm"] [data-baseweb="input"] div,.stChatInput div,.stChatInput,[data-testid="stChatInput"]{margin-bottom:0!important}.stApp,[data-testid="stAppViewContainer"],[data-testid="stAppViewBlock"],.stApp>header,.stApp>[class*='block-container']{background-color:#FDFDFD!important}[data-testid="stChatInput"]{border-radius:10px!important;overflow:hidden!important;background-color:#FFF!important;border:1px solid #E0E0E0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05)!important;display:flex!important}[data-testid="stChatInput"]>div{background-color:#FFF!important;flex-grow:1!important}[data-testid="stChatInput"] input{color:#2A2A2A!important;background-color:#FFF!important;padding-left:15px!important;border:none!important}[data-testid="stChatInput"] input::placeholder{color:#BBB!important}[data-testid="stChatInput"] button,[data-testid="stChatInput"] [data-testid="baseButton-primaryFormSubmit"]{background-color:#2A2A2A!important;border-radius:0 10px 10px 0!important;color:white!important;min-width:50px!important;height:100%!important;padding:10px!important;border:none!important}[data-testid="stChatInput"] button:hover,[data-testid="stChatInput"] [data-testid="baseButton-primaryFormSubmit"]:hover{background-color:#28A745!important;border:none!important}[data-testid="stChatInput"] button svg,[data-testid="stChatInput"] [data-testid="baseButton-primaryFormSubmit"] svg{fill:white!important;color:white!important}.chat-container{background-color:#FDFDFD!important;border-radius:10px!important}[data-testid="baseButton-secondary"]{background-color:#F8F9FA!important;border:1px solid #E0E0E0!important;border-radius:10px!important;color:#2A2A2A!important;font-size:14px!important;box-shadow:none!important}h1,h2,h3,h4{font-weight:600!important;color:#2A2A2A!important}h1{font-size:26px!important;margin-bottom:20px!important}.main .block-container{padding:25px;max-width:700px;margin:0 auto;background:transparent}.stChatMessage{background:#FFF!important;border-radius:10px!important;padding:18px!important;border:1px solid #E0E0E0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05);margin-bottom:20px!important;color:#000!important;transition:all 0.3s ease}.stChatMessage:hover{box-shadow:0 4px 8px rgba(0,0,0,0.1)}.stChatMessage.user{background:#F5F8FF!important;border:1px solid #E0E8FF!important;color:#000!important}.stMarkdown{color:#000!important}.stMarkdown p,.stMarkdown li,.stMarkdown div,.stMarkdown code{color:#000!important;font-weight:500!important}[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]>p,[data-testid="stChatMessage"] .stMarkdown>p{color:#000!important;font-weight:500!important;font-size:16px!important;line-height:1.6!important;margin-bottom:12px!important}.stChatMessage p,.stChatMessage span,.stChatMessage div,.stChatMessage li,.stChatMessage a,.stChatMessage code{color:#000!important;font-weight:500!important}[data-testid="stChatMessageContent"],[data-testid="stChatMessageContent"] *{color:#000!important;font-weight:500!important}[data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] span,[data-testid="stMarkdownContainer"] div,[data-testid="stMarkdownContainer"] li,[data-testid="stMarkdownContainer"] a,[data-testid="stMarkdownContainer"] code,[data-testid="stMarkdownContainer"] *{color:#000!important;font-weight:500!important}.main .block-container [data-testid="stChatMessage"] *,.main .block-container [data-testid="stChatMessageContent"] *,.element-container .stMarkdownContainer p,.element-container .stMarkdownContainer span{color:#000!important;font-weight:500!important}[data-testid="stChatMessage"]{background-color:#FFF!important;border:1px solid #E0E0E0!important}[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"]{color:#000!important}[data-testid="stSidebar"]{background:#FFF;border-right:1px solid #E0E0E0!important}[data-testid="stSidebar"] h2{color:#2A2A2A;font-size:20px!important;margin-bottom:20px;padding-bottom:10px;border-bottom:1px solid #E0E0E0}button[kind="primary"]{background:#34C759!important;border-radius:10px!important;padding:8px 16px!important;border:none!important;color:white!important;font-weight:500!important;box-shadow:0 2px 5px rgba(52,199,89,0.3)!important;transition:all 0.3s ease!important}button[kind="primary"]:hover{transform:translateY(-2px);background:#28A745!important;box-shadow:0 4px 8px rgba(52,199,89,0.4)!important}button[kind="secondary"]{background:#FFF!important;border-radius:10px!important;padding:8px 16px!important;border:none!important;color:white!important;font-weight:500!important;box-shadow:0 2px 5px rgba(255,102,0,0.3)!important;transition:all 0.3s ease!important}button[kind="secondary"]:hover{transform:translateY(-2px);background:#E55C00!important;box-shadow:0 4px 8px rgba(255,102,0,0.4)!important}.stAlert{border-radius:10px!important;border:1px solid #E0E0E0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05)!important;background-color:#FFF!important}.logo-text{font-size:38px!important;font-weight:700!important;color:#2A2A2A!important;display:inline-block!important;margin-bottom:8px!important;line-height:1.2!important}.logo-highlight{color:#FF6600!important;font-weight:inherit!important}.chat-reset-button{border-radius:10px;background-color:#f8f9fa;border:1px solid #E0E0E0;color:#2A2A2A;padding:8px 12px;text-align:center;text-decoration:none;font-size:14px;cursor:pointer;transition:all 0.3s ease}.chat-reset-button:hover{background-color:#e9ecef;border-color:#ced4da}.prompt-suggestion{background:#FFF;border-radius:8px;padding:10px 15px;margin:10px 5px;border:1px solid #E0E0E0;cursor:pointer;transition:all 0.3s ease;color:#121111;display:inline-block;box-shadow:0 2px 5px rgba(0,0,0,0.05);animation:fadeIn 0.5s ease}.prompt-suggestion:hover{background:#E6F9E6;border-color:#C5E8C5;transform:scale(1.05);box-shadow:0 4px 8px rgba(0,0,0,0.1)}.prompt-icon{color:#34C759;margin-right:5px;font-size:16px;transform:scale(1);transition:transform 0.3s ease}.prompt-suggestion:hover .prompt-icon{transform:scale(1.1)}@keyframes fadeIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}@media (max-width:768px){.main .block-container{padding:15px}h1{font-size:22px!important;margin-bottom:15px!important}.logo-text{font-size:22px}.prompt-suggestion{max-width:100%;font-size:14px;padding:10px}.stChatMessage{padding:15px!important}button[kind="primary"]{padding:10px!important}}[data-testid="stTextArea"]{border:1px solid #E0E0E0!important;border-radius:10px!important;background-color:#FFF!important;padding:0!important;box-shadow:0 2px 5px rgba(0,0,0,0.05)!important}[data-testid="stTextArea"]>div{background-color:#FFF!important}[data-testid="stTextArea"] textarea{padding:12px 15px!important;font-size:14px!important;color:#0d0d0c!important;background-color:#FFF!important;min-height:100px!important;resize:vertical!important;font-size:18px!important;font-weight:500!important}[data-testid="stTextArea"] textarea::placeholder{color:#0d0d0c!important;font-size:18px!important;font-weight:500!important}[data-testid="stTextArea"]:focus-within{border-color:#34C759!important;box-shadow:0 0 0 1px #34C759!important;outline:none!important}[data-testid="stTextArea"] textarea:focus{box-shadow:none!important;outline:none!important;border-color:transparent!important}[data-testid="stForm"] [data-baseweb="textarea"]:focus-within,[data-baseweb="textarea"]:focus,[data-baseweb="textarea"]:focus-within,[data-baseweb="base-input"]:focus,[data-baseweb="base-input"]:focus-within{border-color:#34C759!important;box-shadow:0 0 0 1px #34C759!important;outline-color:#34C759!important}:focus{outline-color:#34C759!important}textarea:focus{border-color:#34C759!important;box-shadow:0 0 0 1px #34C759!important;outline-color:#34C759!important}[data-testid="baseButton-primary"]{margin-top:10px!important;height:45px!important;font-size:24px!important;background-color:#34C759!important;border-radius:10px!important;color:white!important;padding:0!important;border:none!important;box-shadow:0 2px 5px rgba(52,199,89,0.3)!important;max-width:100%!important}[data-testid="baseButton-primary"]:hover{background-color:#28A745!important;box-shadow:0 4px 8px rgba(52,199,89,0.4)!important}[data-testid="baseButton-secondary"]{margin-top:10px!important;max-width:100%!important}.stTextArea{max-width:100%!important}"""

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

# Beispielprodukte hinzufügen falls keine CSV-Datei vorhanden ist (behalten für Produktkontext)
def create_sample_data():
    # Beispielprodukte
    products = [
        {"product_name": "Bio Äpfel", "category": "Obst & Gemüse", "price_value": 2.99, "currency": "€", "unit": "1kg", "image": "apple.jpg"},
        {"product_name": "Rinderhackfleisch", "category": "Fleisch", "price_value": 5.49, "currency": "€", "unit": "500g", "image": "beef.jpg"},
        {"product_name": "Bio Vollmilch", "category": "Milchprodukte", "price_value": 1.29, "currency": "€", "unit": "1L", "image": "milk.jpg"},
        {"product_name": "Mehrkornbrot", "category": "Backwaren", "price_value": 2.19, "currency": "€", "unit": "750g", "image": "bread.jpg"},
        {"product_name": "Mascarpone", "category": "Milchprodukte", "price_value": 1.79, "currency": "€", "unit": "250g", "image": "cheese.jpg"},
        {"product_name": "Spanische Orangen", "category": "Obst & Gemüse", "price_value": 3.49, "currency": "€", "unit": "2kg", "image": "orange.jpg"},
        {"product_name": "Lachsfilet", "category": "Fisch", "price_value": 8.99, "currency": "€", "unit": "300g", "image": "salmon.jpg"},
        {"product_name": "Avocado", "category": "Obst & Gemüse", "price_value": 1.99, "currency": "€", "unit": "Stück", "image": "avocado.jpg"}
    ]
    
    # Zufällige Gültigkeitsdaten generieren
    today = datetime.today()
    
    for product in products:
        valid_from = today - timedelta(days=random.randint(0, 5))
        valid_to = today + timedelta(days=random.randint(3, 14))
        product["valid_from"] = valid_from.strftime("%Y-%m-%d")
        product["valid_to"] = valid_to.strftime("%Y-%m-%d")
        
        # Badge für spezielle Angebote
        product["is_special"] = random.choice([True, False, False])
    
    return pd.DataFrame(products)

# CSV-Datei laden
@st.cache_data
def load_csv_data():
    try:
        df = pd.read_csv("Aldi_Angebote_Top.csv")
        if df.empty:
            return create_sample_data()
        return df
    except Exception as e:
        # Wenn ein Fehler auftritt, verwenden wir Beispieldaten
        return create_sample_data()

# Daten in String umwandeln für den Kontext
def get_products_context():
    df = load_csv_data()
    if df.empty:
        return "Keine Produktdaten verfügbar."
    
    context = "Aktuelle Aldi Angebote:\n\n"
    for _, row in df.iterrows():
        product_info = (
            f"Produkt: {row.get('product_name', 'N/A')}\n"
            f"Kategorie: {row.get('category', 'N/A')}\n"
            f"Preis: {row.get('price_value', 'N/A')} {row.get('currency', 'EUR')}\n"
            f"Gültig von: {row.get('valid_from', 'N/A')} bis {row.get('valid_to', 'N/A')}\n"
            f"Einheit: {row.get('unit', 'N/A')}\n\n"
        )
        context += product_info
    
    return context

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
        color: #34C759;
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
        "Benutze NUR die folgenden Produktinformationen, um alle Anfragen zu beantworten. " +
        "Wenn du nach Produkten gefragt wirst, die nicht in der Datenbank sind, sage deutlich, " +
        "dass du keine Informationen zu diesen Produkten hast. " +
        "WICHTIG: Verweise NIEMALS auf Angebotsbroschüren oder externe Quellen. " +
        "Antworte ausschließlich mit den Daten, die dir zur Verfügung gestellt werden." + 
        "WICHTIG: Antworte erst, wenn du alle Informationen analysiert hast, um eine korrekte Antwort zu geben."}
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
        # Text in dunklerer Farbe anzeigen
        st.markdown(f"""
        <div style="color: #000000 !important; font-weight: 500 !important;">
            {message["content"]}
        </div>
        """, unsafe_allow_html=True)

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
    
    /* Primary Button (Senden-Button) */
    [data-testid="baseButton-primary"] {
        margin-top: 10px !important;
        height: 45px !important;
        font-size: 24px !important;
        background-color: #34C759 !important;
        border-radius: 10px !important;
        color: white !important;
        padding: 0 !important;
        border: none !important;
        box-shadow: 0 2px 5px rgba(52, 199, 89, 0.3) !important;
        max-width: 100% !important;
    }
    
    [data-testid="baseButton-primary"]:hover {
        background-color: #28A745 !important;
        box-shadow: 0 4px 8px rgba(52, 199, 89, 0.4) !important;
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
    user_input = st.text_area("Chat-Eingabe", value=initial_value, placeholder="Was suchst du heute?", 
                          label_visibility="collapsed", key=current_key, height=120)
    
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
        
        # Kontext aus der CSV-Datei holen
        products_context = get_products_context()
        
        # Erweitere die Systemnachricht mit dem aktuellen Kontext
        context_message = {"role": "system", "content": f"Hier sind die aktuellen Produktinformationen:\n\n{products_context}\n\nWICHTIG: Verweise in deinen Antworten NIEMALS auf Angebotsbroschüren, Flyer oder andere externe Quellen. Verwende ausschließlich die oben aufgeführten Produktdaten."}
        
        # AI-Antwort generieren
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # OpenAI API-Aufruf mit neuer Syntax und erweitertem Kontext
            # Systemnachricht immer direkt verwenden (auch wenn sie im Session State geändert wurde)
            system_prompt = {
                "role": "system", 
                "content": "Du bist ein hilfreicher Einkaufsassistent für SparFuchs.de. " +
                "Benutze NUR die folgenden Produktinformationen, um alle Anfragen zu beantworten. " +
                "Wenn du nach Produkten gefragt wirst, die nicht in der Datenbank sind, sage deutlich, " +
                "dass du keine Informationen zu diesen Produkten hast. " +
                "WICHTIG: Verweise NIEMALS auf Angebotsbroschüren oder externe Quellen. " +
                "Antworte ausschließlich mit den Daten, die dir zur Verfügung gestellt werden." + 
                "WICHTIG: Antworte erst, wenn du alle Informationen analysiert hast, um eine korrekte Antwort zu geben."
            }
            
            # Erweitere die Systemnachricht mit dem aktuellen Kontext
            context_message = {"role": "system", "content": f"Hier sind die aktuellen Produktinformationen:\n\n{products_context}\n\nWICHTIG: Verweise in deinen Antworten NIEMALS auf Angebotsbroschüren, Flyer oder andere externe Quellen. Verwende ausschließlich die oben aufgeführten Produktdaten."}
            
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
                
                # Nur DeepseekV3 Base Modell verwenden
                model_variants = [
                    "deepseek/deepseek-chat",  # DeepSeek V3 Base
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
                                max_tokens=1200,
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
            ("Welche Obst-Angebote gibt es aktuell?", "🍎"),
            ("Wo ist diese Woche Hackfleisch im Angebot?", "🥩")
        ])
        
    with col2:        
        display_suggestions_row([
            ("Gibt es bei Aldi Reis, Nudeln und Kartoffeln im Angebot?", "🔍"),
            ("Wo ist Red Bull im Angebot?", "🔍")
        ])

# Zusätzliche Ideen für Anfänger unten anzeigen
if len([m for m in st.session_state.messages if m["role"] != "system"]) <= 2:
    st.markdown("<p style='margin-top: 20px; text-align: center; font-size: 14px; color: #666666;'>Du kannst mich auch fragen:</p>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    with cols[0]:
        if st.button("💰 Welche 3 Artikel sind am günstigsten bei Aldi?", type="secondary"):
            st.session_state.preset_input = "Welche 3 Artikel sind am günstigsten bei Aldi?"
            st.session_state.submit_text = "Welche 3 Artikel sind am günstigsten bei Aldi?"
            st.rerun()
    with cols[1]:
        if st.button("⚖️ Vergleiche Äpfel und Orangen", type="secondary"):
            st.session_state.preset_input = "Vergleiche Äpfel und Orangen"
            st.session_state.submit_text = "Vergleiche Äpfel und Orangen"
            st.rerun()
    with cols[2]:
        if st.button("🥗 Suche vegetarische Produkte", type="secondary"):
            st.session_state.preset_input = "Suche vegetarische Produkte"
            st.session_state.submit_text = "Suche vegetarische Produkte"
            st.rerun()

# Kleine Info am Seitenende für Mobilgeräte
st.markdown(
    "<div style='position: fixed; bottom: 10px; left: 0; width: 100%; text-align: center; font-size: 12px; color: #999999;'>"
    "© SparFuchs.de • AI Agent Made in Germany"
    "</div>",
    unsafe_allow_html=True
)