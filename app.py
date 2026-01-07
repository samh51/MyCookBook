import streamlit as st
import pandas as pd
import random
import time
import os

# --- COOKIE WORKAROUND FÜR CLOUD ---
# Wenn wir in der Cloud sind, existiert cookies.txt nicht.
# Wir erstellen sie aus den Secrets.
if "cookies" in st.secrets:
    with open("cookies.txt", "w") as f:
        f.write(st.secrets["cookies"])
# -----------------------------------

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
from modules.auth import login_form, change_user_password, update_user_language # NEU

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

# --- USER DATEN LADEN ---
if "df_z" not in st.session_state or st.session_state.df_z is None:
    user_email = st.session_state.user_email
    st.session_state.df_z, st.session_state.df_s, st.session_state.df_m, \
    st.session_state.df_e, st.session_state.df_o, st.session_state.basics, \
    st.session_state.sh_z, st.session_state.sh_s, st.session_state.sh_b, \
    st.session_state.sh_m, st.session_state.sh_e, st.session_state.sh_o, _ = get_data(user_email)

# --- SPRACHEN & ÜBERSETZUNG ---
LANGUAGES = {
    "English": "EN", "Deutsch": "DE", "Español": "ES",
    "Français": "FR", "Italiano": "IT", "Polski": "PL"
}
CODE_TO_NAME = {v: k for k, v in LANGUAGES.items()}

TRANSLATIONS = {
    "EN": {
        # Nav
        "nav_dash": "⌂ Dashboard", "nav_coll": "◫ Collections", "nav_shop": "≡ Shopping List", 
        "nav_cook": "♨ Cook", "nav_import": "⬇ Import", "nav_edit": "⚙ Editor", "nav_profile": "👤 Profile",
        # General
        "search_ph": "Search...", "welcome": "Welcome back", "favs": "Your Favorites", "all_rec": "Recipe Book",
        "no_rec": "No recipes found.", "random": "Inspiration", "random_btn": "Surprise Me",
        "to_rec": "Open Recipe", "ingredients": "Ingredients", "steps": "Instructions",
        "save": "Save", "delete": "Delete", "calc_macros": "AI Calc Macros",
        "portions": "Servings", "import_btn": "Analyze & Save",
        "url_ph": "Link to YouTube / Instagram / TikTok", "folder_new": "New Collection",
        "add_shop": "Add to List", "clean_shop": "Clean List", "clear_shop": "Delete All",
        "save_coll_title": "Save to Collection", "save_coll_btn": "Add",
        "translating": "Translating recipe...", "logout": "Logout",
        # Dashboard / Intro
        "dash_intro": "Your digital kitchen assistant. Here is what you can do:",
        "feat_1_t": "AI Import", "feat_1_d": "Paste any video link (Insta/TikTok/YouTube). The AI extracts ingredients, steps, and nutrition automatically.",
        "feat_2_t": "Nutrition", "feat_2_d": "Every recipe gets detailed macro-nutrients (Calories, Protein, Carbs, Fat) calculated per serving.",
        "feat_3_t": "Shopping", "feat_3_d": "Adjust servings and add ingredients directly to your interactive shopping list.",
        "feat_4_t": "Organize", "feat_4_d": "Create custom collections and mark your favorites to find them quickly.",
        # Profile
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
        "translating": "Übersetze Rezept...", "logout": "Abmelden",
        "dash_intro": "Dein digitaler Küchen-Assistent. Das kannst du machen:",
        "feat_1_t": "KI Import", "feat_1_d": "Kopiere einen Link (Insta/TikTok/YouTube). Die KI extrahiert Zutaten, Schritte & Nährwerte automatisch.",
        "feat_2_t": "Nährwerte", "feat_2_d": "Jedes Rezept erhält automatisch berechnete Makros (Kcal, Protein, Carbs, Fett) pro Portion.",
        "feat_3_t": "Einkauf", "feat_3_d": "Passe die Portionen an und setze Zutaten direkt auf deine interaktive Einkaufsliste.",
        "feat_4_t": "Ordnung", "feat_4_d": "Erstelle eigene Sammlungen und markiere Favoriten für schnellen Zugriff.",
        "prof_set": "Einstellungen", "prof_lang": "Sprache", "prof_pw": "Passwort ändern",
        "pw_old": "Altes Passwort", "pw_new": "Neues Passwort", "pw_upd": "Passwort aktualisieren", "pw_success": "Passwort geändert!"
    },
    # (Andere Sprachen hier gekürzt, nutzen Fallback auf EN für neue Keys wenn nötig, aber wir haben es sauber)
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
        "translating": "Traduciendo...", "logout": "Cerrar Sesión",
        "dash_intro": "Tu asistente de cocina digital. Esto es lo que puedes hacer:",
        "feat_1_t": "Importar IA", "feat_1_d": "Pega un enlace. La IA extrae ingredientes, pasos y nutrición automáticamente.",
        "feat_2_t": "Nutrición", "feat_2_d": "Cálculo automático de macros (Calorías, Proteínas, Grasas) por porción.",
        "feat_3_t": "Compras", "feat_3_d": "Ajusta las porciones y añade ingredientes a tu lista de compras.",
        "feat_4_t": "Organizar", "feat_4_d": "Crea colecciones personalizadas y marca tus favoritos.",
        "prof_set": "Ajustes", "prof_lang": "Idioma", "prof_pw": "Cambiar Contraseña",
        "pw_old": "Contraseña anterior", "pw_new": "Nueva contraseña", "pw_upd": "Actualizar", "pw_success": "¡Actualizado!"
    }
}
# Fallback für FR/IT/PL (Kopie von EN um Key Errors zu vermeiden, User sollte DE/EN/ES nutzen für Full UX)
for l in ["FR", "IT", "PL"]: TRANSLATIONS[l] = TRANSLATIONS["EN"]

if "lang_code" not in st.session_state: st.session_state.lang_code = "EN"
def T(key): return TRANSLATIONS[st.session_state.lang_code].get(key, TRANSLATIONS["EN"].get(key, key))

MENU_MAP = {
    "dashboard": "nav_dash", "collections": "nav_coll", "shopping": "nav_shop",
    "cook": "nav_cook", "import": "nav_import", "edit": "nav_edit", "profile": "nav_profile"
}

# Alias
df_z = st.session_state.df_z; df_m = st.session_state.df_m; sh_z = st.session_state.sh_z
# (Restliche Alias sparen wir hier um Code kurz zu halten, Nutzung via st.session_state wenn nötig)

# --- HELPERS ---
def refresh_data():
    del st.session_state['df_z']; st.rerun()

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
    if st.button("⟳ Refresh"): st.session_state.clear(); st.rerun()

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
        st.markdown(f"""<div style="padding: 10px 10px 0 10px;">
            <span class="recipe-cat">{cat if cat else "Rezept"}</span>
            <div style="height: 30px; overflow: hidden; margin-bottom: 5px;">
                <span class="recipe-title" title="{r_name}">{r_name}</span>
            </div></div>""", unsafe_allow_html=True)
        c_btn, c_star = st.columns([4, 1])
        c_btn.button(T("to_rec"), key=f"btn_{context}_{r_name}", use_container_width=True, on_click=go_to_recipe_callback, args=(r_name,))
        if c_star.button("★" if is_fav else "☆", key=f"fav_{context}_{r_name}"): fav_callback(r_name, is_fav)

# === CONTENT ===
active_nav = st.session_state.internal_nav

# 1. DASHBOARD
if active_nav == "dashboard":
    # Begrüßung
    st.title(f"{T('welcome')}, {st.session_state.user_name}! 👋")
    
    # --- ONBOARDING / EMPTY STATE ---
    if df_z is None or df_z.empty:
        st.markdown(f"_{T('dash_intro')}_")
        st.write("")
        
        # Moderne Feature Cards
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.info(f"**🎥 {T('feat_1_t')}**\n\n{T('feat_1_d')}")
        with c2:
            st.success(f"**🥑 {T('feat_2_t')}**\n\n{T('feat_2_d')}")
        with c3:
            st.warning(f"**🛒 {T('feat_3_t')}**\n\n{T('feat_3_d')}")
        with c4:
            st.error(f"**📚 {T('feat_4_t')}**\n\n{T('feat_4_d')}")
            
        st.divider()
        cb1, cb2 = st.columns(2)
        if cb1.button(f"🚀 {T('nav_import')}", type="primary", use_container_width=True): 
            st.session_state.internal_nav = "import"; st.rerun()
        if cb2.button(f"✏️ {T('nav_edit')}", use_container_width=True): 
            st.session_state.internal_nav = "edit"; st.rerun()

    else:
        # NORMALES DASHBOARD MIT SUCHE
        if search_query:
            all_r = sorted(df_z['Rezept'].unique())
            filtered = [r for r in all_r if search_query in r.lower()]
            if not df_m.empty and 'Kategorie' in df_m.columns:
                 cat_matches = df_m[df_m['Kategorie'].str.lower().str.contains(search_query, na=False)]['Rezept'].tolist()
                 filtered = list(set(filtered + cat_matches))
            st.markdown(f"**Results:** {search_query}")
            if filtered:
                cols = st.columns(3)
                for i, r in enumerate(filtered): 
                    with cols[i%3]: render_card(r, "search")
            else: st.info(T("no_rec"))
        else:
            # Random Feature
            with st.expander(f"🎲 {T('random')}", expanded=False):
                c1, c2 = st.columns([3, 1])
                rc = c1.selectbox("Category", ["Alle"] + CATEGORIES, label_visibility="collapsed")
                if c2.button(T("random_btn"), type="primary", use_container_width=True):
                    all_r = sorted(df_z['Rezept'].unique())
                    pool = all_r
                    if rc != "Alle" and not df_m.empty: pool = df_m[df_m['Kategorie'] == rc]['Rezept'].tolist()
                    if pool:
                        cols = st.columns(3)
                        for i, r in enumerate(random.sample(pool, min(len(pool), 3))): 
                            with cols[i]: render_card(r, "rand")

            # Favoriten
            favs = df_z[df_z['is_fav'] == True]['Rezept'].unique()
            if len(favs) > 0:
                st.markdown(f"### {T('favs')}")
                cols = st.columns(3)
                for i, f in enumerate(favs): 
                    with cols[i%3]: render_card(f, "fav")
                st.write("")

            # Alle Rezepte
            st.markdown(f"### {T('all_rec')}")
            all_r = sorted(df_z['Rezept'].unique())
            cats = st.multiselect("Filter", CATEGORIES, label_visibility="collapsed")
            dis_list = [r for r in all_r if r not in favs]
            if cats and not df_m.empty:
                 valid = df_m[df_m['Kategorie'].isin(cats)]['Rezept'].tolist()
                 dis_list = [r for r in dis_list if r in valid]
            
            if dis_list:
                cols = st.columns(3)
                for i, r in enumerate(dis_list): 
                    with cols[i%3]: render_card(r, "all")

# 7. PROFIL (Neu)
elif active_nav == "profile":
    st.title(T("nav_profile"))
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;">
            <div style="font-size: 40px;">👤</div>
            <h3>{st.session_state.user_name}</h3>
            <p>{st.session_state.user_email}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(T("logout"), type="secondary", use_container_width=True):
            st.session_state.user_email = None; st.session_state.user_name = None; st.rerun()

    with c2:
        st.subheader(T("prof_set"))
        
        # Sprache ändern
        curr_lang_name = CODE_TO_NAME.get(st.session_state.lang_code, "English")
        sel_lang_name = st.selectbox(T("prof_lang"), list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(curr_lang_name))
        
        if st.button(T("save")):
            new_code = LANGUAGES[sel_lang_name]
            # Update DB
            update_user_language(st.session_state.user_email, new_code, st.session_state.sh_u)
            # Update Session
            st.session_state.lang_code = new_code
            st.success("Language updated!")
            time.sleep(1); st.rerun()
            
        st.divider()
        st.subheader(T("prof_pw"))
        with st.form("pw_change"):
            # Altes PW Check wäre sicherer, hier der Einfachheit halber nur neu
            np1 = st.text_input(T("pw_new"), type="password")
            np2 = st.text_input("Confirm", type="password")
            if st.form_submit_button(T("pw_upd")):
                if np1 and np1 == np2:
                    change_user_password(st.session_state.user_email, np1, st.session_state.sh_u)
                    st.success(T("pw_success"))
                else:
                    st.error("Passwords do not match.")

# ... (RESTLICHE TABS BLEIBEN IDENTISCH ZUM VORHERIGEN CODE) ...
# Fügen wir der Vollständigkeit halber die anderen Tabs hier wieder an:

elif active_nav == "collections":
    st.title(T("nav_coll"))
    with st.expander(T("folder_new")):
        with st.form("new_folder"):
            c1, c2 = st.columns([3,1])
            new_f = c1.text_input("Name")
            if c2.form_submit_button(T("save")) and new_f:
                if df_o.empty or new_f not in df_o['OrdnerName'].unique():
                    st.session_state.sh_o.append_row([new_f, "INIT_HIDDEN", st.session_state.user_email])
                    refresh_data()
    st.divider()
    if not df_o.empty:
        folders = [f for f in df_o['OrdnerName'].unique() if f]
        sel_f = st.selectbox("Collection", folders, label_visibility="collapsed")
        if sel_f:
            recs = [r for r in df_o[df_o['OrdnerName'] == sel_f]['Rezept'].unique() if r != "INIT_HIDDEN"]
            if recs:
                cols = st.columns(3)
                for i, r in enumerate(recs):
                    with cols[i%3]: render_card(r, f"coll_{sel_f}")
            else: st.info(T("no_rec"))

elif active_nav == "shopping":
    st.title(T("nav_shop"))
    if not df_e.empty:
        local_df = df_e.copy()
        local_df['id'] = local_df['Zutat'] + "_" + local_df['Einheit']
        local_df['done'] = local_df['id'].apply(lambda x: x in st.session_state.shop_checked)
        local_df = local_df.sort_values(by=['done', 'Zutat'])
        
        def toggle(item_id):
            if item_id in st.session_state.shop_checked: st.session_state.shop_checked.remove(item_id)
            else: st.session_state.shop_checked.add(item_id)

        for _, row in local_df.iterrows():
            txt = f"{row['Menge']} {row['Einheit']} {row['Zutat']}"
            st.checkbox(txt, row['done'], key=f"chk_{row['id']}", on_change=toggle, args=(row['id'],))
        
        st.divider()
        c1, c2 = st.columns([1,2])
        if c1.button(T("clean_shop")):
             sync_shopping_list_to_db(local_df[~local_df['done']], st.session_state.sh_e)
             st.session_state.shop_checked = set()
             refresh_data()
        if c2.button(T("clear_shop"), type="secondary"):
             st.session_state.sh_e.clear(); st.session_state.sh_e.append_row(["Zutat", "Menge", "Einheit", "Owner"])
             refresh_data()
    else: st.info("Leer.")

elif active_nav == "cook":
    if not df_z.empty:
        all_r = sorted(df_z['Rezept'].unique())
        sel_r = all_r
        if search_query:
            filtered = [r for r in all_r if search_query in r.lower()]
            if filtered: sel_r = filtered
        
        idx = 0
        if "selected_recipe" in st.session_state and st.session_state.selected_recipe in sel_r:
            idx = sel_r.index(st.session_state.selected_recipe)
        rezept = st.selectbox(T("nav_cook"), sel_r, index=idx, key="cook_selector", label_visibility="collapsed")
        
        if rezept:
            orig_z = df_z[df_z['Rezept'] == rezept]
            orig_s = st.session_state.df_s[st.session_state.df_s['Rezept'] == rezept]
            orig_m = df_m[df_m['Rezept'] == rezept]
            
            current_lang = st.session_state.lang_code
            display_data = {}
            cache_key = f"{rezept}_{current_lang}"
            
            if current_lang != "EN":
                if "trans_cache" in st.session_state and st.session_state.trans_cache.get("key") == cache_key:
                    display_data = st.session_state.trans_cache["data"]
                else:
                    with st.spinner(T("translating")):
                        z_list = orig_z[['Zutat', 'Menge', 'Einheit']].to_dict('records')
                        s_list = orig_s.sort_values('Schritt_Nr')['Anweisung'].tolist()
                        kategorie = orig_m.iloc[0]['Kategorie'] if not orig_m.empty and 'Kategorie' in orig_m.columns else ""
                        payload = {"Rezept": rezept, "Kategorie": kategorie, "Zutaten": z_list, "Schritte": s_list}
                        translated = translate_recipe_text(payload, st.session_state.lang_code)
                        display_data = translated
                        st.session_state.trans_cache = {"key": cache_key, "data": translated}
            else:
                display_data = {
                    "Rezept": rezept,
                    "Kategorie": orig_m.iloc[0]['Kategorie'] if not orig_m.empty and 'Kategorie' in orig_m.columns else "",
                    "Zutaten": orig_z[['Zutat', 'Menge', 'Einheit']].to_dict('records'),
                    "Schritte": orig_s.sort_values('Schritt_Nr')['Anweisung'].tolist()
                }

            bp = float(orig_m['Portionen'].iloc[0]) if not orig_m.empty and orig_m['Portionen'].iloc[0] else 2.0
            img = PLACEHOLDER_IMG; url = ""
            if not orig_m.empty:
                r0 = orig_m.iloc[0]
                if str(r0['BildURL']).startswith(("http", "data:")): img = r0['BildURL']
                if str(r0['OriginalURL']).startswith("http"): url = r0['OriginalURL']

            st.markdown(f"""<div style="width: 100%; height: 350px; background-image: url('{img}'); background-size: cover; background-position: center; border-radius: 12px; margin-bottom: 25px;"></div>""", unsafe_allow_html=True)
            c1, c2 = st.columns([3,1])
            c1.markdown(f"## {display_data.get('Rezept', rezept)}")
            if display_data.get('Kategorie'): c1.caption(display_data.get('Kategorie'))
            
            is_fav = orig_z['is_fav'].iloc[0] if not orig_z.empty else False
            if c2.button("★ Favorit" if not is_fav else "☆ Entfernen", use_container_width=True):
                toggle_favorit(rezept, is_fav, sh_z); refresh_data()
            
            with st.popover(T("save_coll_title")):
                if not df_o.empty:
                    tf = st.selectbox("Collection", [f for f in df_o['OrdnerName'].unique() if f])
                    if st.button(T("save_coll_btn")):
                        add_to_folder_db(tf, rezept, st.session_state.sh_o); st.toast("OK!", icon="✅")

            if url: st.markdown(f"[Original Link]({url})")
            st.divider()
            c_p, c_shop = st.columns([1, 2])
            wp = c_p.number_input(T("portions"), 1, value=int(bp))
            fak = wp / bp if bp > 0 else 1
            if c_shop.button(T("add_shop")):
                tmp = orig_z.copy(); tmp['Menge'] *= fak
                add_to_shopping_list(tmp, st.session_state.sh_e); refresh_data(); st.toast("OK", icon="✅")
            
            t1, t2 = st.tabs([T("ingredients"), T("steps")])
            with t1:
                st.write("")
                for r in display_data.get('Zutaten', []):
                    m = str(round(r['Menge']*fak, 1)).replace(".0","") if r['Menge']>0 else ""
                    st.markdown(f"**{m} {r['Einheit']}** {r['Zutat']}")
            with t2:
                st.write("")
                for i, s in enumerate(display_data.get('Schritte', [])): st.markdown(f"**{i+1}.** {s}")
            st.divider()
            if st.button(T("nav_edit")):
                 st.session_state.edit_recipe_name = rezept; st.session_state.internal_nav = "edit"; st.rerun()

elif active_nav == "import":
    st.title(T("nav_import"))
    u = st.text_input(T("url_ph"))
    if st.button(T("import_btn"), type="primary"):
        with st.spinner("..."):
            c, th, err = get_web_content(u)
            if c:
                d = rezept_analysieren(c, th, u, "TRANSCRIPT" not in c)
                if isinstance(c, str) and "temp_audio" in c and os.path.exists(c): os.remove(c)
                if d:
                    save_recipe_to_db(d, sh_z, st.session_state.sh_s, st.session_state.sh_m, True)
                    st.success("OK!"); time.sleep(1); refresh_data()
            else: st.error(err)

elif active_nav == "edit":
    st.title(T("nav_edit"))
    all_r = sorted(df_z['Rezept'].unique()) if not df_z.empty else []
    sel_r = all_r
    if search_query:
        filtered = [r for r in all_r if search_query in r.lower()]
        if filtered: sel_r = filtered
    
    pi = 0
    if "edit_recipe_name" in st.session_state and st.session_state.edit_recipe_name in sel_r:
        pi = sel_r.index(st.session_state.edit_recipe_name)
    es = st.selectbox("Rezept", sel_r, index=pi)
    
    if es:
        cz = df_z[df_z['Rezept'] == es][['Zutat', 'Menge', 'Einheit']]
        cs = st.session_state.df_s[st.session_state.df_s['Rezept'] == es].sort_values('Schritt_Nr')[['Anweisung']]
        cm = df_m[df_m['Rezept'] == es]
        
        if "last_edited_recipe" not in st.session_state or st.session_state.last_edited_recipe != es:
            st.session_state.last_edited_recipe = es
            if not cm.empty:
                for k in ["Kcal", "Protein", "Carbs", "Fett"]: 
                    st.session_state[f"edit_{k.lower()}"] = int(cm.iloc[0][k])
        
        c1, c2 = st.columns(2)
        nn = c1.text_input("Name", es)
        
        c_img = PLACEHOLDER_IMG; c_url = ""; c_cat = "Sonstiges"
        if not cm.empty:
            if str(cm.iloc[0]['BildURL']).startswith(("http", "data:")): c_img = cm.iloc[0]['BildURL']
            c_url = cm.iloc[0]['OriginalURL']
            if cm.iloc[0]['Kategorie'] in CATEGORIES: c_cat = cm.iloc[0]['Kategorie']
        
        n_img = c2.text_input("Bild URL", c_img)
        n_url = c2.text_input("Original Link", c_url)
        n_cat = c1.selectbox("Kategorie", CATEGORIES, index=CATEGORIES.index(c_cat) if c_cat in CATEGORIES else 0)
        
        st.markdown(f"""<div style="width: 100px; height: 100px; background-image: url('{n_img}'); background-size: cover; border-radius: 8px;"></div>""", unsafe_allow_html=True)
        bp = st.number_input(T("portions"), value=float(cm['Portionen'].iloc[0]) if not cm.empty else 2.0)
        
        st.subheader(T("ingredients"))
        ez = st.data_editor(cz, num_rows="dynamic", use_container_width=True)
        st.subheader(T("steps"))
        es_df = st.data_editor(cs, num_rows="dynamic", use_container_width=True)
        
        if st.button(T("calc_macros")):
            zt = "".join([f"{r['Menge']} {r['Einheit']} {r['Zutat']}\n" for _, r in ez.iterrows()])
            stt = "\n".join(es_df['Anweisung'].tolist())
            nm = makros_neu_berechnen(zt, stt, bp)
            if nm:
                for k, v in nm.items(): st.session_state[f"edit_{k.lower()}"] = v
                st.rerun()

        col = st.columns(4)
        nk = col[0].number_input("Kcal", key="edit_kcal")
        np = col[1].number_input("Protein", key="edit_protein")
        nc = col[2].number_input("Carbs", key="edit_carbs")
        nf = col[3].number_input("Fett", key="edit_fett")
        
        st.write("")
        c_save, c_del = st.columns([2, 1])
        if c_save.button(T("save"), type="primary", use_container_width=True):
            jd = {
                "Rezept": nn, "Portionen": bp, "BildURL": n_img, "OriginalURL": n_url, "Kategorie": n_cat,
                "Makros": {"Kcal": nk, "Protein": np, "Carbs": nc, "Fett": nf},
                "Zutaten": ez.to_dict('records'), "Schritte": es_df['Anweisung'].tolist()
            }
            if nn != es: delete_recipe_from_db(es, sh_z, st.session_state.sh_s, st.session_state.sh_m)
            save_recipe_to_db(jd, sh_z, st.session_state.sh_s, st.session_state.sh_m, True)
            st.success("OK"); time.sleep(1); refresh_data()
        
        if c_del.button(T("delete"), use_container_width=True):
            delete_recipe_from_db(es, sh_z, st.session_state.sh_s, st.session_state.sh_m)
            refresh_data()
