# Verbindungen zwischen Python-Code und CSS in SparFuchs.de

Diese Dokumentation erklärt die wichtigsten Verbindungen zwischen dem Python-Code in `app.py` und den CSS-Stilen in `static/styles.dev.css`.

## Grundlegende Verknüpfung

Die CSS-Datei wird in der Python-App über zwei Hauptfunktionen eingebunden und verwaltet:

1. `create_minified_css_file()`: Erstellt eine optimierte Version der CSS-Datei
2. `apply_modern_supermarket_style()`: Lädt und wendet die CSS-Stile auf die App an

## Schlüsselelemente und ihre Verbindungen

### 1. Chat-Nachrichten

**Python-Code (app.py):**
```python
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
```

**CSS (styles.dev.css):**
```css
/* Chat-Nachrichten */
.stChatMessage,
[data-testid="stChatMessage"] {
  background-color: #ffffff !important;
  background: #ffffff !important;
  border-radius: var(--border-radius) !important;
  padding: 18px !important;
  border: 1px solid #ffffff !important;
  box-shadow: var(--box-shadow);
  margin-bottom: 20px !important;
  color: #333 !important;
  transition: all 0.3s ease;
}
```

Die Chat-Nachrichten werden über `st.chat_message()` in Python erstellt und dann durch die CSS-Klassen `.stChatMessage` und `[data-testid="stChatMessage"]` gestylt. Das `unsafe_allow_html=True` ermöglicht die HTML-Formatierung in den Nachrichten.

### 2. Logo-Darstellung

**Python-Code (app.py):**
```python
# Logo mit CSS-Klassen aus der externen Datei
html_code = """
<div class="logo-container">
    <span class="logo-main" style="font-size: 38px !important; font-weight: 800 !important; color: var(--text-color) !important;">🛒 SparFuchs</span>
    <span id="orange-text" style="font-size: 38px !important; color: #FF6600 !important; font-weight: 800 !important; display: inline-block !important; text-shadow: 0 0 1px #FF6600 !important; -webkit-text-stroke: 0.5px #FF6600 !important;">.de</span>
</div>
<p class="logo-subtitle">Dein KI-Assistent für Supermarkt-Angebote</p>
"""
st.markdown(html_code, unsafe_allow_html=True)
```

**CSS (styles.dev.css):**
```css
/* Logo-Styling */
.logo-container {
  margin-bottom: 0px;
  display: flex;
  align-items: center;
}

.logo-main {
  font-size: 38px !important;
  font-weight: 800 !important;
  color: var(--text-color) !important;
  text-shadow: 0 0 1px var(--text-color) !important;
  letter-spacing: -0.02em !important;
  display: inline-block !important;
}

#orange-text {
  font-size: 38px !important;
  font-weight: 800 !important;
  color: #FF6600 !important;
  text-shadow: 0 0 1px #FF6600 !important;
  letter-spacing: -0.02em !important;
  -webkit-text-stroke: 0.5px #FF6600 !important;
  display: inline-block !important;
}
```

Das Logo wird über HTML mit spezifischen CSS-Klassen im Python-Code erstellt. Die Klassen `.logo-container`, `.logo-main` und `#orange-text` werden in der CSS-Datei definiert.

### 3. Vorschlags-Buttons

**Python-Code (app.py):**
```python
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
```

**CSS (styles.dev.css):**
```css
/* Prompt-Suggestions */
.prompt-suggestion-container {
  display: inline-block;
  margin: 5px;
  background: #FFFFFF;
}

.prompt-suggestion {
  background: var(--white);
  border-radius: 8px;
  padding: 10px 15px;
  margin: 10px 5px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #121111;
  display: inline-block;
  box-shadow: var(--hover-shadow);
  animation: fadeIn 0.5s ease;
}
```

Die Vorschlags-Buttons werden durch die Funktion `display_prompt_suggestion()` erstellt, die HTML mit den CSS-Klassen `.prompt-suggestion-container` und `.prompt-suggestion` generiert.

### 4. Lade-Animation

**Python-Code (app.py):**
```python
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
```

**CSS (styles.dev.css):**
```css
/* Loading Animation */
.loader-container {
  display: inline-flex;
  align-items: center;
}

.loading-text, 
.loading-dots {
  animation: pulse 1.5s infinite;
}

.search-spinner-box {
  text-align: center;
  margin-bottom: 12px;
  font-weight: bold;
  color: var(--secondary-color);
  background-color: #FFF8F0;
  padding: 8px;
  border-radius: var(--border-radius);
  border: 1px solid #FFE0C0;
  box-shadow: 0 2px 4px rgba(255, 102, 0, 0.1);
}
```

Die Ladeanimation wird über HTML mit den CSS-Klassen `.search-spinner-box`, `.loader-container`, `.loading-text` und `.loading-dots` erstellt. Die Animation selbst wird über die CSS-Animation `pulse` definiert.

## Responsives Design

Die Anwendung nutzt Media Queries in der CSS-Datei, um auf verschiedenen Geräten optimal anzuzeigen:

**CSS (styles.dev.css):**
```css
@media (max-width: 768px) {
  /* Layout & Container */
  .main .block-container {
    padding: 0 15px !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    margin-top: -40px !important;
  }
  
  /* weitere responsive Anpassungen... */
}
```

Diese Media Queries passen das Layout für mobile Geräte an, ohne dass im Python-Code spezielle Anpassungen notwendig sind. 