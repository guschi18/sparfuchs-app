import streamlit as st

# Liste der Supermärkte
MARKETS = ["Aldi", "Lidl", "Penny", "Edeka", "Rewe"]

def render_market_toggles() -> list[str]:
    """
    Rendert ein Segmented Control zur Auswahl von Supermärkten mit Streamlit,
    zentriert auf der Seite.

    Returns:
        list[str]: Eine Liste der ausgewählten Supermarkt-Namen.
    """

    # Erstelle Spalten für das Layout: eine kleine, eine größere mittlere und eine weitere kleine Spalte
    # Passe die Verhältnisse bei Bedarf an, um die gewünschte Zentrierung zu erreichen, z.B. [1, 2, 1] oder [0.5, 3, 0.5]
    col1, col2, col3 = st.columns([1, 3, 1]) # Du kannst diese Verhältnisse anpassen

    with col2: # Platziere das Segmented Control in der mittleren Spalte
        selected_markets = st.segmented_control(
            "Supermärkte auswählen", # Label ist leer gemäß Originalcode
            options=MARKETS,
            selection_mode="multi", # Annahme: "multi" ist der gewünschte Modus
            key="market_segment_control",
            label_visibility="collapsed" # Label ausblenden
            # default=MARKETS # Aktiviere diese Zeile, wenn standardmäßig alle Märkte ausgewählt sein sollen
        )

    # st.segmented_control gibt bereits eine Liste der ausgewählten Optionen zurück
    # oder eine leere Liste, wenn keine ausgewählt wurden.
    # Wenn keine Auswahl getroffen wird, könnte es None zurückgeben, stelle also sicher, dass es eine Liste ist.
    return selected_markets if selected_markets is not None else []

if __name__ == '__main__':
    # Beispielverwendung beim direkten Ausführen dieser Datei
    st.set_page_config(layout="wide") # Optional: Verwende ein breites Layout für bessere Sichtbarkeit der Zentrierung
    st.title("Market Toggle Test - Centered")
    selected = render_market_toggles()
    st.write("Ausgewählte Märkte:", selected) 