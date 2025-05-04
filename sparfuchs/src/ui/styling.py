"""
CSS-Styling und Verarbeitung für die SparFuchs.de Anwendung.

Dieses Modul enthält Funktionen zum Laden und Anwenden der CSS-Stile
auf die Streamlit-Anwendung.
"""
import streamlit as st
import re
from pathlib import Path

def apply_modern_supermarket_style():
    """
    Lädt die CSS-Styles aus der Entwicklungsdatei, minimiert sie und wendet sie auf die App an.
    
    Die Funktion stellt sicher, dass der 'static'-Ordner existiert und liest die Styles 
    aus der styles.dev.css. Die CSS wird minimiert und auf die Streamlit-App angewendet.
    """
    # Stelle sicher, dass der static-Ordner existiert
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    dev_css_path = static_dir / "styles.dev.css"
    min_css_path = static_dir / "styles.min.css"
    
    # CSS-Datei einlesen, minimieren und speichern
    if dev_css_path.exists():
        with open(dev_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        
        # Einfache CSS-Minimierung
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)  # Kommentare entfernen
        css_content = re.sub(r'\s+', ' ', css_content)  # Mehrfach-Leerzeichen zu einem reduzieren
        css_content = css_content.strip()
        
        # Speichern der minimierten CSS-Datei
        with open(min_css_path, "w", encoding="utf-8") as f:
            f.write(css_content)
    elif min_css_path.exists():
        # Wenn keine dev-CSS, aber min-CSS existiert, verwende die vorhandene min-CSS
        with open(min_css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    else:
        # Fallback: Leere CSS verwenden
        css_content = ""
    
    # CSS auf die App anwenden
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

def apply_base_styles():
    """
    Wendet grundlegende Streamlit-Seitenkonfiguration und Basis-Stile an.
    
    Diese Funktion sollte vor allen anderen st-Aufrufen ausgeführt werden.
    """
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
    </style>
    """, unsafe_allow_html=True)

    # Einige grundlegende Stile sofort anwenden
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