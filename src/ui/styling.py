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
    
    css_to_apply = ""

    # CSS-Datei einlesen
    if dev_css_path.exists():
        with open(dev_css_path, "r", encoding="utf-8") as f:
            css_to_apply = f.read()
        
        # Einfache CSS-Minimierung (optional, da Browser das auch handhaben)
        # css_to_apply = re.sub(r'/\*.*?\*/', '', css_to_apply, flags=re.DOTALL)  # Kommentare entfernen
        # css_to_apply = re.sub(r'\s+', ' ', css_to_apply)  # Mehrfach-Leerzeichen
        # css_to_apply = css_to_apply.strip()
        
        # Es ist nicht zwingend notwendig, die minimierte Version separat zu speichern,
        # es sei denn, es gibt einen bestimmten Grund dafür (z.B. Performance-Analyse).
        # Streamlit selbst hat keinen direkten Mechanismus, um zwischen dev und min CSS zu wechseln.
        # with open(min_css_path, "w", encoding="utf-8") as f:
        #     f.write(css_to_apply) # Speichere die (ggf. minimierte) CSS

    elif min_css_path.exists():
        # Fallback, falls nur die minimierte Version existiert
        with open(min_css_path, "r", encoding="utf-8") as f:
            css_to_apply = f.read()
    else:
        # Fallback: Leere CSS verwenden, wenn keine Datei gefunden wird
        # Dies verhindert einen Fehler, falls die CSS-Datei fehlt.
        st.warning("Keine CSS-Datei (styles.dev.css oder styles.min.css) im 'static'-Ordner gefunden.")
        css_to_apply = ""
    
    # CSS auf die App anwenden, nur wenn css_to_apply nicht leer ist
    if css_to_apply:
        st.markdown(f"<style>{css_to_apply}</style>", unsafe_allow_html=True)

def apply_base_styles():
    """
    Wendet grundlegende Streamlit-Seitenkonfiguration an.
    
    Diese Funktion sollte vor allen anderen st-Aufrufen ausgeführt werden.
    """
    # Streamlit Seitenkonfiguration
    st.set_page_config(
        page_title="SparFuchs.de", 
        page_icon="🛒",
        layout="centered"
    )
    # Der st.markdown-Aufruf für Basis-Stile wurde entfernt.
    # Diese Stile müssen in static/styles.dev.css enthalten sein. 