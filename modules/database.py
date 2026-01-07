import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import streamlit as st
import json
import os
import time  # WICHTIG
from .utils import download_and_compress_image, PLACEHOLDER_IMG

SHEET_NAME = "MeineRezepte"

# --- NEU: RETRY DECORATOR ---
def safe_read(worksheet):
    """Versucht Daten zu lesen, mit Wartezeit bei API-Limits"""
    for i in range(5): # 5 Versuche
        try:
            return worksheet.get_all_records()
        except Exception as e:
            if "429" in str(e) or "Quota exceeded" in str(e):
                wait_time = (2 ** i) + random.random() # Exponential Backoff: 1s, 2s, 4s...
                print(f"⚠️ API Limit erreicht. Warte {round(wait_time, 1)}s...")
                time.sleep(wait_time)
            else:
                raise e # Andere Fehler werfen
    return []

def get_db_connection():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.path.exists("credentials.json"):
            with open("credentials.json", "r") as f: creds = ServiceAccountCredentials.from_json_keyfile_dict(json.load(f), scope)
        else: creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(st.secrets["gcp_service_account"]), scope)
            
        client = gspread.authorize(creds)
        spreadsheet = client.open(SHEET_NAME)
        return spreadsheet
    except Exception as e:
        st.error(f"DB Verbindungsfehler: {e}")
        return None

def get_data(user_email=None):
    spreadsheet = get_db_connection()
    if not spreadsheet: return [None]*13

    def get_or_create(title, cols, head):
        try: return spreadsheet.worksheet(title)
        except: 
            ws = spreadsheet.add_worksheet(title, 1000, cols); ws.append_row(head)
            return ws

    sh_z = get_or_create("Zutaten", 10, ["Rezept", "Zutat", "Menge", "Einheit", "Favorit", "Owner"])
    sh_s = get_or_create("Anleitungen", 5, ["Rezept", "Schritt_Nr", "Anweisung", "Owner"])
    sh_b = get_or_create("Basics", 2, ["Zutat"])
    sh_m = get_or_create("Metadaten", 10, ["Rezept", "Portionen", "Kcal", "Protein", "Carbs", "Fett", "BildURL", "OriginalURL", "Kategorie", "Owner"])
    sh_e = get_or_create("Einkauf", 4, ["Zutat", "Menge", "Einheit", "Owner"])
    sh_o = get_or_create("Ordner", 3, ["OrdnerName", "Rezept", "Owner"])
    sh_u = get_or_create("Users", 4, ["Email", "Password", "Name", "Language"])

    try:
        headers_m = sh_m.row_values(1)
        if "Kategorie" not in headers_m: sh_m.update_cell(1, 9, "Kategorie")
        if "Owner" not in headers_m: sh_m.update_cell(1, 10, "Owner")
    except: pass

    def load_clean_df(sh, cols_expected):
        # HIER NUTZEN WIR JETZT safe_read STATT get_all_records
        recs = safe_read(sh) 
        df = pd.DataFrame(recs)
        if df.empty: return pd.DataFrame(columns=cols_expected)
        for col in cols_expected:
            if col not in df.columns: df[col] = ""
        return df

    df_z = load_clean_df(sh_z, ["Rezept", "Zutat", "Menge", "Einheit", "Favorit", "Owner"])
    df_s = load_clean_df(sh_s, ["Rezept", "Schritt_Nr", "Anweisung", "Owner"])
    df_m = load_clean_df(sh_m, ["Rezept", "Portionen", "Kcal", "Protein", "Carbs", "Fett", "BildURL", "OriginalURL", "Kategorie", "Owner"])
    df_e = load_clean_df(sh_e, ["Zutat", "Menge", "Einheit", "Owner"])
    df_o = load_clean_df(sh_o, ["OrdnerName", "Rezept", "Owner"])
    basics = [] # Basics laden wir hier nicht zwingend jedes Mal, spart Calls

    if user_email:
        if not df_z.empty and 'Owner' in df_z.columns: df_z = df_z[df_z['Owner'] == user_email]
        if not df_s.empty and 'Owner' in df_s.columns: df_s = df_s[df_s['Owner'] == user_email]
        if not df_m.empty and 'Owner' in df_m.columns: df_m = df_m[df_m['Owner'] == user_email]
        if not df_e.empty and 'Owner' in df_e.columns: df_e = df_e[df_e['Owner'] == user_email]
        if not df_o.empty and 'Owner' in df_o.columns: df_o = df_o[df_o['Owner'] == user_email]

    if not df_z.empty:
        df_z['Menge'] = pd.to_numeric(df_z['Menge'], errors='coerce').fillna(0)
        df_z['is_fav'] = df_z['Favorit'].astype(str).str.lower().isin(['true', '1', 'ja'])
    if not df_m.empty:
         for c in ["Portionen", "Kcal", "Protein", "Carbs", "Fett"]: 
             if c in df_m.columns: df_m[c] = pd.to_numeric(df_m[c], errors='coerce').fillna(0)
         df_m["BildURL"].replace("", PLACEHOLDER_IMG, inplace=True)
    if not df_e.empty: 
        df_e['Menge'] = pd.to_numeric(df_e['Menge'], errors='coerce').fillna(0)

    return df_z, df_s, df_m, df_e, df_o, basics, sh_z, sh_s, sh_b, sh_m, sh_e, sh_o, sh_u

def delete_recipe_from_db(name, sh_z, sh_s, sh_m):
    user = st.session_state.user_email
    if not user: return

    def clean_sheet_for_user(sh, name_col_idx, owner_col_idx):
        vals = sh.get_all_values()
        if not vals: return
        header = vals[0]
        new_data = []
        for row in vals[1:]:
            if len(row) > max(name_col_idx, owner_col_idx):
                r_name = row[name_col_idx]
                r_owner = row[owner_col_idx]
                if r_name == name and r_owner == user: continue 
                new_data.append(row)
            else: new_data.append(row)
        sh.clear(); sh.append_row(header)
        if new_data: sh.append_rows(new_data)

    clean_sheet_for_user(sh_z, 0, 5)
    clean_sheet_for_user(sh_s, 0, 3)
    clean_sheet_for_user(sh_m, 0, 9)

def save_recipe_to_db(data, sh_z, sh_s, sh_m, update_mode=False):
    name = data["Rezept"]
    user = st.session_state.user_email
    if not user: return

    if update_mode: delete_recipe_from_db(name, sh_z, sh_s, sh_m)
    
    m = data.get("Makros", {})
    raw_img = data.get("BildURL", PLACEHOLDER_IMG)
    if raw_img and raw_img.startswith("http") and not "placeholder" in raw_img:
        with st.spinner("Speichere Bild..."):
            final_img = download_and_compress_image(raw_img)
    else: final_img = raw_img

    sh_m.append_row([
        name, data.get("Portionen", 2), m.get("Kcal", 0), m.get("Protein", 0), m.get("Carbs", 0), m.get("Fett", 0), 
        final_img, data.get("OriginalURL", ""), data.get("Kategorie", "Sonstiges"), user
    ])
    
    rows_z = [[name, z["Zutat"], z["Menge"], z["Einheit"], "", user] for z in data["Zutaten"]]
    if rows_z: sh_z.append_rows(rows_z)
    
    rows_s = [[name, i+1, s, user] for i, s in enumerate(data["Schritte"])]
    if rows_s: sh_s.append_rows(rows_s)

def toggle_favorit(name, status, sh):
    user = st.session_state.user_email
    try:
        cell_list = sh.findall(name)
        for cell in cell_list:
            row_vals = sh.row_values(cell.row)
            if len(row_vals) > 5 and row_vals[5] == user:
                sh.update_cell(cell.row, 5, "" if status else "TRUE")
    except: pass

def add_to_folder_db(folder_name, recipe_name, sh_o):
    user = st.session_state.user_email
    current = sh_o.get_all_records()
    for row in current:
        if row['OrdnerName'] == folder_name and row['Rezept'] == recipe_name and row.get('Owner') == user:
            return
    sh_o.append_row([folder_name, recipe_name, user])

def add_to_shopping_list(ingredients_df, sh_e):
    user = st.session_state.user_email
    all_recs = sh_e.get_all_records()
    df_current = pd.DataFrame(all_recs)
    
    user_df = pd.DataFrame()
    other_users_rows = []
    if not df_current.empty and 'Owner' in df_current.columns:
        user_df = df_current[df_current['Owner'] == user].copy()
        other_users_rows = df_current[df_current['Owner'] != user].values.tolist()

    new_data = ingredients_df[['Zutat', 'Menge', 'Einheit']].copy()
    if not user_df.empty:
        user_df['Menge'] = pd.to_numeric(user_df['Menge'], errors='coerce').fillna(0)
        combined = pd.concat([user_df, new_data])
    else: combined = new_data
    
    combined['Zutat_Norm'] = combined['Zutat'].str.lower().str.strip()
    combined['Einheit_Norm'] = combined['Einheit'].str.lower().str.strip()
    
    grouped = combined.groupby(['Zutat_Norm', 'Einheit_Norm'], as_index=False).agg({
        'Menge': 'sum', 'Zutat': 'first', 'Einheit': 'first'
    })
    
    sh_e.clear(); sh_e.append_row(["Zutat", "Menge", "Einheit", "Owner"])
    my_rows = [[row['Zutat'], row['Menge'], row['Einheit'], user] for _, row in grouped.iterrows() if row['Menge'] > 0]
    if other_users_rows: sh_e.append_rows(other_users_rows)
    if my_rows: sh_e.append_rows(my_rows)

def sync_shopping_list_to_db(df_active, sh_e):
    user = st.session_state.user_email
    all_recs = sh_e.get_all_records()
    df_all = pd.DataFrame(all_recs)
    
    other_rows = []
    if not df_all.empty and 'Owner' in df_all.columns:
        other_rows = df_all[df_all['Owner'] != user].values.tolist()
        
    my_rows = [[row['Zutat'], row['Menge'], row['Einheit'], user] for _, row in df_active.iterrows()]
    
    sh_e.clear(); sh_e.append_row(["Zutat", "Menge", "Einheit", "Owner"])
    if other_rows: sh_e.append_rows(other_rows)
    if my_rows: sh_e.append_rows(my_rows)