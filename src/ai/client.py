"""
OpenRouter-Client und KI-Verbindungsfunktionen für SparFuchs.de.

Dieses Modul enthält Funktionen für die Initialisierung und Verwendung des
OpenRouter-Clients zur Kommunikation mit KI-Modellen.
"""
import os
import sys
import httpx
from openai import OpenAI
from dotenv import load_dotenv

def init_client():
    """
    Initialisiert und konfiguriert den OpenAI-Client für OpenRouter.
    
    Die Funktion lädt Umgebungsvariablen und erstellt einen OpenAI-Client,
    der über die OpenRouter-API kommuniziert.
    
    Returns:
        OpenAI: Konfigurierter OpenAI-Client mit OpenRouter als Basis-URL
    """
    # Umgebungsvariablen laden
    load_dotenv()
    
    # API-Schlüssel überprüfen
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    # Versuche verschiedene Methoden für die OpenAI-Client-Initialisierung
    # Methode 1: Client-Initialisierung mit explizitem HTTP-Client ohne Proxies
    try:
        # Umgebungsvariablen für Proxy deaktivieren, bevor wir OpenAI initialisieren
        os.environ["no_proxy"] = "*"
        if "http_proxy" in os.environ:
            del os.environ["http_proxy"]
        if "https_proxy" in os.environ:
            del os.environ["https_proxy"]
        
        # HTTP-Client ohne Proxies erstellen
        transport = httpx.HTTPTransport(retries=3)
        http_client = httpx.Client(transport=transport)
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",  # OpenRouter API-Basis-URL
            http_client=http_client
        )
        return client
    except Exception as e:
        print(f"Fehler bei Methode 1: {e}")
        
        # Methode 2: Client mit manuellem Transport
        try:
            # Erstellen eines httpx-Clients ohne Proxy
            transport = httpx.HTTPTransport(retries=3)
            client = OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                http_client=httpx.Client(transport=transport)
            )
            return client
        except Exception as e:
            print(f"Fehler bei Methode 2: {e}")
            
            # Methode 3: Minimum-Konfiguration
            try:
                client = OpenAI(api_key=api_key)
                client.base_url = "https://openrouter.ai/api/v1"
                return client
            except Exception as e:
                print(f"Fehler bei Methode 3: {e}")
                
                # Fallback: Anzeigen wovon die Fehler kommen
                import traceback
                traceback.print_exc()
                raise RuntimeError("Konnte OpenAI-Client nicht initialisieren")

def get_available_models():
    """
    Gibt eine Liste der verfügbaren Modelle und ihre Eigenschaften zurück.
    
    Returns:
        list: Liste von Dictionaries mit Modellnamen und Eigenschaften
    """
    # Vordefinierte Liste der bekannten Modelle, die wir bevorzugt verwenden
    return [
        {
            "id": "x-ai/grok-3-mini-beta",
            "name": "xAI: Grok 3 Mini Beta",
            "context_length": 4000,
            "is_free": True
        }
    ] 