"""
Kontextgenerierung für KI-Anfragen.

Dieses Modul enthält Funktionen für die Erstellung von optimierten Kontexten
für KI-Anfragen basierend auf Benutzeranfragen und Produktdaten.
"""
import re
from ..data.product_data import get_filtered_products_context, load_recipes
import pandas as pd

def get_system_prompt():
    """
    Erstellt den Systemprompt für die KI.
    
    Der Systemprompt enthält die grundlegenden Anweisungen und Formatierungsregeln
    für die KI, um korrekte und hilfreiche Antworten zu generieren.
    
    Returns:
        dict: Ein Dictionary mit dem Systemprompt im OpenAI-Format
    """
    system_prompt = {
        "role": "system", 
        "content": "Du bist ein hilfreicher Einkaufsassistent für SparFuchs.de mit fundiertem Wissen über Lebensmittel und Produktkategorien. " +
        "Benutze die dir bereitgestellten Produktinformationen, um Anfragen zu beantworten. " +
        "WICHTIG: Du darfst NUR Produkte erwähnen, die in den bereitgestellten Daten vorhanden sind. " +
        "ERFINDE NIEMALS Produkte oder Angebote. Wenn du ein Produkt nicht in den Daten findest, sage klar, " +
        "dass du keine Information darüber hast. " +
        "SEMANTISCHE INTERPRETATION - SEHR WICHTIG: Wende dein volles Verständnis über Lebensmittelkategorien an. " +
        "PRODUKTBEZIEHUNGEN ERKENNEN: " +
        "- Wenn der Nutzer nach 'Nudeln' fragt, berücksichtige ALLE verschiedenen Arten wie: Pasta, Tortelloni, Farfalle, Spaghetti, Penne usw. " +
        "- Wenn 'Bio-Pasta' in den Daten steht, ist dies eine Art von Nudeln! " +
        "- Produktmarken (wie 'GUT BIO', 'CUCINA NOBILE') sind nur Markennamen, fokussiere dich auf die Produktart dahinter. " +
        "- Selbst wenn Produkte in unterschiedlichen Kategorien oder Unterkategorien aufgeführt sind, nutze dein Wissen, " +
        "  um zu erkennen, was sie wirklich sind (z.B. können Tortelloni unter 'Fertiggerichte' kategorisiert sein, sind aber trotzdem Nudeln). " +
        "WICHTIG: Nutze dein eigenes Wissen über Lebensmittel, um Produkte zu klassifizieren, unabhängig davon, " +
        "wie sie im Datensatz kategorisiert sind. " +
        "VOLLSTÄNDIGE ANTWORTEN: Bei Kategorie-Anfragen (z.B. 'Welche Getränke...' oder 'Welche Nudeln...') liste ALLE passenden Produkte auf, " +
        "die in den Daten vorhanden sind und zur semantischen Kategorie passen. Suche aktiv nach ALLEN relevanten Produkten. " +
        "WICHTIG: Antworte IMMER auf Deutsch, unabhängig von der Sprache der Anfrage. " +
        "WICHTIG: Verweise NIEMALS auf Angebotsbroschüren oder externe Quellen. " +
        "Antworte ausschließlich mit den Daten, die dir zur Verfügung gestellt werden. " + 
        "WICHTIG: Antworte erst, wenn du alle Informationen analysiert hast, um eine korrekte Antwort zu geben. " +
        "FORMATIERUNGSANWEISUNG: Formatiere deine Antworten zu Produkten immer in folgendem Format: " +
        "1. Beginne mit einer kurzen einleitenden Antwort, die die Frage beantwortet. " +
        "2. Liste dann jedes gefundene Produkt in folgendem klaren Format auf: " +
        "\n**Produktname** (mit Details wie Gewicht, Sorte, etc.): Preis €<br>" +
        "\n<strong class=\"meta-info\">Gültig:</strong> [DD.MM.YYYY] bis [DD.MM.YYYY]<br>" +
        "\n<strong class=\"meta-info\">Supermarkt:</strong> [Supermarktname]" +
        "\n\n" +
        "3. Bei Preisvergleichen oder Zusammenfassungen, nutze einen abschließenden Absatz mit einer klaren Kennzeichnung: " +
        "\n**Preisvergleich:** Das günstigste Produkt ist X für Y € (Z € pro kg/Stück)." +
        "\n\n" +
        "4. Wenn ein gesuchtes Produkt nicht verfügbar ist, teile dies explizit mit: " +
        "\n**Hinweis:** Bei [Produkt] habe ich leider keine aktuellen Angebote bei [Supermarkt] gefunden." +
        "\n\n" +
        "5. Verwende fettgedruckten Text für Hervorhebungen der Struktur-Elemente wie oben gezeigt." +
        "6. WICHTIG: Setze nach JEDEM Element einen HTML-Zeilenumbruch mit <br>. Jedes Element (Produktname, Gültig vom, Supermarkt) MUSS auf einer eigenen Zeile stehen!" +
        "7. EXTREM WICHTIG: Verwende das explizite HTML-Tag <br> nach jeder Zeile, anstatt nur Markdown-Zeilenumbrüche, damit die Elemente klar voneinander getrennt angezeigt werden." +
        "\n\n" +
        "Beispiel: " +
        "\nJa, bei Aldi gibt es aktuell Kartoffeln und Nudeln im Angebot:\n" +
        "\n**Speisefrühkartoffeln** (1,5 kg): 2,79 €<br>" +
        "\n<strong class=\"meta-info\">Gültig:</strong> 24.04.2025 bis 26.04.2025<br>" +
        "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi" +
        "\n\n" +
        "**CUCINA NOBILE Farfalle Fantasia** (versch. Sorten, 250 g): 1,49 €<br>" +
        "\n<strong class=\"meta-info\">Gültig:</strong> 22.04.2025 bis 26.04.2025<br>" +
        "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi" +
        "\n\n" +
        "**Hinweis:** Bei Reis habe ich leider keine aktuellen Angebote bei Aldi gefunden."
    }
    
    return system_prompt

def process_query(prompt: str, selected_markets: list[str], recipe_mode: bool):
    """
    Verarbeitet eine Benutzeranfrage und bereitet den Kontext für die KI-Antwort vor.
    
    Die Funktion erstellt einen system_prompt und einen context_message für die KI-Anfrage,
    basierend auf der Benutzeranfrage und den gefilterten Produktdaten.
    
    Args:
        prompt (str): Die Anfrage des Benutzers
        selected_markets (list[str]): Die vom Benutzer ausgewählten Supermärkte.
        recipe_mode (bool): Gibt an, ob der Rezeptfinder-Modus aktiv ist.
        
    Returns:
        tuple: (system_prompt, context_message, products_context)
               - system_prompt: Systemnachricht für die KI
               - context_message: Kontextnachricht mit Produktdaten
               - products_context: Gefilterte Produktdaten als Text
    """
    try:
        # Systemprompt
        system_prompt = get_system_prompt()
        
        # Kontext aus der CSV-Datei holen (gefiltert basierend auf der Anfrage und ausgewählten Märkten)
        products_context = get_filtered_products_context(prompt, selected_markets)
        
        # Rezeptkontext hinzufügen, wenn der Modus aktiv ist
        recipe_context = ""
        if recipe_mode:
            recipes_df = load_recipes()
            if not recipes_df.empty:
                # Extrahiere Schlüsselwörter aus dem Prompt (mind. 3 Zeichen)
                prompt_lower = prompt.lower()
                keywords = re.findall(r'\b\w{3,}\b', prompt_lower)
                
                filtered_recipes_df = pd.DataFrame() # Initialisiere leeren DataFrame

                if keywords:
                    # Annahme: Die relevanten Spalten heißen 'Rezeptname' und 'Zutaten'
                    # Passe dies bei Bedarf an die tatsächlichen Spaltennamen in More_Rezepte.csv an.
                    search_columns = ['Rezeptname', 'Zutaten'] 
                    # Stelle sicher, dass die Spalten im DataFrame existieren
                    existing_search_columns = [col for col in search_columns if col in recipes_df.columns]

                    if existing_search_columns:
                        mask = pd.Series(False, index=recipes_df.index)
                        for keyword in keywords:
                            keyword_mask = pd.Series(False, index=recipes_df.index)
                            for col in existing_search_columns:
                                # Prüfe, ob die Spalte String-Typ ist, bevor .str verwendet wird
                                if pd.api.types.is_string_dtype(recipes_df[col]):
                                     keyword_mask = keyword_mask | recipes_df[col].str.contains(keyword, case=False, na=False)
                            mask = mask | keyword_mask
                        filtered_recipes_df = recipes_df[mask]

                # Nur wenn gefilterte Rezepte gefunden wurden, füge sie zum Kontext hinzu
                if not filtered_recipes_df.empty:
                    recipe_context += "\n\nZUSÄTZLICHE INFORMATIONEN: RELEVANTE REZEPTE (basierend auf Anfrage)\n"
                    recipe_context += "Wenn der Benutzer nach Rezepten, Kochideen oder ähnlichem fragt, nutze die folgenden Rezeptdaten, da sie zur Anfrage passen könnten:\n\n"
                    recipe_context += filtered_recipes_df.to_string(index=False, header=True)
                    recipe_context += "\n\nENDE DER REZEPTINFORMATIONEN\n"
                # Optional: Hinweis hinzufügen, wenn keine *relevanten* Rezepte gefunden wurden?
                # else:
                #     recipe_context = "\n\n(Rezeptmodus ist aktiv, aber keine zur Anfrage passenden Rezepte gefunden.)"
            else:
                recipe_context = "\n\n(Rezeptmodus ist aktiv, aber es konnten keine Rezeptdaten geladen werden.)"

        # Erweitere die Systemnachricht mit dem aktuellen Kontext (Angebote + ggf. gefilterte Rezepte)
        context_message = {
            "role": "system", 
            "content": f"Hier sind die aktuellen Produktinformationen (Angebote). Du DARFST NUR diese Produkte in deinen Antworten verwenden und KEINE anderen:\n\n{products_context}\n\n"
            f"{recipe_context}" # Rezeptkontext hier einfügen
            "WICHTIG: DENKE AKTIV und GRÜNDLICH über die Anfrage und Produktkategorien nach. " +
            "Erkenne semantische Beziehungen zwischen verschiedenen Produktbezeichnungen und Kategorien. " +
            "Wenn z.B. ein 'GUT BIO Bio-Pasta' Produkt in den Daten enthalten ist und jemand nach 'Nudeln' fragt, " +
            "dann ist dieses Produkt definitiv relevant und sollte genannt werden. " +
            "Bei Pasta/Nudeln-Produkten achte auf alle Varianten wie Tortelloni, Farfalle, Spaghetti etc. - " +
            "alle diese Produkte gehören zur Kategorie 'Nudeln'. " +
            "Denke selbständig und nutze dein Lebensmittelwissen.\n\n" +
            "WICHTIG: Verweise in deinen Antworten NIEMALS auf Angebotsbroschüren, Flyer oder andere externe Quellen. " +
            "Verwende ausschließlich die oben aufgeführten Produktdaten."
        }
        
        return system_prompt, context_message, products_context
        
    except Exception as e:
        return None, None, str(e) 