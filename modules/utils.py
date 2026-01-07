import base64
from io import BytesIO
from PIL import Image
import requests

# Neutrales Platzhalter-Bild (Schneidebrett/Küche)
PLACEHOLDER_IMG = "https://images.unsplash.com/photo-1495521821757-a1efb6729352?q=80&w=800&auto=format&fit=crop"

def zutat_bereinigen(name):
    if not isinstance(name, str): return str(name)
    suche = name.lower().strip()
    mapping = {
        "garlic": "Knoblauch", "onion": "Zwiebel", "salt": "Salz", "pepper": "Pfeffer",
        "oil": "Öl", "sugar": "Zucker", "flour": "Mehl", "butter": "Butter",
        "milk": "Milch", "water": "Wasser", "egg": "Ei", "lemon": "Zitrone"
    }
    for k, v in mapping.items():
        if k in suche: return v
    return name.capitalize()

def download_and_compress_image(url):
    """Lädt Bild, verkleinert es auf 250px und gibt Base64 zurück."""
    if not url or "placeholder" in url: return url
    if str(url).startswith("data:image"): return url
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.instagram.com/'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200: return PLACEHOLDER_IMG
            
        img = Image.open(BytesIO(response.content))
        if img.mode in ("RGBA", "P"): img = img.convert("RGB")
        
        img.thumbnail((250, 250))
        
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=60)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/jpeg;base64,{img_str}"
    except Exception as e:
        print(f"Bild Fehler: {e}")
        return PLACEHOLDER_IMG