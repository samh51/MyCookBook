import os
import time
import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import streamlit as st
from .utils import PLACEHOLDER_IMG

# --- KONFIGURATION ---
# Versuche API Key aus Secrets zu laden, sonst Fallback auf den Hardcoded Key (für lokales Testen)
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "AIzaSyD5YahUeVmJgAI7cEfxplcD_Re16L8HMIM" 

# Kategorien für die KI-Zuordnung
CATEGORIES = ["Fleisch", "Fisch", "Hühnchen", "Vegetarisch", "Vegan", "Pasta", "Reis", "Dessert", "Vorspeise", "Frühstück", "Sonstiges"]

# --- HELFER FUNKTIONEN ---

def clean_json_response(text):
    """
    Entfernt Markdown-Formatierungen (```json ... ```) aus dem KI-Antworttext,
    damit json.loads() nicht abstürzt.
    """
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()

def get_video_id_youtube(url):
    """Extrahiert die Video-ID aus verschiedenen YouTube-Link-Formaten"""
    try:
        if "[youtube.com/shorts/](https://youtube.com/shorts/)" in url: return url.split("shorts/")[1].split("?")[0]
        elif "[youtube.com/watch?v=](https://youtube.com/watch?v=)" in url: return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url: return url.split("youtu.be/")[1].split("?")[0]
    except: return None
    return None

def get_web_content(url):
    """
    Lädt Metadaten und Audio/Text von YouTube, TikTok oder Instagram.
    Versucht erst Transkripte, dann Audio-Download.
    """
    thumbnail_url = None
    content_path = None
    error_msg = None
    
    # Prüfe auf Cookies Datei für robustere Downloads (Insta/TikTok)
    cookie_file = "cookies.txt"
    has_cookies = os.path.exists(cookie_file)
    
    ydl_opts_base = {
        'quiet': True, 
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    if has_cookies: 
        ydl_opts_base['cookiefile'] = cookie_file

    # 1. Metadaten (Thumbnail) holen
    try:
        with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
            info = ydl.extract_info(url, download=False)
            thumbnail_url = info.get('thumbnail')
    except Exception as e:
        print(f"Metadaten Warnung: {e}")
        thumbnail_url = PLACEHOLDER_IMG

    # 2. YouTube Transkript Versuch (Schneller als Audio Download)
    yt_id = get_video_id_youtube(url)
    if yt_id:
        try:
            # Versuche Transkripte in verschiedenen Sprachen zu finden
            transcript = YouTubeTranscriptApi.get_transcript(yt_id, languages=['en', 'de', 'es', 'fr', 'it', 'pl'])
            text = " ".join([t['text'] for t in transcript])
            return f"TRANSCRIPT: {text}", thumbnail_url, None
        except: 
            pass # Fallback auf Audio Download

    # 3. Audio Download (Falls kein Transkript oder andere Plattform)
    try:
        temp_filename = f"temp_audio_{int(time.time())}.m4a"
        
        ydl_opts_download = ydl_opts_base.copy()
        ydl_opts_download.update({
            'format': 'bestaudio/best',
            'outtmpl': temp_filename,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }],
        })
        
        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            ydl.extract_info(url, download=True)
            
            if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                content_path = temp_filename
            else:
                error_msg = "Datei leer (Login erforderlich?)."
                
    except Exception as e:
        error_msg = f"Download Fehler: {e}"

    return content_path, thumbnail_url, error_msg

# --- KI FUNKTIONEN ---

def rezept_analysieren(content, img_url, original_url, is_file=False):
    """
    Analysiert Text (Transkript) oder Audio Datei mit Gemini Pro/Flash
    und extrahiert ein strukturiertes JSON Rezept.
    """
    if not GEMINI_API_KEY or "HIER" in GEMINI_API_KEY:
        st.error("⚠️ API Key fehlt!"); return None

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest') 
    
    cat_str = ", ".join(CATEGORIES)
    
    prompt = f"""
    Du bist ein Profi-Koch. Analysiere das Rezept aus dem Input.
    
    WICHTIG: 
    1. Schätze Portionen (Default: 2) und Makros PRO PORTION (inkl. Zubereitungsart).
    2. Ordne das Gericht EINER dieser Kategorien zu: {cat_str}. Wenn unsicher, nimm 'Sonstiges'.
    
    Antworte NUR mit reinem JSON (kein Markdown):
    {{
      "Rezept": "Name des Gerichts", 
      "Portionen": Zahl, 
      "Kategorie": "Kategorie Name",
      "Makros": {{"Kcal": Zahl, "Protein": Zahl, "Carbs": Zahl, "Fett": Zahl}},
      "Zutaten": [{{"Zutat": "Name", "Menge": Zahl, "Einheit": "g/ml/Stk"}}],
      "Schritte": ["Schritt 1", "Schritt 2"]
    }}
    """
    try:
        if is_file and os.path.exists(content):
            # Datei Upload zu Google
            myfile = genai.upload_file(content)
            
            # Warten bis Verarbeitung fertig
            while myfile.state.name == "PROCESSING":
                time.sleep(1)
                myfile = genai.get_file(myfile.name)
                
            response = model.generate_content([prompt, myfile])
        else:
            # Text Input
            response = model.generate_content(f"{prompt}\n\nInput:\n{content}")
            
        # JSON Cleaning
        json_text = clean_json_response(response.text)
        data = json.loads(json_text)
        
        # Metadaten hinzufügen
        data["BildURL"] = img_url if img_url else PLACEHOLDER_IMG
        data["OriginalURL"] = original_url if original_url else ""
        
        # Kategorie Check
        if "Kategorie" not in data or data["Kategorie"] not in CATEGORIES:
            data["Kategorie"] = "Sonstiges"
            
        return data

    except Exception as e:
        st.error(f"KI Fehler: {e}")
        return None

def makros_neu_berechnen(zutaten_text, schritte_text, portionen):
    """Berechnet Nährwerte basierend auf manuell editierten Zutaten"""
    if not GEMINI_API_KEY: return None
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Berechne die Nährwerte **PRO PORTION**.
    Gesamt: {portionen} Portionen.
    
    Zutaten:
    {zutaten_text}
    
    Zubereitung:
    {schritte_text}
    
    Antworte NUR mit JSON:
    {{"Kcal": int, "Protein": int, "Carbs": int, "Fett": int}}
    """
    try:
        response = model.generate_content(prompt)
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except Exception as e:
        st.error(f"KI Fehler: {e}")
        return None

def translate_recipe_text(data, target_lang):
    """
    Übersetzt die Text-Teile des Rezept-JSONs in die Zielsprache.
    Behält die JSON Struktur exakt bei.
    """
    if not GEMINI_API_KEY: return data
    
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Translate the content of this JSON to {target_lang}.
    IMPORTANT:
    1. Keep the JSON structure EXACTLY the same.
    2. Only translate values for keys: "Rezept", "Zutat", "Einheit", "Kategorie" and the strings in the "Schritte" list.
    3. Do NOT translate the keys themselves (e.g. keep "Zutaten", "Makros" as keys).
    4. Return ONLY raw JSON.

    Input JSON:
    {json.dumps(data)}
    """
    try:
        response = model.generate_content(prompt)
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except Exception as e:
        print(f"Translation Error: {e}")
        return data # Im Fehlerfall Original zurückgeben