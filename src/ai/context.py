"""
Kontextgenerierung für KI-Anfragen.

Dieses Modul enthält Funktionen für die Erstellung von optimierten Kontexten
für KI-Anfragen basierend auf Benutzeranfragen und Produktdaten.
"""
import re
from ..data.product_data import get_filtered_products_context, load_recipes, load_csv_data
from ..utils.ingredient_parser import extract_main_ingredients
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

def get_recipe_system_prompt():
    """
    Erstellt den Systemprompt für die KI im Rezeptmodus.
    
    Der Systemprompt enthält klare Anweisungen und Formatierungsregeln
    für die KI, um zuverlässig auf Rezeptanfragen zu antworten.
    
    Returns:
        dict: Ein Dictionary mit dem Systemprompt im OpenAI-Format
    """
    system_prompt = {
        "role": "system",
        "content": "Du bist ein spezialisierter Rezeptassistent für SparFuchs.de. Deine Aufgabe ist es, Nutzern passende Rezepte basierend auf ihrer Anfrage und den dir bereitgestellten Rezeptdaten zu liefern. " +
                   "WICHTIG: Du darfst AUSSCHLIESSLICH die dir im Kontext übermittelten Rezeptdaten verwenden. " +
                   "Erfinde NIEMALS Rezepte, Zutaten oder Zubereitungsschritte. " +
                   "Verwende KEINE externen Quellen oder dein eigenes Wissen über andere Rezepte. " +
                   "Wenn du kein passendes Rezept in den bereitgestellten Daten findest, teile dies dem Nutzer klar mit. " +
                   "NEU: Du erhältst zusätzlich eine Liste mit relevanten Angeboten für die Hauptzutaten der gefundenen Rezepte. " +
                   "Präsentiere diese Angebote klar und deutlich im Anschluss an das jeweilige Rezept oder gesammelt, wenn mehrere Rezepte angezeigt werden. " +
                   "Weise darauf hin, dass es sich um Angebote für die *Hauptzutaten* handelt. " +
                   "FORMATIERUNGSANWEISUNGEN FÜR REZEPTE: " +
                   "1. Gib zuerst den **Rezeptnamen** an (Markdown Fett). " +
                   "2. Liste dann die **Zutaten** auf (Markdown Liste). " +
                   "3. Beschreibe danach die **Zubereitung** in klaren Schritten (Markdown nummerierte Liste). " +
                   "4. Nutze Markdown nur für die Rezept-Formatierung (Rezeptname, Zutaten, Zubereitung). " +
                   "5. FÜGE NACH DEM REZEPT EINEN ABSCHNITT '\n\n**PASSENDE ANGEBOTE FÜR HAUPTZUTATEN:**\n' HINZU (Markdown Fett für die Überschrift). " +
                   "   WICHTIG: Liste die gefundenen Angebote für die Hauptzutaten des Rezepts EXAKT im folgenden HTML-Format auf. Verwende KEIN Markdown für die Angebote selbst: " +
                   "   Für jedes Angebot verwende: " +
                   "   \n**PRODUKTNAME DES ANGEBOTS** (Details): PREIS €<br>" +
                   "   \n<strong class=\"meta-info\">Gültig:</strong> STARTDATUM bis ENDDATUM<br>" +
                   "   \n<strong class=\"meta-info\">Supermarkt:</strong> SUPERMARKTNAME<br>\n\n" +
                   "   Stelle sicher, dass JEDES dieser Elemente (Produkt, Gültig, Supermarkt) auf einer NEUEN ZEILE steht, getrennt durch explizite <br> HTML-Tags. KEINE Markdown-Listen oder normale Zeilenumbrüche für die Angebotsdetails verwenden!" +
                   "   Wenn für einige Hauptzutaten keine Angebote gefunden wurden, fasse dies am Ende des Angebotsabschnitts in einem Satz zusammen (z.B. 'Für Zutat X und Zutat Y wurden keine Angebote gefunden.'). " +
                   "Beispiel für ein Rezept MIT Angeboten (achte auf die exakte Formatierung der Angebote!): " +
                   "\n\n**Rezeptname:** Kartoffelsalat\n" +
                   "\n**Zutaten:**\n" +
                   "- 500g Kartoffeln festkochend\n" +
                   "- 1 Zwiebel\n" +
                   "- 100ml Gemüsebrühe\n" +
                   "- Essig, Öl, Salz, Pfeffer\n" +
                   "\n**Zubereitung:**\n" +
                   "1. Kartoffeln kochen, pellen und in Scheiben schneiden.\n" +
                   "2. Zwiebel fein würfeln.\n" +
                   "3. Gemüsebrühe, Essig, Öl, Salz und Pfeffer verrühren und über die Kartoffeln geben.\n" +
                   "\n\n**PASSENDE ANGEBOTE FÜR HAUPTZUTATEN:**\n" +
                   "\n**Speisefrühkartoffeln festkochend** (1,5 kg): 2,79 €<br>" +
                   "\n<strong class=\"meta-info\">Gültig:</strong> 24.07.2024 bis 26.07.2024<br>" +
                   "\n<strong class=\"meta-info\">Supermarkt:</strong> Aldi<br>\n\n" +
                   "Für Zwiebeln wurden keine Angebote gefunden.\n\n" +
                   "ANTWORTE IMMER AUF DEUTSCH."
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
        if recipe_mode:
            system_prompt = get_recipe_system_prompt()
        else:
            system_prompt = get_system_prompt()
        
        # Kontext aus der CSV-Datei holen (gefiltert basierend auf der Anfrage und ausgewählten Märkten)
        products_context = get_filtered_products_context(prompt, selected_markets)
        
        # Rezeptkontext hinzufügen, wenn der Modus aktiv ist
        raw_data_context = "" # Wird für Debugging oder spezifische Anzeige verwendet
        
        if recipe_mode:
            recipes_df = load_recipes()
            angebote_df = load_csv_data() # Geändert: load_processed_data zu load_csv_data
            
            context_message_content = "Es konnten keine Rezeptdaten geladen werden oder es wurden keine passenden Rezepte für deine Anfrage gefunden." # Standardnachricht
            
            if recipes_df.empty:
                context_message_content = "Ich konnte leider keine Rezepte-Datenbank laden."
            elif angebote_df.empty:
                context_message_content = "Ich konnte Rezepte laden, aber leider keine Angebots-Datenbank. Daher kann ich keine Angebote zu den Zutaten suchen."
            else:
                # Extrahiere Schlüsselwörter aus dem Prompt (mind. 3 Zeichen)
                prompt_lower = prompt.lower()
                keywords = re.findall(r'\b\w{3,}\b', prompt_lower)
                
                filtered_recipes_df = pd.DataFrame() # Initialisiere leeren DataFrame

                if keywords:
                    # Annahme: Die relevanten Spalten heißen 'Rezeptname' und 'Zutaten'
                    # Passe dies bei Bedarf an die tatsächlichen Spaltennamen in More_Rezepte.csv an.
                    search_columns = ['Rezeptname', 'Zutaten', 'Zubereitung'] 
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
                    # Konvertiere das DataFrame in ein besser lesbares Format für die KI
                    # Hier gehen wir davon aus, dass die Spalten 'Rezeptname', 'Zutaten', 'Zubereitung' existieren.
                    # Du musst dies eventuell an deine CSV-Struktur anpassen.
                    recipe_text_parts = []
                    all_main_ingredients_from_found_recipes = set() # Sammelt alle Hauptzutaten

                    for _, row in filtered_recipes_df.iterrows():
                        part = ""
                        current_recipe_main_ingredients = []
                        if 'Rezeptname' in row and pd.notna(row['Rezeptname']):
                            part += f"Rezept: {row['Rezeptname']}\n"
                        if 'Zutaten' in row and pd.notna(row['Zutaten']):
                            part += f"Zutaten: {row['Zutaten']}\n"
                            # Hauptzutaten für dieses spezifische Rezept extrahieren
                            current_recipe_main_ingredients = extract_main_ingredients(row['Zutaten'])
                            all_main_ingredients_from_found_recipes.update(current_recipe_main_ingredients)
                        if 'Zubereitung' in row and pd.notna(row['Zubereitung']):
                            part += f"Zubereitung: {row['Zubereitung']}\n"
                        
                        # Angebotssuche für die Hauptzutaten DIESES Rezepts (optional, wenn man Angebote pro Rezept will)
                        # Für diese Implementierung suchen wir global für alle gefundenen Rezepte weiter unten.
                        # Hier könnte man aber auch Angebote pro Rezept direkt an `part` anhängen.

                        if part: # Nur hinzufügen, wenn mindestens ein Teil vorhanden ist
                             recipe_text_parts.append(part)
                    
                    # Angebots-Sektion für die KI vorbereiten
                    angebote_fuer_zutaten_text = "\n\nRELEVANTE ANGEBOTE FÜR HAUPTZUTATEN:\n"
                    found_any_offer_for_ingredients = False

                    if not all_main_ingredients_from_found_recipes:
                        angebote_fuer_zutaten_text += "Es konnten keine Hauptzutaten aus den Rezepten extrahiert werden, um nach Angeboten zu suchen.\n"
                    else:
                        # Angebotsdaten filtern, falls Märkte ausgewählt wurden
                        if selected_markets:
                            angebote_df_filtered_markets = angebote_df[angebote_df['Supermarkt'].isin(selected_markets)].copy()
                        else:
                            angebote_df_filtered_markets = angebote_df.copy()

                        if angebote_df_filtered_markets.empty and selected_markets:
                            angebote_fuer_zutaten_text += f"Ich habe keine Angebote in den ausgewählten Märkten ({', '.join(selected_markets)}) gefunden.\n"
                        elif angebote_df_filtered_markets.empty:
                             angebote_fuer_zutaten_text += "Ich habe aktuell keine Angebote in meiner Datenbank.\n"
                        else:
                            # Datumsspalten korrekt formatieren, falls sie nicht bereits Strings sind
                            for col in ['Startdatum', 'Enddatum']:
                                if col in angebote_df_filtered_markets.columns and not pd.api.types.is_string_dtype(angebote_df_filtered_markets[col]):
                                    try:
                                        angebote_df_filtered_markets[col] = pd.to_datetime(angebote_df_filtered_markets[col]).dt.strftime('%d.%m.%Y')
                                    except Exception:
                                        # Fallback, falls Konvertierung fehlschlägt, als String belassen
                                        angebote_df_filtered_markets[col] = angebote_df_filtered_markets[col].astype(str)
                            
                            offers_for_prompt = []
                            missing_ingredients_offers = list(all_main_ingredients_from_found_recipes) # Kopie für die Verfolgung

                            for zutat in sorted(list(all_main_ingredients_from_found_recipes)):
                                zutat_lower = zutat.lower()
                                # Suche in Produktname, Kategorie, Unterkategorie
                                # pd.Series.str.contains() erwartet, dass die Spalte String-Typ ist. Konvertiere bei Bedarf.
                                # Wir stellen sicher, dass Spalten existieren und Strings sind, bevor wir .str.contains verwenden
                                produkt_mask = pd.Series(False, index=angebote_df_filtered_markets.index)
                                if 'Produktname' in angebote_df_filtered_markets.columns and pd.api.types.is_string_dtype(angebote_df_filtered_markets['Produktname']):
                                    produkt_mask |= angebote_df_filtered_markets['Produktname'].str.contains(zutat_lower, case=False, na=False)
                                
                                kategorie_mask = pd.Series(False, index=angebote_df_filtered_markets.index)
                                if 'Kategorie' in angebote_df_filtered_markets.columns and pd.api.types.is_string_dtype(angebote_df_filtered_markets['Kategorie']):
                                    kategorie_mask |= angebote_df_filtered_markets['Kategorie'].str.contains(zutat_lower, case=False, na=False)
                                
                                unterkategorie_mask = pd.Series(False, index=angebote_df_filtered_markets.index)
                                if 'Unterkategorie' in angebote_df_filtered_markets.columns and pd.api.types.is_string_dtype(angebote_df_filtered_markets['Unterkategorie']):
                                    unterkategorie_mask |= angebote_df_filtered_markets['Unterkategorie'].str.contains(zutat_lower, case=False, na=False)
                                
                                combined_mask = produkt_mask | kategorie_mask | unterkategorie_mask
                                passende_angebote = angebote_df_filtered_markets[combined_mask]

                                if not passende_angebote.empty:
                                    found_any_offer_for_ingredients = True
                                    if zutat in missing_ingredients_offers:
                                        missing_ingredients_offers.remove(zutat)
                                    
                                    for _, angebot_row in passende_angebote.iterrows():
                                        offers_for_prompt.append(
                                            f"**{angebot_row.get('Produktname', 'N/A')}**: {angebot_row.get('Preis_EUR', 'N/A')} €<br>\n" +
                                            f"<strong class=\"meta-info\">Gültig:</strong> {angebot_row.get('Startdatum', 'N/A')} bis {angebot_row.get('Enddatum', 'N/A')}<br>\n" +
                                            f"<strong class=\"meta-info\">Supermarkt:</strong> {angebot_row.get('Supermarkt', 'N/A')}<br>\n\n"
                                        )
                                else:
                                    pass

                            if offers_for_prompt:
                                angebote_fuer_zutaten_text += "".join(offers_for_prompt)
                            
                            # Behandlung von Zutaten ohne Angebote am Ende zusammenfassen
                            if missing_ingredients_offers:
                                if not offers_for_prompt: # Falls noch gar keine Angebote aufgelistet wurden, ggf. einen Umbruch.
                                     angebote_fuer_zutaten_text += "\n" 
                                
                                if len(missing_ingredients_offers) == 1:
                                    angebote_fuer_zutaten_text += f"Für {missing_ingredients_offers[0]} wurden keine Angebote gefunden.\n\n"
                                elif len(missing_ingredients_offers) > 1:
                                    # Sortiere die Liste für eine konsistente Ausgabe
                                    sorted_missing_ingredients = sorted(list(missing_ingredients_offers))
                                    zutaten_str = ", ".join(sorted_missing_ingredients[:-1]) + f" und {sorted_missing_ingredients[-1]}"
                                    angebote_fuer_zutaten_text += f"Für {zutaten_str} wurden keine Angebote gefunden.\n\n"
                                # Wenn missing_ingredients_offers leer ist, wird hier nichts hinzugefügt.
                                                                
                            if not found_any_offer_for_ingredients and all_main_ingredients_from_found_recipes and not missing_ingredients_offers:
                                # Dieser Fall ist jetzt unwahrscheinlicher. Er würde eintreten, wenn es extrahierte Zutaten gab,
                                # found_any_offer_for_ingredients false ist, ABER missing_ingredients_offers leer ist (was bedeutet, für alle wurde was gefunden - Widerspruch)
                                # oder wenn all_main_ingredients_from_found_recipes leer war (dann sollte die Meldung nicht kommen)
                                # Daher entfernen wir diese spezifische, nun wahrscheinlich redundante oder irreführende Meldung.
                                # angebote_fuer_zutaten_text += "Es wurden insgesamt keine passenden Angebote für die extrahierten Hauptzutaten der Rezepte gefunden.\n"
                                pass # Keine allgemeine "nichts gefunden" Nachricht hier, wenn spezifische Nachrichten existieren oder keine Zutaten da waren.

                    if recipe_text_parts:
                        raw_data_context = "\n\n---\n\n".join(recipe_text_parts)
                        context_message_content = f"Hier sind die Rezeptdaten, die zu deiner Anfrage passen könnten. Bitte nutze NUR diese Daten, um deine Antwort zu formulieren:\n\n{raw_data_context}"
                        context_message_content += angebote_fuer_zutaten_text # Füge Angebotsinfos hinzu
                    else:
                        context_message_content = "Ich habe zwar Rezepte geladen, aber nach Filterung anhand deiner Anfrage keine passenden gefunden. Frage gerne spezifischer oder anders."
            
            context_message = {
                "role": "system", # Wichtig: Auch hier "system" verwenden, damit die KI es als strikte Anweisung nimmt
                "content": context_message_content
            }
            # Im Rezeptmodus geben wir keinen products_context im bisherigen Sinne zurück,
            # sondern die aufbereiteten Rezeptdaten als raw_data_context für potenzielle Anzeige/Debug.
            # Der 'products_context' für die Angebotslogik wird hier irrelevant.
            return system_prompt, context_message, raw_data_context # Rückgabe für Rezeptmodus

        # Folgender Block nur für Angebotsmodus (recipe_mode == False)
        context_message = {
            "role": "system", 
            "content": f"Hier sind die aktuellen Produktinformationen (Angebote). Du DARFST NUR diese Produkte in deinen Antworten verwenden und KEINE anderen:\n\n{products_context}\n\n"
            # Der recipe_context wird hier nicht mehr benötigt, da recipe_mode false ist.
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
        
        return system_prompt, context_message, products_context # Rückgabe für Angebotsmodus
        
    except Exception as e:
        return None, None, str(e) 