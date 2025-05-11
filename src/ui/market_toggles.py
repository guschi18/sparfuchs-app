import streamlit as st

# List of supermarkets
MARKETS = ["Aldi", "Lidl", "Penny", "Edeka", "Rewe"]

def render_market_toggles() -> list[str]:
    """
    Renders a segmented control for supermarket selection using Streamlit,
    centered on the page.

    Returns:
        list[str]: A list of selected supermarket names.
    """

    # Create columns for layout: a small one, a larger middle one, and another small one
    # Adjust the ratios as needed for desired centering, e.g., [1, 2, 1] or [0.5, 3, 0.5]
    col1, col2, col3 = st.columns([1, 3, 1]) # You can adjust these ratios

    with col2: # Place the segmented control in the middle column
        selected_markets = st.segmented_control(
            "", # Label is empty as per original code
            options=MARKETS,
            selection_mode="multi", # Assuming "multi" is the desired mode
            key="market_segment_control"
            # default=MARKETS # Uncomment this line if you want all markets to be selected by default
        )

    # st.segmented_control already returns a list of selected options
    # or an empty list if none are selected.
    # If no selection is made, it might return None, so ensure it's a list.
    return selected_markets if selected_markets is not None else []

if __name__ == '__main__':
    # Example usage when running this file directly
    st.set_page_config(layout="wide") # Optional: use wide layout for better visibility of centering
    st.title("Market Toggle Test - Centered")
    selected = render_market_toggles()
    st.write("Ausgewählte Märkte:", selected) 