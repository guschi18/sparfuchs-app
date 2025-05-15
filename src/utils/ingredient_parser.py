import re

# Regex zum Entfernen von Mengenangaben und Einheiten am Anfang
# Erfasst Zahlen (ganz oder mit Komma/Punkt), optionale Leerzeichen und gängige Einheiten
RE_QUANTITY_UNIT = r"^\s*\d+([,\.]\d+)?\s*(g|kg|ml|l|Stk\.?|EL|TL|Prise|Bund|Blatt|Zehe|Pck\.?|Dose|Becher|Stange|Scheibe[n]?|cm|Spritzer|Handvoll|Stück|eine|einige|etwas|ca\.|halbe[r]?|ganze[r]?|eine halbe|ein ganzer)*\s*"

# Gängige Einheiten und Wörter, die oft mit Mengenangaben verbunden sind
# und entfernt werden sollen, auch wenn sie nicht am Anfang stehen
COMMON_UNITS_WORDS = [
    "g", "kg", "ml", "l", "Stk", "EL", "TL", "Prise", "Bund", "Blatt", "Zehe",
    "Pck", "Dose", "Becher", "Stange", "Scheibe", "Scheiben", "cm", "Spritzer",
    "Handvoll", "Stück", "eine", "einige", "etwas", "ca.", "halbe", "halber", "halbes", "ganze", "ganzer", "ganzes"
]

# Wörter, die Zubereitungsarten oder Zustände beschreiben
PREPARATION_WORDS = [
    "gekocht", "roh", "gewürfelt", "gehackt", "frisch", "getrocknet", "gemahlen",
    "light", "fein", "grob", "halbiert", "gepresst", "flüssig", "zerkleinert",
    "gerieben", "geschält", "entkernt", "ausgelöst", "paniert", "mariniert",
    "gebraten", "gedünstet", "blanchiert", "püriert", "abgetropft", "aufgetaut",
    "geviertelt", "geschnitten", "klein geschnitten", "grob gehackt", "fein gehackt",
    "in Scheiben", "in Würfel", "in Streifen", "zum Kochen", "zum Braten",
    "optional", "nach Belieben", "oder", "evtl.", "z.B.", "bzw.",
    # Farben und Zustände, die oft bei Gemüse vorkommen und entfernt werden können,
    # wenn sie vor dem eigentlichen Gemüsenamen stehen (vorsichtig verwenden!)
    "rote", "roter", "rotes", "gelbe", "gelber", "gelbes", "grüne", "grüner", "grünes",
    "kleine", "kleiner", "kleines", "große", "großer", "großes", "normale", "normaler", "normales"
]

# Wörter, die oft in Klammern stehen oder spezifische Produktmerkmale beschreiben
# und entfernt werden sollen, um zum Kernprodukt zu gelangen.
# Diese Liste kann erweitert werden.
SPECIFIC_PRODUCT_MODIFIERS = [
    "Billie Green", "Veggie", "Bio", "more Protein", "aus der Mühle",
    "aus dem Glas", "aus der Dose", "TK", "tiefgekühlt"
]


def _clean_ingredient_string(ingredient_text: str) -> str:
    """
    Bereinigt einen einzelnen Zutaten-String, um den Hauptnamen zu extrahieren.
    """
    text = ingredient_text.strip()

    # Vorverarbeitung für "oder"-Alternativen:
    if " oder " in text.lower():
        parts = re.split(r'\s+oder\s+', text, maxsplit=1, flags=re.IGNORECASE)
        text = parts[0]

    # 1. Mengen und Einheiten am Anfang entfernen
    text = re.sub(RE_QUANTITY_UNIT, "", text, flags=re.IGNORECASE).strip()

    # 2. Text in Klammern entfernen
    text = re.sub(r"\(.*?\)", "", text).strip()

    # 3. Gängige Einheiten und spezifische Produktmodifikatoren entfernen (Wort für Wort)
    words_to_remove_exact = COMMON_UNITS_WORDS + SPECIFIC_PRODUCT_MODIFIERS
    for word in words_to_remove_exact:
        text = re.sub(r"\b" + re.escape(word) + r"\b", "", text, flags=re.IGNORECASE).strip()

    # 4. Zubereitungsarten/Zustände entfernen (Wort für Wort)
    for word in PREPARATION_WORDS:
        text = re.sub(r"\b" + re.escape(word) + r"\b", "", text, flags=re.IGNORECASE).strip()
        # Auch mit Bindestrich verbundene Varianten, z.B. "klein-geschnitten"
        text = re.sub(r"\b" + re.escape(word.replace(" ", "-")) + r"\b", "", text, flags=re.IGNORECASE).strip()

    # 5. Spezifische Phrasen und Reste entfernen
    phrases_to_remove = [
        "vom Vortag", "nach Wahl", "je nach Größe", "ggf.", "und", ",", ";",
        # "oder normale", "oder normaler", "oder normales" # Entfernt, da "oder" jetzt anders behandelt wird
        # "normale", "normaler", "normales" sind jetzt in PREPARATION_WORDS
    ]
    for phrase in phrases_to_remove:
        text = text.replace(phrase, "")

    # 6. Zahlen, die jetzt möglicherweise isoliert sind, entfernen
    text = re.sub(r"\b\d+([,\.]\d+)?\b", "", text) # Ganze Zahlen oder Zahlen mit Komma/Punkt
    text = re.sub(r"\d+", "", text) # Alle verbleibenden Ziffern

    # 7. Mehrfache Leerzeichen durch ein einzelnes ersetzen und trimmen
    text = re.sub(r"\s+", " ", text).strip()

    # 8. Übrig gebliebene Satzzeichen am Anfang oder Ende entfernen
    text = text.strip(" ,;-.")

    # 9. Manchmal bleiben Reste wie "Schinkenwürfel Schinken Würfel". Versuche, Duplikate zu reduzieren,
    #    indem man den String in Wörter teilt, eindeutige Wörter nimmt und wieder zusammenfügt.
    #    Dies ist eine Heuristik und könnte verfeinert werden.
    if len(text.split()) > 1 and len(set(text.lower().split())) < len(text.split()):
        # Beispiel: "Schinkenwürfel Schinken Würfel" -> unique_words = ["schinkenwürfel", "schinken", "würfel"]
        # Dies ist nicht ideal, wenn "Schinken Würfel" als Einheit gemeint ist. 
        # Besser ist es, wenn die vorherigen Schritte schon sauberer sind.
        # Für den Fall "Schinkenwürfel Schinken Würfel" soll es zu "Schinkenwürfel" werden, wenn "Schinkenwürfel" der erste Begriff ist.
        # Wenn der erste Begriff im weiteren Verlauf wiederholt wird, ist das oft ein Zeichen für eine nicht saubere Extraktion.
        # Eine einfache Heuristik: Wenn der erste Begriff (z.B. "Schinkenwürfel") später nochmal vorkommt (z.B. in "Schinken"),
        # dann behalte nur den ersten Begriff. Diese Logik ist noch nicht implementiert.
        # Stattdessen: Wenn nach allen Bereinigungen der String immer noch Leerzeichen enthält
        # und der erste Teil des Strings (vor dem ersten Leerzeichen) ein plausibler Kandidat ist,
        # und dieser Kandidat im Rest des Strings vorkommt (evtl. in abgewandelter Form), dann nur den ersten Teil nehmen.
        # Beispiel: "Schinkenwürfel schinken würfel"
        # Hier ist "Schinkenwürfel" der erste Teil.
        # Wenn "Schinkenwürfel" bereits das gewünschte Ergebnis ist, sollten die vorherigen Schritte das liefern.
        # Die aktuelle Ausgabe "Schinkenwürfel schinken würfel" ist das Problem.
        # Wir versuchen, solche Redundanzen zu entfernen.
        words = text.split()
        if len(words) > 1:
            # Wenn der erste Begriff (z.B. Schinkenwürfel) im Rest des Strings enthalten ist
            # (z.B. "Schinkenwürfel" in "schinken würfel" - nicht direkt, aber semantisch)
            # Für den Moment eine direktere Vereinfachung: wenn der erste Begriff der längste ist und andere Begriffe Teile davon sind.
            # Oder: Wenn es mehrere Wörter gibt und der erste Teil ein Substring des Ganzen ist.
            # Spezifisch für "Schinkenwürfel schinken würfel":
            # Zerlege in Wörter, mache sie einzigartig (case-insensitive), füge sie wieder zusammen.
            # Dies hilft bei "Wort Wort" -> "Wort"
            unique_words_ordered = list(dict.fromkeys(text.lower().split()))
            if unique_words_ordered:
                # Prüfe, ob der erste extrahierte Begriff (z.B. schinkenwürfel)
                # die anderen Begriffe (schinken, würfel) abdeckt.
                # Wenn ja, behalte nur den ersten.
                # Dies ist sehr heuristisch!
                first_word = unique_words_ordered[0]
                is_dominant = True
                if len(unique_words_ordered) > 1:
                    for other_word in unique_words_ordered[1:]:
                        if other_word not in first_word:
                            is_dominant = False
                            break
                    if is_dominant:
                        text = first_word
                    else: # Fallback, wenn nicht dominant, nimm die einzigartigen Wörter
                        text = " ".join(unique_words_ordered)
                else:
                    text = first_word # Nur ein einzigartiges Wort

    return text.capitalize() # Kapitalisierung am Ende der gesamten Bereinigung


def extract_main_ingredients(ingredients_string: str) -> list[str]:
    """
    Extrahiert Hauptzutaten aus einem kommaseparierten String von Zutaten.

    Args:
        ingredients_string: Ein String, der Zutaten enthält, getrennt durch Semikolons.
                           Beispiel: "250g Kartoffeln gekocht (roh gewogen); 250g Zucchini; ..."

    Returns:
        Eine Liste von extrahierten und bereinigten Hauptzutaten-Namen (Strings).
        Duplikate werden entfernt und nur Zutaten mit Inhalt zurückgegeben.
    """
    if not ingredients_string or not isinstance(ingredients_string, str):
        return []

    individual_ingredients = ingredients_string.split(';')
    main_ingredients = set()

    for ingredient_part in individual_ingredients:
        if not ingredient_part.strip():
            continue

        cleaned_name = _clean_ingredient_string(ingredient_part)

        if cleaned_name and len(cleaned_name) > 1: # Nur sinnvolle Namen hinzufügen
            main_ingredients.add(cleaned_name) # Kapitalisierung erfolgt jetzt in _clean_ingredient_string

    return sorted(list(main_ingredients))


if __name__ == '__main__':
    # Testfälle
    test_cases = [
        "250g Kartoffeln gekocht (roh gewogen); 250g Zucchini; 1 Zwiebel; 2 Knoblauchzehen; 1 EL Olivenöl; Salz; Pfeffer",
        "1 halbe Gurke; 1 rote Paprika; 100g Feta light",
        "30g Veggie Schinkenwürfel (Billie Green) oder normale light Schinken Würfel; 1 Ei (Größe M)",
        "halbe rote Zwiebel",
        "Zwiebel rote große",
        "Schinken oder Schinkenwürfel",
        "Veggie Wurstaufschnitt oder Putenbrust",
        "500g Mehl; 1 Pck. Trockenhefe; 1 TL Zucker; 1 TL Salz; 300ml lauwarmes Wasser",
        "2 Stk. Hähnchenbrustfilet (ca. 300g); 1 EL Paprikapulver edelsüß",
        "1 Dose gehackte Tomaten (400g); 1 Bund Basilikum frisch",
        "1 kleiner Brokkoli; 2 Karotten, geschält und gewürfelt",
        "250 ml Gemüsebrühe (instant); 1 Prise Muskatnuss",
        "1 Zwiebel, fein gehackt; 2 EL Tomatenmark",
        "Nudeln nach Wahl (ca. 200g); Salz zum Kochen",
        "1/2 Zitrone (Saft davon); etwas Olivenöl",
        "1 rote Zwiebel; ca. 50g Rucola",
        "2 Scheiben Vollkorntoast; Frischkäse; Kresse",
        "1  reife Mango; 200 g  Naturjoghurt (1,5 % Fett); 1 EL  Honig; einige  Minzblätter",
        "125 g Couscous; 250 ml Gemüsebrühe, heiß; 1/2 rote Paprika, gewürfelt; 1/2 gelbe Paprika, gewürfelt; 1/4 Gurke, gewürfelt; 2 Frühlingszwiebeln, in Ringen; Saft von 1/2 Zitrone; 2 EL Olivenöl; Salz; Pfeffer; frische Petersilie, gehackt"
    ]

    expected_outputs = [
        ["Kartoffeln", "Knoblauchzehen", "Olivenöl", "Pfeffer", "Salz", "Zucchini", "Zwiebel"],
        ["Feta", "Gurke", "Paprika"],
        ["Ei", "Schinkenwürfel"],
        ["Zwiebel"],
        ["Zwiebel"],
        ["Schinken"],
        ["Wurstaufschnitt"],
        ["Mehl", "Salz", "Trockenhefe", "Wasser", "Zucker"],
        ["Hähnchenbrustfilet", "Paprikapulver edelsüß"],
        ["Basilikum", "Tomaten"],
        ["Brokkoli", "Karotten"],
        ["Gemüsebrühe", "Muskatnuss"],
        ["Tomatenmark", "Zwiebel"],
        ["Nudeln", "Salz"],
        ["Olivenöl", "Zitrone"],
        ["Rucola", "Zwiebel"],
        ["Frischkäse", "Kresse", "Vollkorntoast"],
        ["Honig", "Mango", "Minzblätter", "Naturjoghurt"],
        ["Couscous", "Frühlingszwiebeln", "Gemüsebrühe", "Gurke", "Olivenöl", "Paprika", "Petersilie", "Pfeffer", "Salz", "Zitrone"]
    ]

    for i, tc in enumerate(test_cases):
        result = extract_main_ingredients(tc)
        print(f"Testfall: '{tc}'")
        print(f"Extrahiert: {result}")
        if i < len(expected_outputs):
            print(f"Erwartet:   {expected_outputs[i]}")
            if sorted(result) == sorted(expected_outputs[i]):
                print("Status: CORRECT")
            else:
                print(f"Status: INCORRECT - Erwartet {expected_outputs[i]}, bekommen {result}")
        else:
            print("Status: (Kein erwartetes Ergebnis definiert)")

    # Zusätzlicher Testfall für "30g Veggie Schinkenwürfel (Billie Green) oder normale light Schinken Würfel"
    specific_test = "30g Veggie Schinkenwürfel (Billie Green) oder normale light Schinken Würfel"
    print(f"Spezifischer Testfall: '{specific_test}'")
    result_specific = extract_main_ingredients(specific_test)
    print(f"Extrahiert: {result_specific}")
    # Erwartet: ["Schinkenwürfel"] oder ["Schinken", "Würfel"] - je nach Granularität.
    # Mit der aktuellen Logik sollte es eher "Schinkenwürfel" sein.
    print(f"Erwartet (ungefähr): ['Schinkenwürfel']")

    complex_ingredient = "30g Veggie Schinkenwürfel (Billie Green) oder normale light Schinken Würfel"
    print(f"Einzeltest: '{complex_ingredient}' -> '{_clean_ingredient_string(complex_ingredient)}'")
    complex_ingredient_2 = "250g Kartoffeln gekocht (roh gewogen)"
    print(f"Einzeltest: '{complex_ingredient_2}' -> '{_clean_ingredient_string(complex_ingredient_2)}'")
    complex_ingredient_3 = "1 EL Paprikapulver edelsüß"
    print(f"Einzeltest: '{complex_ingredient_3}' -> '{_clean_ingredient_string(complex_ingredient_3)}'")
    complex_ingredient_4 = "Salz zum Kochen"
    print(f"Einzeltest: '{complex_ingredient_4}' -> '{_clean_ingredient_string(complex_ingredient_4)}'")
    single_test_zwiebel = "halbe rote Zwiebel"
    print(f"Einzeltest Zwiebel: '{single_test_zwiebel}' -> '{_clean_ingredient_string(single_test_zwiebel)}'")
    single_test_schinken = "30g Veggie Schinkenwürfel (Billie Green) oder normale light Schinken Würfel"
    print(f"Einzeltest Schinken: '{single_test_schinken}' -> '{_clean_ingredient_string(single_test_schinken)}'")
    single_test_paprika = "1 rote Paprika"
    print(f"Einzeltest Paprika: '{single_test_paprika}' -> '{_clean_ingredient_string(single_test_paprika)}'")
    problem_schinken = "Veggie Schinkenwürfel (Billie Green)" # Direkter Test nach "oder"-Split
    print(f"Problemfall Schinken: '{problem_schinken}' -> '{_clean_ingredient_string(problem_schinken)}'") 