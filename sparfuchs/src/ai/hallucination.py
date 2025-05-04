"""
Halluzinationserkennung für KI-Antworten.

Dieses Modul enthält Funktionen zur Erkennung von KI-Halluzinationen,
um sicherzustellen, dass nur tatsächlich vorhandene Produkte in den Antworten enthalten sind.
"""
import re

def detect_hallucinations(response, df):
    """
    Prüft, ob die KI-Antwort möglicherweise halluzinierte Produkte enthält.
    
    Die Funktion analysiert die KI-Antwort und vergleicht erwähnte Produkte mit den
    tatsächlich in der Datenbank vorhandenen Produkten, um Halluzinationen zu erkennen.
    
    Args:
        response (str): Die Antwort des KI-Modells
        df (DataFrame): Der Produktdatensatz
    
    Returns:
        bool: True, wenn die Antwort wahrscheinlich halluzinierte Produkte enthält
    """
    # Wenn die Antwort einen Hinweis enthält, dass Produkte nicht gefunden wurden
    if "keine Informationen" in response.lower() or "nicht gefunden" in response.lower() or "keine aktuellen angebote" in response.lower():
        return False
    
    # Extrahiere Produktnamen aus der CSV
    produktnamen = df['Produktname'].str.lower().tolist()
    
    # Füge Kategorien und Unterkategorien als erlaubte Begriffe hinzu
    kategorien = df['Kategorie'].str.lower().unique().tolist()
    unterkategorien = []
    for uk in df['Unterkategorie'].dropna():
        # Unterkategorien können mehrere Begriffe mit "/" enthalten, diese aufteilen
        if isinstance(uk, str):
            unterkategorien.extend([u.strip().lower() for u in uk.split('/')])
    unterkategorien = list(set(unterkategorien))  # Duplikate entfernen
    
    # Extrahiere alle Produktnamenteile für flexibleres Matching
    produktteile = []
    for name in produktnamen:
        teile = name.split()
        for teil in teile:
            if len(teil) > 3:  # Nur längere Begriffe verwenden
                produktteile.append(teil.lower())
    produktteile = list(set(produktteile))  # Duplikate entfernen
    
    # Füge Supermarktnamen und weitere allgemeine Begriffe hinzu
    allgemeine_begriffe = ['aldi', 'lidl', 'supermarkt', 'angebot', 'preis', 'euro', '€', 
                          'gültig', 'von', 'bis', 'startdatum', 'enddatum', 'preisvergleich',
                          'getränke', 'lebensmittel', 'hier sind', 'aktuell', 'im angebot',
                          'rum', 'vodka', 'whiskey', 'bier', 'wein', 'gin', 'likör', 'spirituosen',
                          'alkohol', 'mineralwasser', 'cola', 'saft', 'ja', 'nein', 'leider', 'finden',
                          'diese', 'woche', 'club', 'havana']
    
    erlaubte_begriffe = produktnamen + kategorien + unterkategorien + allgemeine_begriffe + produktteile
    
    # Extrahiere alle fettgedruckten Texte (wahrscheinlich Produktnamen)
    bold_products = re.findall(r'\*\*(.*?)\*\*', response)
    
    # Wenn es keine fettgedruckten Texte gibt (z.B. bei kategorie-basierten Anfragen ohne konkretes Produkt)
    if not bold_products:
        return False
    
    # Prüfe jeden fettgedruckten Text, ob er ein tatsächliches Produkt sein könnte
    for product in bold_products:
        # Entferne Zusatzinformationen in Klammern und Preis-Suffix
        clean_product = re.sub(r'\s*\(.*?\)', '', product).split(':')[0].strip().lower()
        
        # Prüfe, ob das Produkt einer Variation eines CSV-Produkts ähnelt
        found = False
        for erlaubter_begriff in erlaubte_begriffe:
            # Prüfe auf teilweise Übereinstimmung (z.B. "Äpfel" vs. "Bio Äpfel")
            if clean_product in erlaubter_begriff or erlaubter_begriff in clean_product:
                found = True
                break
            
            # Bei zusammengesetzten Begriffen prüfen, ob Teile übereinstimmen
            parts = clean_product.split()
            for part in parts:
                if len(part) > 3 and (part in erlaubter_begriff or erlaubter_begriff in part):
                    found = True
                    break
            if found:
                break
        
        if not found and len(clean_product) > 3:  # Ignoriere sehr kurze Begriffe
            # Mögliche Halluzination gefunden
            return True
    
    return False 