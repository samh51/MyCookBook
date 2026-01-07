import os
import time
import json
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import streamlit as st
import random
from .utils import PLACEHOLDER_IMG

# --- KONFIGURATION ---
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    GEMINI_API_KEY = "AIzaSyD5YahUeVmJgAI7cEfxplcD_Re16L8HMIM" 

CATEGORIES = ["Fleisch", "Fisch", "Hühnchen", "Vegetarisch", "Vegan", "Pasta", "Reis", "Dessert", "Vorspeise", "Frühstück", "Sonstiges"]

# --- HELFER FUNKTIONEN ---

def clean_json_response(text):
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip()

def get_video_id_youtube(url):
    try:
        if "youtube.com/shorts/" in url: return url.split("shorts/")[1].split("?")[0]
        elif "youtube.com/watch?v=" in url: return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url: return url.split("youtu.be/")[1].split("?")[0]
    except: return None
    return None

def get_web_content(url):
    thumbnail_url = None
    content_path = None
    error_msg = None
    
    # Pfad zur Cookie-Datei (wird in app.py aus Secrets erstellt)
    cookie_file = "cookies.txt"
    has_cookies = os.path.exists(cookie_file)
    
    # --- STEALTH OPTIONEN ---
    # Wir tun so, als wären wir ein normaler Browser
    ydl_opts_base = {
        'quiet': True, 
        'noplaylist': True,
        'no_warnings': True,
        'ignoreerrors': True, # Wichtig: Nicht abstürzen bei 403
        'nocheckcertificate': True,
        # Fake User Agent (iPhone)
        'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'http_headers': {
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/'
        }
    }
    
    if has_cookies: 
        ydl_opts_base['cookiefile'] = cookie_file

    # 1. Metadaten holen
    try:
        with yt_dlp.YoutubeDL(ydl_opts_base) as ydl:
            info = ydl.extract_info(url, download=False)
            if info:
                thumbnail_url = info.get('thumbnail')
                # Manchmal ist der Titel nützlich als Fallback-Text
                video_title = info.get('title', '')
                video_desc = info.get('description', '')
    except Exception as e:
        print(f"Metadaten Warnung: {e}")
        thumbnail_url = PLACEHOLDER_IMG

    # 2. YouTube Transkript
    yt_id = get_video_id_youtube(url)
    if yt_id:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(yt_id, languages=['en', 'de', 'es', 'fr', 'it', 'pl'])
            text = " ".join([t['text'] for t in transcript])
            return f"TRANSCRIPT: {text}", thumbnail_url, None
        except: pass

    # 3. Audio Download (Der kritische Teil)
    try:
        temp_filename = f"temp_audio_{int(time.time())}.m4a"
        
        ydl_opts_download = ydl_opts_base.copy()
        ydl_opts_download.update({
            'format': 'bestaudio/best',
            'outtmpl': temp_filename,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a'}],
        })
        
        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            # Versuch 1: Normaler Download
            try:
                ydl.extract_info(url, download=True)
            except Exception as e:
                # Versuch 2: Falls 403, versuchen wir es ohne spezielle Header
                # Manchmal blockiert Instagram gerade WEIL wir Header faken
                if "403" in str(e):
                    print("403 erkannt, versuche Fallback...")
                    ydl.params['user_agent'] = None # Standard Agent nutzen
                    ydl.extract_info(url, download=True)
                else:
                    raise e
            
            if os.path.exists(temp_filename) and os.path.getsize(temp_filename) > 0:
                content_path = temp_filename
            else:
                # FALLBACK: Wenn Download fehlschlägt, geben wir Titel/Beschreibung an die KI
                # Das reicht oft schon für ein Rezept!
                if 'video_title' in locals() and video_title:
                    return f"Rezept aus Metadaten (Download blockiert): {video_title}. \nBeschreibung: {video_desc}", thumbnail_url, None
                else:
                    error_msg = "Download blockiert (403). Cookies prüfen."
                
    except Exception as e:
        # Letzter Rettungsanker: Metadaten
        if 'video_title' in locals() and video_title:
             return f"Rezept aus Metadaten (Notfall): {video_title}. {video_desc}", thumbnail_url, None
        error_msg = f"Fehler: {str(e)[:50]}... (Cookies erneuern?)"

    return content_path, thumbnail_url, error_msg

# --- KI FUNKTIONEN (Bleiben gleich) ---

def rezept_analysieren(content, img_url, original_url, is_file=False):
    if not GEMINI_API_KEY: st.error("⚠️ API Key fehlt!"); return None
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest') 
    
    prompt = f"""
    Du bist ein Profi-Koch. Analysiere das Rezept.
    Input kann Text (Transkript/Metadaten) oder Audio sein.
    
    WICHTIG: 
    1. Schätze Portionen (Default: 2) und Makros PRO PORTION.
    2. Ordne es EINER Kategorie zu: {", ".join(CATEGORIES)}.
    3. Wenn der Input wenig Infos enthält (z.B. nur Titel), erfinde ein passendes, leckeres Rezept basierend darauf.
    
    Antworte NUR mit reinem JSON:
    {{
      "Rezept": "Name", "Portionen": Zahl, "Kategorie": "Name",
      "Makros": {{"Kcal": Zahl, "Protein": Zahl, "Carbs": Zahl, "Fett": Zahl}},
      "Zutaten": [{{"Zutat": "Name", "Menge": Zahl, "Einheit": "g/ml/Stk"}}],
      "Schritte": ["Schritt 1", "Schritt 2"]
    }}
    """
    try:
        if is_file and os.path.exists(content):
            myfile = genai.upload_file(content)
            while myfile.state.name == "PROCESSING": time.sleep(1); myfile = genai.get_file(myfile.name)
            response = model.generate_content([prompt, myfile])
        else:
            response = model.generate_content(f"{prompt}\n\nInput:\n{content}")
        
        json_text = clean_json_response(response.text)
        data = json.loads(json_text)
        
        data["BildURL"] = img_url if img_url else PLACEHOLDER_IMG
        data["OriginalURL"] = original_url if original_url else ""
        if "Kategorie" not in data or data["Kategorie"] not in CATEGORIES: data["Kategorie"] = "Sonstiges"
        return data
    except Exception as e: st.error(f"KI Fehler: {e}"); return None

def makros_neu_berechnen(zutaten_text, schritte_text, portionen):
    if not GEMINI_API_KEY: return None
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    prompt = f"Berechne Nährwerte PRO PORTION (Gesamt {portionen} P.).\nZutaten:\n{zutaten_text}\nZubereitung:\n{schritte_text}\nAntworte NUR mit JSON: {{\"Kcal\": int, \"Protein\": int, \"Carbs\": int, \"Fett\": int}}"
    try:
        response = model.generate_content(prompt)
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except Exception as e: st.error(f"KI Fehler: {e}"); return None

def translate_recipe_text(data, target_lang):
    if not GEMINI_API_KEY: return data
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-flash-latest')
    prompt = f"""
    Translate values to {target_lang}. Keep JSON structure.
    Keys to translate: "Rezept", "Zutat", "Einheit", "Kategorie", "Schritte".
    JSON: {json.dumps(data)}
    """
    try:
        response = model.generate_content(prompt)
        json_text = clean_json_response(response.text)
        return json.loads(json_text)
    except: return data
