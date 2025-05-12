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
import time
import random
import os
from pathlib import Path
from dotenv import load_dotenv

# Interne Module importieren
from src.ui.styling import apply_base_styles, apply_modern_supermarket_style
from src.ui.layout import (
    display_logo, display_chat_container, create_chat_input, 
    display_welcome_suggestions, display_followup_suggestions, 
    display_footer
)
from src.data.product_data import load_csv_data
from src.ai.client import init_client, get_available_models
from src.ai.context import process_query
from src.ai.hallucination import detect_hallucinations
from src.utils.helpers import initialize_session_state, ensure_directories, copy_csv_if_missing
from src.ui.market_toggles import render_market_toggles, render_recipe_toggle

# Stelle sicher, dass die erforderlichen Verzeichnisse existieren
ensure_directories()
copy_csv_if_missing()

# Umgebungsvariablen laden
load_dotenv()

# Anwendung konfigurieren und Basis-Styles anwenden (muss vor anderen st-Aufrufen sein)
apply_base_styles()

# Modernes Supermarkt-Design anwenden
apply_modern_supermarket_style()

# Session State initialisieren
initialize_session_state(st.session_state)

# OpenAI-Client initialisieren
client = init_client()

# Logo und Seitentitel anzeigen
display_logo()

# Render market toggles and get selected markets
selected_markets = render_market_toggles()

# Chat-Container anzeigen und Spinner-Platzhalter erhalten
spinner_placeholder = display_chat_container()

# More-Rezeptfinder Toggle anzeigen (vor dem Chat-Input)
recipe_mode = render_recipe_toggle()

# Chat-Eingabefeld erstellen und Benutzereingabe erhalten
user_input = create_chat_input()

# Wenn Benutzer eine Eingabe gemacht hat
if user_input:
    prompt = user_input
    
    # Markiere, dass die erste Eingabe verarbeitet wurde
    st.session_state["is_first_input"] = False
    
    # Speichern der aktuellen Eingabe für Vergleich beim nächsten Mal
    st.session_state["previous_input"] = prompt
    
    # Erhöhe den Key-Zähler, um beim nächsten Rendering ein leeres Eingabefeld zu erzeugen
    st.session_state["key_counter"] += 1
    
    # Benutzernachricht zum Verlauf hinzufügen
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Setze submit_text zurück, um doppelte Verarbeitung nach rerun zu verhindern
    st.session_state["submit_text"] = None 
    
    try:
        # Hole systemnachricht und kontext, unter Berücksichtigung der ausgewählten Märkte und des Rezept-Modus
        system_prompt, context_message, products_context = process_query(prompt, selected_markets, recipe_mode)
        
        # Erstelle die Nachrichtenliste mit garantierter Systemnachricht
        messages_with_context = [system_prompt, context_message]
        # Füge nur user und assistant Nachrichten hinzu
        messages_with_context.extend([m for m in st.session_state.messages if m["role"] != "system"])
        
        # Zeige Ladeanimation
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
            
            # Verfügbare Modellvarianten
            model_variants = get_available_models()
            
            success = False
            error_messages = []
            full_response = ""  # Initialisierung der Variable vor der Verwendung
            
            # Gib dem System mehr Zeit, um die Anfrage zu verarbeiten
            time.sleep(1.5)  # Erhöhte Verzögerung für bessere Stabilität
            
            # Versuche jeden Modelltyp nacheinander
            for model in model_variants:
                model_name = model["id"]
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
                            max_tokens=12000,  # Erhöht, um vollständige Antworten zu ermöglichen
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
                
                # Wenn ein Modell erfolgreich war, breche die Schleife ab
                if success:
                    break
            
            if not success:
                # Debug-Modus aus Umgebungsvariable auslesen
                debug_mode = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes"]
                
                if debug_mode:
                    # Detaillierte Fehlermeldungen anzeigen
                    error_details = "\n\n".join(error_messages)
                    full_response = f"Entschuldigung, ich konnte Ihre Anfrage nicht bearbeiten. Technische Details:\n\n{error_details}"
                else:
                    full_response = "Entschuldigung, ich konnte Ihre Anfrage nicht bearbeiten. Bitte versuchen Sie es später erneut."
        
        # Nach dem API-Aufruf den Spinner entfernen
        spinner_placeholder.empty()
        
    except Exception as e:
        # Debug-Modus aus Umgebungsvariable auslesen
        debug_mode = os.getenv("DEBUG", "False").lower() in ["true", "1", "t", "yes"]
        
        if debug_mode:
            full_response = f"Entschuldigung, ein unerwarteter Fehler ist aufgetreten: {str(e)}"
        else:
            full_response = "Entschuldigung, ein unerwarteter Fehler ist aufgetreten. Bitte versuchen Sie es später erneut."
    
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
    
    # Nach der Antwortgenerierung die Seite neu laden, um den aktualisierten Chat anzuzeigen
    st.rerun()

# Vorschläge anzeigen
display_welcome_suggestions()
display_followup_suggestions()

# Footer anzeigen
display_footer() 