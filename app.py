import streamlit as st
import pandas as pd
import random
import time
import os

# --- COOKIE WORKAROUND ---
if "cookies" in st.secrets:
    with open("cookies.txt", "w") as f: f.write(st.secrets["cookies"])

# Module
from modules.database import (get_data, save_recipe_to_db, delete_recipe_from_db, toggle_favorit, add_to_folder_db, add_to_shopping_list, sync_shopping_list_to_db)
from modules.api import (rezept_analysieren, makros_neu_berechnen, translate_recipe_text, get_web_content, CATEGORIES)
from modules.utils import PLACEHOLDER_IMG
from modules.styles import apply_custom_css
from modules.auth import login_form, change_user_password, update_user_language

# --- SETUP ---
st.set_page_config(page_title="My Cookbook", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")
apply_custom_css()

# --- DATENBANK INIT ---
if "sh_u" not in st.session_state:
    data = get_data(None)
    st.session_state.sh_u = data[12] 

# --- LOGIN CHECK ---
if not login_form(st.session_state.sh_u):
    st.stop()

# --- USER EMAIL & DATA ---
user_email = st.session_state.user_email

if "df_z" not in st.session_state or st.session_state.df_z is None:
    st.session_state.df_z, st.session_state.df_s, st.session_state.df_m, \
    st.session_state.df_e, st.session_state.df_o, st.session_state.basics, \
    st.session_state.sh_z, st.session_state.sh_s, st.session_state.sh_b, \
    st.session_state.sh_m, st.session_state.sh_e, st.session_state.sh_o, _ = get_data(user_email)

if "shop_checked" not in st.session_state: st.session_state.shop_checked = set()

# --- HELPER ---
def refresh_data():
    for k in ['df_z', 'df_s', 'df_m', 'df_e', 'df_o']: 
        if k in st.session_state: del st.session_state[k]
    st.rerun()

# --- SPRACHEN & ICONS ---
LANGUAGES = {"English": "EN", "Deutsch": "DE", "Español": "ES", "Français": "FR", "Italiano": "IT", "Polski": "PL"}
CODE_TO_NAME = {v: k for k, v in LANGUAGES.items()}

# Hier die Icons direkt in den Namen, damit sie im Menü erscheinen
TRANSLATIONS = {
    "EN": {
        "menu_opts": ["⌂ Dashboard", "◫ Collections", "≡ Shopping", "♨ Cook", "⬇ Import", "⚙ Editor", "👤 Profile"],
        "search_ph": "Search...", "welcome": "Welcome", "favs": "Favorites", "all_rec": "Cookbook",
        "no_rec": "Nothing found.", "random": "Inspiration", "random_btn": "Surprise",
        "to_rec": "Open", "ingredients": "Ingredients", "steps": "Steps",
        "save": "Save", "delete": "Delete", "calc_macros": "Calc Macros", "portions": "Servings", "import_btn": "Analyze",
        "url_ph": "Paste Link", "folder_new": "New Collection", "add_shop": "To List", "clean_shop": "Clean", "clear_shop": "Clear",
        "save_coll_title": "Save to Collection", "save_coll_btn": "Add", "translating": "Translating...", "logout": "Logout", "success": "Done!",
        "dash_intro": "Your smart kitchen assistant.",
        "feat_1_t": "Import", "feat_1_d": "From Insta/TikTok.",
        "feat_2_t": "Macros", "feat_2_d": "Auto nutrition.",
        "feat_3_t": "Shop", "feat_3_d": "Smart list.",
        "feat_4_t": "Sort", "feat_4_d": "Organize.",
        "prof_set": "Settings", "prof_lang": "Language", "prof_pw": "Change Password",
        "pw_old": "Old", "pw_new": "New", "pw_upd": "Update", "pw_success": "Updated!"
    },
    "DE": {
        "menu_opts": ["⌂ Dashboard", "◫ Sammlungen", "≡ Einkauf", "♨ Kochen", "⬇ Import", "⚙ Editor", "👤 Profil"],
        "search_ph": "Suchen...", "welcome": "Hallo", "favs": "Favoriten", "all_rec": "Rezeptbuch",
        "no_rec": "Nichts gefunden.", "random": "Inspiration", "random_btn": "Überraschung",
        "to_rec": "Öffnen", "ingredients": "Zutaten", "steps": "Schritte",
        "save": "Speichern", "delete": "Löschen", "calc_macros": "Makros", "portions": "Portionen", "import_btn": "Analysieren",
        "url_ph": "Link einfügen", "folder_new": "Neue Sammlung", "add_shop": "Auf Liste", "clean_shop": "Aufräumen", "clear_shop": "Leeren",
        "save_coll_title": "In Sammlung", "save_coll_btn": "Hinzufügen", "translating": "Übersetze...", "logout": "Abmelden", "success": "Erledigt!",
        "dash_intro": "Dein smarter Assistent.",
        "feat_1_t": "Import", "feat_1_d": "Von Insta/TikTok.",
        "feat_2_t": "Makros", "feat_2_d": "Auto Nährwerte.",
        "feat_3_t": "Einkauf", "feat_3_d": "Smarte Liste.",
        "feat_4_t": "Ordnung", "feat_4_d": "Sortieren.",
        "prof_set": "Einstellungen", "prof_lang": "Sprache", "prof_pw": "Passwort",
        "pw_old": "Alt", "pw_new": "Neu", "pw_upd": "Ändern", "pw_success": "Geändert!"
    },
    "ES": {
        "menu_opts": ["⌂ Tablero", "◫ Colecciones", "≡ Compras", "♨ Cocinar", "⬇ Importar", "⚙ Editor", "👤 Perfil"],
        "search_ph": "Buscar...", "welcome": "Hola", "favs": "Favoritos", "all_rec": "Recetario",
        "no_rec": "Nada encontrado.", "random": "Inspiración", "random_btn": "Sorpresa",
        "to_rec": "Ver", "ingredients": "Ingredientes", "steps": "Pasos",
        "save": "Guardar", "delete": "Borrar", "calc_macros": "Macros", "portions": "Porciones", "import_btn": "Analizar",
        "url_ph": "Pegar enlace", "folder_new": "Nueva Colección", "add_shop": "A la lista", "clean_shop": "Limpiar", "clear_shop": "Borrar todo",
        "save_coll_title": "Colección", "save_coll_btn": "Añadir", "translating": "Traduciendo...", "logout": "Salir", "success": "¡Hecho!",
        "dash_intro": "Tu asistente inteligente.",
        "feat_1_t": "Importar", "feat_1_d": "De Insta/TikTok.",
        "feat_2_t": "Nutrición", "feat_2_d": "Macros auto.",
        "feat_3_t": "Compras", "feat_3_d": "Lista inteligente.",
        "feat_4_t": "Orden", "feat_4_d": "Organizar.",
        "prof_set": "Ajustes", "prof_lang": "Idioma", "prof_pw": "Contraseña",
        "pw_old": "Vieja", "pw_new": "Nueva", "pw_upd": "Actualizar", "pw_success": "¡Listo!"
    }
}
# Fallback
for l in ["FR", "IT", "PL"]: TRANSLATIONS[l] = TRANSLATIONS["EN"]

if "lang_code" not in st.session_state: st.session_state.lang_code = "EN"
def T(key): return TRANSLATIONS[st.session_state.lang_code].get(key, TRANSLATIONS["EN"].get(key, key))

# Interne Keys für die Logik (Reihenfolge muss matchen mit menu_opts!)
INTERNAL_KEYS = ["dashboard", "collections", "shopping", "cook", "import", "edit", "profile"]

# Alias
df_z = st.session_state.df_z; df_m = st.session_state.df_m
sh_z = st.session_state.sh_z; sh_s = st.session_state.sh_s; sh_m = st.session_state.sh_m; sh_e = st.session_state.sh_e; sh_o = st.session_state.sh_o
df_e = st.session_state.df_e; df_o = st.session_state.df_o

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
    st.markdown("### 👨‍🍳 MyCookbook")
    search_query = st.text_input("Search", placeholder=T("search_ph"), label_visibility="collapsed").lower().strip()
    st.write("") 
    
    if "internal_nav" not in st.session_state: st.session_state.internal_nav = "dashboard"
    
    # Menü Optionen (Mit Icons)
    options_display = T("menu_opts")
    
    # Index finden
    current_idx = 0
    if st.session_state.internal_nav in INTERNAL_KEYS:
        current_idx = INTERNAL_KEYS.index(st.session_state.internal_nav)
    
    selected_display = st.radio("nav_hidden", options_display, index=current_idx, label_visibility="collapsed")
    
    # Update State
    new_idx = options_display.index(selected_display)
    st.session_state.internal_nav = INTERNAL_KEYS[new_idx]
    
    st.divider()
    if st.button("⟳ Reload"): refresh_data()

# --- CARD RENDERER (LIST VIEW) ---
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
        # Spalten: Bild (klein) | Text (groß)
        c1, c2 = st.columns([1, 2]) 
        
        with c1:
            st.markdown(f"""<div class="list-img" style="background-image: url('{img}');"></div>""", unsafe_allow_html=True)
            
        with c2:
            st.markdown(f"""
            <div style="padding: 5px;">
                <span class="recipe-cat">{cat if cat else "Recipe"}</span>
                <div class="recipe-title" title="{r_name}">{r_name}</div>
            </div>
            """, unsafe_allow_html=True)
            
            b1, b2 = st.columns([3, 1])
            b1.button(T("to_rec"), key=f"btn_{context}_{r_name}", use_container_width=True, on_click=go_to_recipe_callback, args=(r_name,))
            fav_char = "★" if is_fav else "☆"
            if b2.button(fav_char, key=f"fav_{context}_{r_name}", use_container_width=True):
                fav_callback(r_name, is_fav)

# === CONTENT ===
active_nav = st.session_state.internal_nav

# 1. DASHBOARD
if active_nav == "dashboard":
    st.title(f"{T('welcome')}, {st.session_state.user_name}!")
    
    if df_z is None or df_z.empty:
        st.info(T("dash_intro"))
        c1, c2 = st.columns(2)
        if c1.button(f"📥 {T('feat_1_t')}", type="primary", use_container_width=True): 
            st.session_state.internal_nav = "import"; st.rerun()
        if c2.button(f"📝 {T('feat_4_t')}", use_container_width=True): 
            st.session_state.internal_nav = "edit"; st.rerun()
    else:
        if search_query:
            all_r = sorted(df_z['Rezept'].unique())
            filtered = [r for r in all_r if search_query in r.lower()]
            if not df_m.empty and 'Kategorie' in df_m.columns:
                 cat_matches = df_m[df_m['Kategorie'].str.lower().str.contains(search_query, na=False)]['Rezept'].tolist()
                 filtered = list(set(filtered + cat_matches))
            st.write(f"🔎 **{len(filtered)}**")
            if filtered:
                # WICHTIG: 2 Spalten Layout
                cols = st.columns(2)
                for i, r in enumerate(filtered): 
                    with cols[i%2]: render_card(r, "search")
            else: st.warning(T("no_rec"))
        else:
            if st.button(f"🎲 {T('random_btn')}", use_container_width=True):
                all_r = sorted(df_z['Rezept'].unique())
                if all_r:
                    r = random.choice(all_r)
                    go_to_recipe_callback(r); st.rerun()

            favs = df_z[df_z['is_fav'] == True]['Rezept'].unique()
            if len(favs) > 0:
                st.subheader(T("favs"))
                cols = st.columns(2)
                for i, f in enumerate(favs): 
                    with cols[i%2]: render_card(f, "fav")
                st.write("---")

            st.subheader(T("all_rec"))
            cats = st.multiselect("Filter", CATEGORIES, label_visibility="collapsed", placeholder="Kategorie...")
            all_r = sorted(df_z['Rezept'].unique())
            dis_list = [r for r in all_r if r not in favs]
            if cats and not df_m.empty:
                 valid = df_m[df_m['Kategorie'].isin(cats)]['Rezept'].tolist()
                 dis_list = [r for r in dis_list if r in valid]
            
            if dis_list:
                cols = st.columns(2)
                for i, r in enumerate(dis_list): 
                    with cols[i%2]: render_card(r, "all")

# 7. PROFIL
elif active_nav == "profile":
    st.title("Profile")
    st.info(f"👤 **{st.session_state.user_name}**\n\n{st.session_state.user_email}")
    if st.button(T("logout"), type="primary", use_container_width=True):
        st.session_state.user_email = None; st.session_state.user_name = None; st.rerun()
    st.divider()
    st.subheader(T("prof_set"))
    curr_lang_name = CODE_TO_NAME.get(st.session_state.lang_code, "English")
    sel_lang_name = st.selectbox(T("prof_lang"), list(LANGUAGES.keys()), index=list(LANGUAGES.keys()).index(curr_lang_name))
    if st.button(T("save")):
        new_code = LANGUAGES[sel_lang_name]
        update_user_language(st.session_state.user_email, new_code, st.session_state.sh_u)
        st.session_state.lang_code = new_code
        st.success(T("success")); time.sleep(1); st.rerun()
    st.divider()
    with st.expander(T("prof_pw")):
        with st.form("pw_change"):
            np1 = st.text_input(T("pw_new"), type="password")
            np2 = st.text_input("Confirm", type="password")
            if st.form_submit_button(T("pw_upd")):
                if np1 and np1 == np2:
                    change_user_password(st.session_state.user_email, np1, st.session_state.sh_u)
                    st.success(T("success"))
                else: st.error("Mismatch")

# 2. SAMMLUNGEN
elif active_nav == "collections":
    st.title(T("nav_coll"))
    with st.expander(f"➕ {T('folder_new')}"):
        with st.form("new_folder"):
            new_f = st.text_input("Name")
            if st.form_submit_button(T("save")) and new_f:
                if df_o.empty or new_f not in df_o['OrdnerName'].unique():
                    st.session_state.sh_o.append_row([new_f, "INIT_HIDDEN", st.session_state.user_email])
                    refresh_data()
    if not df_o.empty:
        folders = [f for f in df_o['OrdnerName'].unique() if f]
        sel_f = st.selectbox("Ordner", folders, label_visibility="collapsed")
        if sel_f:
            recs = [r for r in df_o[df_o['OrdnerName'] == sel_f]['Rezept'].unique() if r != "INIT_HIDDEN"]
            if recs:
                cols = st.columns(2)
                for i, r in enumerate(recs):
                    with cols[i%2]: render_card(r, f"coll_{sel_f}")
            else: st.info(T("no_rec"))

# 3. EINKAUF
elif active_nav == "shopping":
    st.title(T("nav_shop"))
    if not df_e.empty:
        local_df = df_e.copy()
        local_df['id'] = local_df['Zutat'] + "_" + local_df['Einheit']
        if "shop_checked" not in st.session_state: st.session_state.shop_checked = set()
        local_df['done'] = local_df['id'].apply(lambda x: x in st.session_state.shop_checked)
        local_df = local_df.sort_values(by=['done', 'Zutat'])
        def toggle(item_id):
            if item_id in st.session_state.shop_checked: st.session_state.shop_checked.remove(item_id)
            else: st.session_state.shop_checked.add(item_id)
        for _, row in local_df.iterrows():
            lbl = f"{row['Menge']} {row['Einheit']} {row['Zutat']}"
            st.checkbox(lbl, row['done'], key=f"chk_{row['id']}", on_change=toggle, args=(row['id'],))
        st.divider()
        c1, c2 = st.columns(2)
        if c1.button(T("clean_shop")):
             sync_shopping_list_to_db(local_df[~local_df['done']], st.session_state.sh_e)
             st.session_state.shop_checked = set()
             refresh_data()
        if c2.button(T("clear_shop"), type="secondary"):
             st.session_state.sh_e.clear(); st.session_state.sh_e.append_row(["Zutat", "Menge", "Einheit", "Owner"])
             refresh_data()
    else: st.info("Leer.")

# 4. KOCHEN
elif active_nav == "cook":
    if not df_z.empty:
        all_r = sorted(df_z['Rezept'].unique())
        idx = 0
        if "selected_recipe" in st.session_state and st.session_state.selected_recipe in all_r:
            idx = all_r.index(st.session_state.selected_recipe)
        rezept = st.selectbox("Rezept", all_r, index=idx, key="cook_selector", label_visibility="collapsed")
        
        if rezept:
            orig_z = df_z[df_z['Rezept'] == rezept]
            orig_s = st.session_state.df_s[st.session_state.df_s['Rezept'] == rezept]
            orig_m = df_m[df_m['Rezept'] == rezept]
            
            current_lang = st.session_state.lang_code
            display_data = {}
            if current_lang != "EN" and current_lang != "DE":
                cache_key = f"{rezept}_{current_lang}"
                if "trans_cache" in st.session_state and st.session_state.trans_cache.get("key") == cache_key:
                    display_data = st.session_state.trans_cache["data"]
                else:
                    with st.spinner(T("translating")):
                        z_list = orig_z[['Zutat', 'Menge', 'Einheit']].to_dict('records')
                        s_list = orig_s.sort_values('Schritt_Nr')['Anweisung'].tolist()
                        payload = {"Rezept": rezept, "Zutaten": z_list, "Schritte": s_list}
                        translated = translate_recipe_text(payload, st.session_state.lang_code)
                        display_data = translated
                        st.session_state.trans_cache = {"key": cache_key, "data": translated}
            else:
                display_data = {
                    "Rezept": rezept,
                    "Zutaten": orig_z[['Zutat', 'Menge', 'Einheit']].to_dict('records'),
                    "Schritte": orig_s.sort_values('Schritt_Nr')['Anweisung'].tolist()
                }

            bp = float(orig_m['Portionen'].iloc[0]) if not orig_m.empty and orig_m['Portionen'].iloc[0] else 2.0
            img = PLACEHOLDER_IMG; url = ""
            if not orig_m.empty:
                r0 = orig_m.iloc[0]
                if str(r0['BildURL']).startswith(("http", "data:")): img = r0['BildURL']
                if str(r0['OriginalURL']).startswith("http"): url = r0['OriginalURL']

            st.markdown(f"""<div style="width: 100%; height: 250px; background-image: url('{img}'); background-size: cover; background-position: center; border-radius: 12px; margin-bottom: 20px;"></div>""", unsafe_allow_html=True)
            st.markdown(f"### {display_data.get('Rezept', rezept)}")
            
            c_fav, c_coll = st.columns(2)
            is_fav = orig_z['is_fav'].iloc[0] if not orig_z.empty else False
            if c_fav.button("★ Favorit" if not is_fav else "☆ Entfernen", use_container_width=True):
                toggle_favorit(rezept, is_fav, sh_z); refresh_data()
            
            with c_coll.popover(T("save_coll_btn"), use_container_width=True):
                if not df_o.empty:
                    tf = st.selectbox("Ordner", [f for f in df_o['OrdnerName'].unique() if f])
                    if st.button("Speichern"):
                        add_to_folder_db(tf, rezept, st.session_state.sh_o); st.toast(T("success"))

            if url: st.markdown(f"[Original Video]({url})")
            st.divider()
            
            c_p, c_shop = st.columns([1, 2])
            wp = c_p.number_input(T("portions"), 1, value=int(bp))
            fak = wp / bp if bp > 0 else 1
            if c_shop.button(f"🛒 {T('add_shop')}", use_container_width=True):
                tmp = orig_z.copy(); tmp['Menge'] *= fak
                add_to_shopping_list(tmp, st.session_state.sh_e); refresh_data(); st.toast(T("success"))
            
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
            if st.button(f"✏️ {T('nav_edit')}", use_container_width=True):
                 st.session_state.edit_recipe_name = rezept; st.session_state.internal_nav = "edit"; st.rerun()

# 5. IMPORT
elif active_nav == "import":
    st.title(T("nav_import"))
    u = st.text_input(T("url_ph"))
    if st.button(T("import_btn"), type="primary", use_container_width=True):
        with st.spinner("..."):
            c, th, err = get_web_content(u)
            if c:
                d = rezept_analysieren(c, th, u, "TRANSCRIPT" not in c)
                if isinstance(c, str) and "temp_audio" in c and os.path.exists(c): os.remove(c)
                if d:
                    save_recipe_to_db(d, sh_z, st.session_state.sh_s, st.session_state.sh_m, True)
                    st.success(T("success")); time.sleep(2); refresh_data()
            else: st.error(err)

# 6. EDITOR
elif active_nav == "edit":
    st.title(T("nav_edit"))
    all_r = sorted(df_z['Rezept'].unique()) if not df_z.empty else []
    
    pi = 0
    if "edit_recipe_name" in st.session_state and st.session_state.edit_recipe_name in all_r:
        pi = all_r.index(st.session_state.edit_recipe_name)
    es = st.selectbox("Rezept wählen", all_r, index=pi)
    
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
        n_img = c2.text_input("Bild URL", cm.iloc[0]['BildURL'] if not cm.empty else "")
        n_url = c2.text_input("Original Link", cm.iloc[0]['OriginalURL'] if not cm.empty else "")
        cat_idx = 0
        if not cm.empty and cm.iloc[0]['Kategorie'] in CATEGORIES: cat_idx = CATEGORIES.index(cm.iloc[0]['Kategorie'])
        n_cat = c1.selectbox("Kategorie", CATEGORIES, index=cat_idx)
        
        bp = st.number_input(T("portions"), value=float(cm['Portionen'].iloc[0]) if not cm.empty else 2.0)
        
        st.subheader("Zutaten")
        ez = st.data_editor(cz, num_rows="dynamic", use_container_width=True)
        st.subheader("Schritte")
        es_df = st.data_editor(cs, num_rows="dynamic", use_container_width=True)
        
        if st.button(T("calc_macros"), use_container_width=True):
            zt = "".join([f"{r['Menge']} {r['Einheit']} {r['Zutat']}\n" for _, r in ez.iterrows()])
            stt = "\n".join(es_df['Anweisung'].tolist())
            nm = makros_neu_berechnen(zt, stt, bp)
            if nm:
                for k, v in nm.items(): st.session_state[f"edit_{k.lower()}"] = v
                st.rerun()

        c1, c2, c3, c4 = st.columns(4)
        nk = c1.number_input("Kcal", key="edit_kcal")
        np = c2.number_input("Prot", key="edit_protein")
        nc = c3.number_input("Carb", key="edit_carbs")
        nf = c4.number_input("Fett", key="edit_fett")
        
        st.write("")
        if st.button(T("save"), type="primary", use_container_width=True):
            jd = {
                "Rezept": nn, "Portionen": bp, "BildURL": n_img, "OriginalURL": n_url, "Kategorie": n_cat,
                "Makros": {"Kcal": nk, "Protein": np, "Carbs": nc, "Fett": nf},
                "Zutaten": ez.to_dict('records'), "Schritte": es_df['Anweisung'].tolist()
            }
            if nn != es: delete_recipe_from_db(es, sh_z, st.session_state.sh_s, st.session_state.sh_m)
            save_recipe_to_db(jd, sh_z, st.session_state.sh_s, st.session_state.sh_m, True)
            st.success(T("success")); time.sleep(2); refresh_data()
        
        if st.button(T("delete"), use_container_width=True):
            delete_recipe_from_db(es, sh_z, st.session_state.sh_s, st.session_state.sh_m)
            refresh_data()
