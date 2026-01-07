import streamlit as st
import pandas as pd
import random
import time
import os

# --- COOKIE WORKAROUND FÜR CLOUD ---
if "cookies" in st.secrets:
    with open("cookies.txt", "w") as f:
        f.write(st.secrets["cookies"])

# Module
from modules.database import (
    get_data, save_recipe_to_db, delete_recipe_from_db, toggle_favorit, 
    add_to_folder_db, add_to_shopping_list, sync_shopping_list_to_db
)
from modules.api import (
    rezept_analysieren, makros_neu_berechnen, translate_recipe_text, get_web_content, CATEGORIES
)
from modules.utils import PLACEHOLDER_IMG
from modules.styles import apply_custom_css
from modules.auth import login_form, change_user_password, update_user_language

# --- SETUP ---
st.set_page_config(page_title="My Cookbook", page_icon="🌿", layout="wide")
apply_custom_css()

# --- DATENBANK INIT ---
if "sh_u" not in st.session_state:
    data = get_data(None)
    st.session_state.sh_u = data[12] # User Sheet

# --- LOGIN CHECK ---
if not login_form(st.session_state.sh_u):
    st.stop()

# --- USER EMAIL HOLEN ---
user_email = st.session_state.user_email

# --- DATEN FÜR USER LADEN ---
if "df_z" not in st.session_state or st.session_state.df_z is None:
    st.session_state.df_z, st.session_state.df_s, st.session_state.df_m, \
    st.session_state.df_e, st.session_state.df_o, st.session_state.basics, \
    st.session_state.sh_z, st.session_state.sh_s, st.session_state.sh_b, \
    st.session_state.sh_m, st.session_state.sh_e, st.session_state.sh_o, _ = get_data(user_email)

# --- HELPER: REFRESH DATA ---
def refresh_data():
    keys = ['df_z', 'df_s', 'df_m', 'df_e', 'df_o']
    for k in keys:
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# --- SPRACHEN & ÜBERSETZUNG ---
LANGUAGES = {
    "English": "EN", "Deutsch": "DE", "Español": "ES",
    "Français": "FR", "Italiano": "IT", "Polski": "PL"
}
CODE_TO_NAME = {v: k for k, v in LANGUAGES.items()}

TRANSLATIONS = {
    "EN": {
        "nav_dash": "⌂ Dashboard", "nav_coll": "◫ Collections", "nav_shop": "≡ Shopping List", 
        "nav_cook": "♨ Cook", "nav_import": "⬇ Import", "nav_edit": "⚙ Editor", "nav_profile": "👤 Profile",
        "search_ph": "Search...", "welcome": "Welcome back", "favs": "Your Favorites", "all_rec": "Recipe Book",
        "no_rec": "No recipes found.", "random": "Inspiration", "random_btn": "Surprise Me",
        "to_rec": "Open Recipe", "ingredients": "Ingredients", "steps": "Instructions",
        "save": "Save", "delete": "Delete", "calc_macros": "AI Calc Macros",
        "portions": "Servings", "import_btn": "Analyze & Save",
        "url_ph": "Link to YouTube / Instagram / TikTok", "folder_new": "New Collection",
        "add_shop": "Add to List", "clean_shop": "Clean List", "clear_shop": "Delete All",
        "save_coll_title": "Save to Collection", "save_coll_btn": "Add",
        "translating": "Translating recipe...", "logout": "Logout", "success": "Success!",
        "dash_intro": "Your digital kitchen assistant. Here is what you can do:",
        "feat_1_t": "AI Import", "feat_1_d": "Paste any video link (Insta/TikTok/YouTube). The AI extracts ingredients, steps, and nutrition automatically.",
        "feat_2_t": "Nutrition", "feat_2_d": "Every recipe gets detailed macro-nutrients (Calories, Protein, Carbs, Fat) calculated per serving.",
        "feat_3_t": "Shopping", "feat_3_d": "Adjust servings and add ingredients directly to your interactive shopping list.",
        "feat_4_t": "Organize", "feat_4_d": "Create custom collections and mark your favorites to find them quickly.",
        "prof_set": "Settings", "prof_lang": "Language", "prof_pw": "Change Password",
        "pw_old": "Old Password", "pw_new": "New Password", "pw_upd": "Update Password", "pw_success": "Password updated!"
    },
    "DE": {
        "nav_dash": "⌂ Dashboard", "nav_coll": "◫ Sammlungen", "nav_shop": "≡ Einkaufsliste", 
        "nav_cook": "♨ Kochen", "nav_import": "⬇ Import", "nav_edit": "⚙ Editor", "nav_profile": "👤 Profil",
        "search_ph": "Suche...", "welcome": "Willkommen zurück", "favs": "Deine Favoriten", "all_rec": "Rezeptbuch",
        "no_rec": "Keine Rezepte gefunden.", "random": "Inspiration", "random_btn": "Überrasch mich",
        "to_rec": "Zum Rezept", "ingredients": "Zutaten", "steps": "Zubereitung",
        "save": "Speichern", "delete": "Löschen", "calc_macros": "KI Makros berechnen",
        "portions": "Portionen", "import_btn": "Analysieren & Speichern",
        "url_ph": "Link zu YouTube / Instagram / TikTok", "folder_new": "Neue Sammlung",
        "add_shop": "Auf Einkaufsliste", "clean_shop": "Liste bereinigen", "clear_shop": "Alles löschen",
        "save_coll_title": "In Sammlung speichern", "save_coll_btn": "Hinzufügen",
        "translating": "Übersetze Rezept...", "logout": "Abmelden", "success": "Erfolgreich!",
        "dash_intro": "Dein digitaler Küchen-Assistent. Das kannst du machen:",
        "feat_1_t": "KI Import", "feat_1_d": "Kopiere einen Link (Insta/TikTok/YouTube). Die KI extrahiert Zutaten, Schritte & Nährwerte automatisch.",
        "feat_2_t": "Nährwerte", "feat_2_d": "Jedes Rezept erhält automatisch berechnete Makros (Kcal, Protein, Carbs, Fett) pro Portion.",
        "feat_3_t": "Einkauf", "feat_3_d": "Passe die Portionen an und setze Zutaten direkt auf deine interaktive Einkaufsliste.",
        "feat_4_t": "Ordnung", "feat_4_d": "Erstelle eigene Sammlungen und markiere Favoriten für schnellen Zugriff.",
        "prof_set": "Einstellungen", "prof_lang": "Sprache", "prof_pw": "Passwort ändern",
        "pw_old": "Altes Passwort", "pw_new": "Neues Passwort", "pw_upd": "Passwort aktualisieren", "pw_success": "Passwort geändert!"
    },
    "ES": {
        "nav_dash": "⌂ Tablero", "nav_coll": "◫ Colecciones", "nav_shop": "≡ Lista de Compras", 
        "nav_cook": "♨ Cocinar", "nav_import": "⬇ Importar", "nav_edit": "⚙ Editor", "nav_profile": "👤 Perfil",
        "search_ph": "Buscar...", "welcome": "Bienvenido", "favs": "Favoritos", "all_rec": "Recetario",
        "no_rec": "No se encontraron recetas.", "random": "Inspiración", "random_btn": "Sorpréndeme",
        "to_rec": "Ver Receta", "ingredients": "Ingredientes", "steps": "Instrucciones",
        "save": "Guardar", "delete": "Borrar", "calc_macros": "Calc Macros IA",
        "portions": "Porciones", "import_btn": "Analizar y Guardar",
        "url_ph": "Enlace a YouTube / Instagram / TikTok", "folder_new": "Nueva Colección",
        "add_shop": "Añadir a lista", "clean_shop": "Limpiar lista", "clear_shop": "Borrar todo",
        "save_coll_title": "Guardar en colección", "save_coll_btn": "Añadir",
        "translating": "Traduciendo...", "logout": "Cerrar Sesión", "success": "¡Éxito!",
        "dash_intro": "Tu asistente de cocina digital. Esto es lo que puedes hacer:",
        "feat_1_t": "Importar IA", "feat_1_d": "Pega un enlace. La IA extrae ingredientes, pasos y nutrición automáticamente.",
        "feat_2_t": "Nutrición", "feat_2_d": "Cálculo automático de macros (Calorías, Proteínas, Grasas) por porción.",
        "feat_3_t": "Compras", "feat_3_d": "Ajusta las porciones y añade ingredientes a tu lista de compras.",
        "feat_4_t": "Organizar", "feat_4_d": "Crea colecciones personalizadas y marca tus favoritos.",
        "prof_set": "Ajustes", "prof_lang": "Idioma", "prof_pw": "Cambiar Contraseña",
        "pw_old": "Contraseña anterior", "pw_new": "Nueva contraseña", "pw_upd": "Actualizar", "pw_success": "¡Actualizado!"
    }
}
for l in ["FR", "IT", "PL"]: TRANSLATIONS[l] = TRANSLATIONS["EN"]

if "lang_code" not in st.session_state: st.session_state.lang_code = "EN"
def T(key): return TRANSLATIONS[st.session_state.lang_code].get(key, TRANSLATIONS["EN"].get(key, key))

MENU_MAP = {
    "dashboard": "nav_dash", "collections": "nav_coll", "shopping": "nav_shop",
    "cook": "nav_cook", "import": "nav_import", "edit": "nav_edit", "profile": "nav_profile"
}

# Alias
df_z = st.session_state.df_z; df_m = st.session_state.df_m
sh_z = st.session_state.sh_z; sh_s = st.session_state.sh_s; sh_m = st.session_state.sh_m; sh_e = st.session_state.sh_e; sh_o = st.session_state.sh_o

# --- CALLBACKS ---
def go_to_recipe_callback(r_name):
    st.session_state.selected_recipe = r_name
    st.session_state.internal_nav = "cook"
    if "trans_cache" in st.session_state: del st.session_state.trans_cache

def fav_callback(r_name, is_currently_fav):
    toggle_favorit(r_name, is_currently_fav, sh_z)
    refresh_data()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### My Cookbook")
    search_query = st.text_input("", placeholder=T("search_ph")).lower().strip()
    st.write("") 
    
    if "internal_nav" not in st.session_state: st.session_state.internal_nav = "dashboard"
    options_display = [T(v) for k, v in MENU_MAP.items()]
    options_internal = list(MENU_MAP.keys())
    current_idx = options_internal.index(st.session_state.internal_nav) if st.session_state.internal_nav in options_internal else 0
    selected_display = st.radio("Menu", options_display, index=current_idx, label_visibility="collapsed")
    st.session_state.internal_nav = options_internal[options_display.index(selected_display)]
    
    st.divider()
    if st.button("⟳ Refresh"): refresh_data()

# --- SHARED CARD FUNCTION ---
def render_card(r_name, context="all"):
    img = PLACEHOLDER_IMG; cat = ""
    if not df_m.empty:
        entry = df_m[df_m['Rezept'] == r_name]
        if not entry.empty: 
            val = str(entry.iloc[0]['BildURL']).strip()
            if val.startswith(("http", "data:")): img = val
            if 'Kategorie' in entry.columns: cat = entry.iloc[0]['Kategorie']
    is_fav = False
    if not df_z.empty:
        z_rows = df_z[df_z['Rezept'] == r_name]
        if not z_rows.empty: is_fav = z_rows.iloc[0]['is_fav']

    with st.container(border=True):
        st.markdown(f"""<div class="recipe-card-img" style="background-image: url('{img}');"></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="padding: 10px 10px
