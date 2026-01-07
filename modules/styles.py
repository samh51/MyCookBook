import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* --- FONT & COLORS (Light/Dark Auto) --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        :root {
            --bg-color: #ffffff;
            --text-color: #111111;
            --card-bg: #ffffff;
            --border-color: #e5e5e5;
            --nav-bg: #f9f9f9;
            --accent: #000000;
            --accent-text: #ffffff;
        }

        /* DARK MODE OVERRIDES */
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-color: #0e1117;
                --text-color: #fafafa;
                --card-bg: #262730;
                --border-color: #3b3c45;
                --nav-bg: #1a1c24;
                --accent: #ffffff;
                --accent-text: #000000;
            }
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            background-color: var(--bg-color);
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: var(--nav-bg);
        }
        
        /* Navigation Label verstecken */
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            display: none !important;
        }

        /* --- NAVIGATION BUTTONS (Einheitlich) --- */
        .stRadio > div { gap: 8px; width: 100%; }
        
        .stRadio label {
            background-color: var(--card-bg);
            padding: 12px 15px !important;
            border-radius: 10px;
            border: 1px solid var(--border-color);
            cursor: pointer;
            margin-bottom: 0px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            width: 100%; /* Volle Breite */
            display: flex;
            align-items: center;
        }
        
        .stRadio div[role="radiogroup"] > label > div:first-child { display: none; }
        
        .stRadio label p {
            font-size: 15px !important;
            font-weight: 600;
            margin: 0;
            color: var(--text-color);
            width: 100%;
        }

        /* Active State */
        .stRadio label[data-checked="true"] {
            background-color: var(--accent) !important;
            border-color: var(--accent) !important;
        }
        .stRadio label[data-checked="true"] p { color: var(--accent-text) !important; }

        /* --- PRIMARY BUTTONS (Login Fix) --- */
        div.stButton > button[kind="primary"] {
            background-color: var(--accent);
            color: var(--accent-text);
            border: 1px solid var(--accent);
            border-radius: 8px;
            font-weight: 600;
        }
        div.stButton > button[kind="primary"]:hover {
            opacity: 0.9;
            color: var(--accent-text);
        }
        
        /* Secondary Buttons */
        div.stButton > button[kind="secondary"] {
            background-color: var(--card-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        /* --- CARD DESIGN --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid var(--border-color);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-radius: 12px;
            overflow: hidden;
            background: var(--card-bg);
            margin-bottom: 8px;
            padding: 0 !important;
        }
        
        /* BILD */
        .list-img {
            width: 100%;
            height: 100%;
            min-height: 110px;
            background-size: cover;
            background-position: center;
            border-right: 1px solid var(--border-color);
        }

        /* TEXT */
        .recipe-title {
            font-weight: 700;
            font-size: 15px;
            color: var(--text-color);
            line-height: 1.3;
            margin-bottom: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .recipe-cat {
            font-size: 11px;
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 6px;
            display: block;
        }

        /* --- MOBILE GRID FORCE (Der entscheidende Teil) --- */
        @media (max-width: 768px) {
            
            /* Login/Dashboard Intro Buttons Lesbarkeit */
            .stButton button {
                width: 100%;
            }

            /* HIER ZWINGEN WIR DAS GRID */
            [data-testid="column"] {
                width: 50% !important;
                flex: 0 0 50% !important;
                min-width: 50% !important;
                max-width: 50% !important;
                padding: 0 4px !important;
            }
            
            /* Verhindert, dass Streamlit Spalten untereinander stapelt */
            [data-testid="column"] > div {
                width: 100% !important;
            }
            
            /* Toast Nachricht */
            .stToast { top: 10px; right: 10px; max-width: 90%; }
        }
        </style>
    """, unsafe_allow_html=True)
