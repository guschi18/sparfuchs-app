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

def create_chat_input(disabled: bool = False):
    """
    Erstellt das Chat-Eingabefeld und den Submit-Button.
    
    Args:
        disabled (bool): Ob das Eingabefeld und der Button deaktiviert sein sollen.

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
        
        text_area_value = ""  # Standardwert für das Textfeld
        if disabled:  # Wenn das Feld deaktiviert ist (KI verarbeitet)
            text_area_value = st.session_state.get("current_processing_prompt", "")
        elif "preset_input" in st.session_state:  # Wenn das Feld aktiv ist und ein Vorschlag angeklickt wurde
            text_area_value = st.session_state.get("preset_input", "")
        # Ansonsten (Feld aktiv, kein Vorschlag) bleibt text_area_value leer, 
        # was durch den key_counter-Mechanismus das Feld für eine neue Eingabe leert.

        user_input_from_field = st.text_area("Chat-Eingabe", 
                                 value=text_area_value, 
                                 placeholder="Wonach suchst du? (Obst, Rezeptideen, Preisvergleiche, etc.. ) ", 
                                 label_visibility="collapsed", 
                                 key=current_key, 
                                 height=95,
                                 disabled=disabled)
        
        # Verfolge Änderungen im Textfeld nur, wenn es aktiv ist
        if not disabled and user_input_from_field and st.session_state.get("last_input_value") != user_input_from_field:
            st.session_state["last_input_value"] = user_input_from_field
        
        # Preset-Wert nach Verwendung zurücksetzen, nur wenn Feld aktiv ist und preset verwendet wurde
        if not disabled and "preset_input" in st.session_state and text_area_value == st.session_state.preset_input:
            # Setze den Text auch in last_input_value, um doppelte Verarbeitung zu vermeiden, falls der Nutzer nichts ändert
            if st.session_state.get("preset_input"): # Nur wenn preset_input nicht leer war
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
                                 key=f"submit_button_{st.session_state.key_counter}",
                                 disabled=disabled)
        
        # Verwende user_input_from_field hier, da es den tatsächlichen Inhalt des Feldes widerspiegelt
        if submit_clicked and user_input_from_field and user_input_from_field.strip():
            st.session_state["submit_text"] = user_input_from_field.strip()
            return user_input_from_field.strip()
        
        # Reset-Button direkt unter dem Send-Button platzieren (nur wenn es AI-Antworten gibt)
        has_ai_responses = any(message["role"] == "assistant" for message in st.session_state.messages)
        if has_ai_responses:
            if st.button("🔄 Chat zurücksetzen", key="reset_chat", type="secondary", use_container_width=True, disabled=disabled):
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
        st.markdown("<h3 class='welcome-header'>👋 Willkommen! Hier sind einige Vorschläge:</h3>", unsafe_allow_html=True)
        
        # Neue Methode ohne JavaScript-Abhängigkeit
        col1, col2 = st.columns(2)
        
        with col1:
            display_suggestions_row([
                ("Wo ist Coca Cola im Angebot?", "🔍"),
                ("Wo ist diese Woche Hackfleisch am günstigsten?", "🥩")
            ])
            
        with col2:        
            display_suggestions_row([
                 ("Welche Obst Angebote gibt es aktuell?", "🍎"),
                ("Wo sind Nudeln, Kartoffeln und Reis im Angebot?", "🔍")
            ])

def display_followup_suggestions():
    """
    Zeigt zusätzliche Vorschläge für Anfänger an.
    """
    if len([m for m in st.session_state.messages if m["role"] != "system"]) <= 2:
        st.markdown("<p class='recipe-finder-hint'>Wenn More-Rezeptfinder aktiviert ist, kannst mich auch fragen:</p>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        with cols[2]:
            if st.button("🥗 Ich suche ein Rezept mit Zucchini", type="secondary", use_container_width=True):
                st.session_state.preset_input = "Ich suche ein Rezept mit Zucchini"
                st.session_state.submit_text = "Ich suche ein Rezept mit Zucchini"
                st.rerun()
        with cols[0]:
            if st.button("🥘 Ich möchte gerne einen Auflauf mit Kartoffeln und Schinken essen", type="secondary", use_container_width=True):
                st.session_state.preset_input = "Ich möchte gerne einen Auflauf mit Kartoffeln und Schinken essen"
                st.session_state.submit_text = "Ich möchte gerne einen Auflauf mit Kartoffeln und Schinken essen"
                st.rerun()
        with cols[1]:
            if st.button("🍝 Gib mir bitte ein Rezept mit Hühnchen und Nudeln", type="secondary", use_container_width=True):
                st.session_state.preset_input = "Gib mir bitte ein Rezept mit Hühnchen und Nudeln"
                st.session_state.submit_text = "Gib mir bitte ein Rezept mit Hühnchen und Nudeln"
                st.rerun()

def display_footer():
    """
    Zeigt den Footer der Anwendung an.
    """
    st.markdown(
        "<div class='app-footer'>© SparFuchs.de • AI Agent Made in Germany</div>",
        unsafe_allow_html=True
    ) 