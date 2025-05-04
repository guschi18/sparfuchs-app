"""
Layout-Funktionen für die SparFuchs.de Benutzeroberfläche.

Dieses Modul enthält Funktionen zum Erstellen und Anzeigen der
verschiedenen UI-Elemente der Anwendung.
"""
import streamlit as st

def display_logo():
    """
    Zeigt das SparFuchs.de Logo mit Styling an.
    """
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

def display_chat_container():
    """
    Erstellt und zeigt den Chat-Container an.
    
    Returns:
        tuple: Ein Tuple aus dem Chat-Container und dem Spinner-Platzhalter
    """
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
    
    # Platzhalter für Spinner festlegen
    spinner_placeholder = st.empty()
    
    return spinner_placeholder

def create_chat_input():
    """
    Erstellt das Chat-Eingabefeld und den Submit-Button.
    
    Returns:
        str: Der eingegebene Text, wenn vorhanden, sonst None
    """
    # Initialisiere eine Key-Zähler-Variable, wenn sie noch nicht existiert
    if "key_counter" not in st.session_state:
        st.session_state["key_counter"] = 0

    # Textfeld-Container - nur eine Ebene von Spalten
    textfield_cols = st.columns([1, 20, 3])  # Weniger leere Spalte links, breiteres Textfeld

    # Textfeld in der mittleren Spalte
    with textfield_cols[1]:
        current_key = f"custom_chat_input_{st.session_state.key_counter}"
        initial_value = st.session_state.get("preset_input", "")
        user_input = st.text_area("Chat-Eingabe", 
                                 value=initial_value, 
                                 placeholder="Wonach suchst du? (Obst, Rezeptideen, Preisvergleiche, etc.. ) ", 
                                 label_visibility="collapsed", 
                                 key=current_key, 
                                 height=95)
        
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
        submit_clicked = st.button("→", 
                                 type="primary", 
                                 use_container_width=True, 
                                 key=f"submit_button_{st.session_state.key_counter}")
        
        if submit_clicked and user_input and user_input.strip():
            st.session_state["submit_text"] = user_input.strip()
            return user_input.strip()
        
        # Reset-Button direkt unter dem Send-Button platzieren (nur wenn es AI-Antworten gibt)
        has_ai_responses = any(message["role"] == "assistant" for message in st.session_state.messages)
        if has_ai_responses:
            if st.button("🔄 Chat zurücksetzen", key="reset_chat", type="secondary", use_container_width=True):
                # System-Nachricht behalten, Rest löschen
                system_message = st.session_state.messages[0]
                st.session_state.messages = [system_message]
                st.rerun()
    
    # Wenn ein voreingestellter Text zur Verarbeitung vorhanden ist
    if st.session_state.get("submit_text"):
        submitted_text = st.session_state["submit_text"]
        st.session_state["submit_text"] = None
        return submitted_text
    
    return None

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

def display_welcome_suggestions():
    """
    Zeigt Vorschläge für neue Benutzer an.
    """
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

def display_followup_suggestions():
    """
    Zeigt zusätzliche Vorschläge für Anfänger an.
    """
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

def display_footer():
    """
    Zeigt den Footer der Anwendung an.
    """
    st.markdown(
        "<div class='app-footer'>© SparFuchs.de • AI Agent Made in Germany</div>",
        unsafe_allow_html=True
    ) 