"""
Produktdatenverarbeitung für die SparFuchs.de Anwendung.

Dieses Modul enthält Funktionen zum Laden, Filtern und Aufbereiten
der Produktdaten aus CSV-Dateien.
"""
import streamlit as st
import pandas as pd
import re
from pathlib import Path

# Konstanten
CSV_FILE_PATH = Path("data/Angebote.csv")

@st.cache_data
def load_csv_data():
    """
    Lädt die Produktdaten aus der CSV-Datei.
    
    Die Funktion ist mit @st.cache_data dekoriert, um Mehrfachladungen zu vermeiden und die
    Performance zu verbessern.
    
    Returns:
        DataFrame: Ein Pandas DataFrame mit den Produktdaten oder ein leeres DataFrame, wenn die Datei nicht 
        gefunden wurde oder leer ist.
    """
    try:
        df = pd.read_csv(CSV_FILE_PATH)
        if df.empty:
            st.warning(f"Die CSV-Datei '{CSV_FILE_PATH}' ist leer. Bitte fügen Sie Produktdaten hinzu.")
            return pd.DataFrame()
        return df
    except Exception as e:
        st.warning(f"Fehler beim Laden der CSV-Datei '{CSV_FILE_PATH}': {str(e)}")
        return pd.DataFrame()

def get_products_context():
    """
    Wandelt die Produktdaten in einen formatierten Textstring für den KI-Kontext um.
    
    Die Funktion lädt die Produktdaten und formatiert sie als Textstring, der als
    Kontext für die KI-Anfragen verwendet wird.
    
    Returns:
        str: Formatierter Text mit allen Produktinformationen
    """
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

def get_filtered_products_context(user_query: str, selected_markets: list[str]):
    """
    Filtert die Produktdaten basierend auf der Benutzeranfrage und den ausgewählten Supermärkten
    und erstellt einen optimierten Kontext.
    
    Die Funktion analysiert die Benutzeranfrage semantisch, um relevante Produkte zu identifizieren,
    und erstellt einen optimierten Kontext für die KI. Sie berücksichtigt dabei:
    - Semantische Gruppen von Produkten (z.B. "Nudeln" umfasst verschiedene Pasta-Arten)
    - Spezifische Supermarkt-Filter
    - Kategorie-basierte Filter
    
    Args:
        user_query (str): Die Anfrage des Benutzers
        selected_markets (list[str]): Eine Liste der ausgewählten Supermärkte. Wenn leer, werden alle berücksichtigt.
        
    Returns:
        str: Optimierter Kontext mit gefilterten Produktinformationen
    """
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
        "getränke": "Getränke",
        "lebensmittel": "Lebensmittel",
        "drogerie": "Drogerie",
        "haushalt": "Haushalt",
        "kleidung": "Kleidung",
        "garten": ["Garten/Pflanzen", "Garten", "Pflanzen"]
    }
    
    # Normalisiere den Suchbegriff
    user_query_lower = user_query.lower()
    
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
            
        # NEU: Nach ausgewählten Supermärkten filtern, wenn welche ausgewählt wurden
        if selected_markets: # Prüft, ob die Liste nicht leer ist
            filtered_df = filtered_df[filtered_df['Supermarkt'].isin(selected_markets)]
            
            # Wenn nach dem Filtern keine Produkte mehr übrig sind, geben wir einen Hinweis zurück,
            # anstatt den gesamten Kontext.
            if filtered_df.empty:
                return f"Keine Produkte in den ausgewählten Supermärkten ({', '.join(selected_markets)}) gefunden, die zur Anfrage '{user_query}' passen."
    
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
    context += "- 'Nudeln' umfasst auch Pasta, Tortelloni, Farfalle, Spaghetti, Penne usw. - jegliche Art von Pasta ist eine Form von Nudeln.\n"
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