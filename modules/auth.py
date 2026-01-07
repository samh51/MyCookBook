import streamlit as st
import bcrypt
import pandas as pd
import time

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    try: return bcrypt.checkpw(password.encode(), hashed.encode())
    except: return False

def update_user_language(email, new_lang_code, sh_users):
    """Aktualisiert die Sprache in der DB"""
    try:
        cell = sh_users.find(email)
        # Sprache ist Spalte 4 (D)
        sh_users.update_cell(cell.row, 4, new_lang_code)
        return True
    except: return False

def change_user_password(email, new_pw, sh_users):
    """Aktualisiert das Passwort"""
    try:
        cell = sh_users.find(email)
        new_hash = hash_password(new_pw)
        # Passwort ist Spalte 2 (B)
        sh_users.update_cell(cell.row, 2, new_hash)
        return True
    except: return False

def login_form(sh_users):
    """Login Maske"""
    if "user_email" not in st.session_state: st.session_state.user_email = None
    if "user_name" not in st.session_state: st.session_state.user_name = None
    
    # Standard Sprache Englisch, falls noch nichts gesetzt
    if "lang_code" not in st.session_state: st.session_state.lang_code = "EN"

    if st.session_state.user_email: return True

    c_center = st.container()
    
    with c_center:
        st.markdown("<br><br><h1 style='text-align: center;'>My Cookbook 🌿</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Your personal AI kitchen assistant.</p><br>", unsafe_allow_html=True)
        
        tab_login, tab_register = st.tabs(["Login", "Sign Up"])
        
        # --- LOGIN ---
        with tab_login:
            email = st.text_input("Email", key="l_email").lower().strip()
            password = st.text_input("Password", type="password", key="l_pw")
            remember = st.checkbox("Stay signed in on this device") # UI Element
            
            st.write("")
            if st.button("Login", type="primary", use_container_width=True):
                users = sh_users.get_all_records()
                user_found = False
                for u in users:
                    if u['Email'] == email:
                        if check_password(password, u['Password']):
                            st.session_state.user_email = email
                            st.session_state.user_name = u['Name']
                            
                            # Sprache laden
                            user_lang = u.get('Language', 'EN')
                            st.session_state.lang_code = user_lang if user_lang else "EN"
                            
                            st.success(f"Welcome back, {u['Name']}!")
                            time.sleep(0.5); st.rerun()
                        else: st.error("Wrong password.")
                        user_found = True; break
                if not user_found: st.error("User not found.")

        # --- REGISTER ---
        with tab_register:
            c1, c2 = st.columns(2)
            new_name = c1.text_input("Your Name", key="r_name")
            
            lang_options = {"English": "EN", "Deutsch": "DE", "Español": "ES", "Français": "FR", "Italiano": "IT", "Polski": "PL"}
            sel_lang = c2.selectbox("Language", list(lang_options.keys()))
            
            new_email = st.text_input("Email Address", key="r_email").lower().strip()
            new_pw = st.text_input("Choose Password", type="password", key="r_pw")
            new_pw2 = st.text_input("Confirm Password", type="password", key="r_pw2")
            
            if st.button("Create Account", type="primary", use_container_width=True):
                if new_pw != new_pw2: st.error("Passwords do not match.")
                elif not new_email or not new_name or not new_pw: st.error("Please fill in all fields.")
                else:
                    users = sh_users.get_all_records()
                    if any(u['Email'] == new_email for u in users): st.error("Email already registered.")
                    else:
                        hashed = hash_password(new_pw)
                        sh_users.append_row([new_email, hashed, new_name, lang_options[sel_lang]])
                        st.success("Account created! Please log in.")

    return False