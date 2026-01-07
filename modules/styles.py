import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* --- FONT: INTER (Wie Apple/Modern UI) --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        /* --- GLOBAL VARIABLES --- */
        :root {
            --bg-color: #ffffff;
            --sidebar-bg: #f5f5f7; /* Apple Light Gray */
            --text-color: #1d1d1f; /* Fast Schwarz */
            --accent-color: #000000;
            --border-color: #e5e5e5;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            background-color: var(--bg-color);
        }
        
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            letter-spacing: -0.5px; /* Modernes Tight-Tracking */
            color: #000000;
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
            border-right: 1px solid transparent;
        }

        /* Verstecke Standard Radio Buttons */
        .stRadio > label { display: none !important; }
        div[role="radiogroup"] > label > div:first-child { display: none; }
        
        div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 8px;
            padding: 10px 0;
        }
        
        /* MENU ITEMS (Minimalistisch) */
        div[role="radiogroup"] label {
            display: flex;
            align-items: center;
            width: 100%;
            height: 45px;
            background-color: transparent; /* Kein Hintergrund normal */
            border-radius: 8px;
            border: none;
            margin: 0 !important;
            padding-left: 15px !important;
            cursor: pointer;
            transition: all 0.2s ease;
            color: #666;
        }
        
        div[role="radiogroup"] label p {
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            font-weight: 500;
            margin: 0;
        }
        
        /* HOVER */
        div[role="radiogroup"] label:hover {
            background-color: rgba(0,0,0,0.05);
            color: #000;
        }
        
        /* ACTIVE STATE (Schwarz markiert) */
        div[role="radiogroup"] label[data-checked="true"] {
            background-color: #000000 !important;
            color: #ffffff !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        div[role="radiogroup"] label[data-checked="true"] p {
            color: #ffffff !important;
        }

        /* --- CARDS (Clean & Flat) --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 0; /* Bild geht bis an den Rand */
            overflow: hidden;
            transition: all 0.3s ease;
            min-height: 380px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: none;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            border-color: transparent;
        }
        
        /* Inneres Padding für Text in der Karte */
        div[data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(2) {
            padding: 15px;
        }

        /* BILD */
        .recipe-card-img {
            width: 100%;
            padding-top: 100%; /* Quadratisch */
            background-size: cover;
            background-position: center;
            border-bottom: 1px solid var(--border-color);
        }

        /* TYPO IN KARTE */
        .recipe-title {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 1.1rem;
            color: #000;
            margin-bottom: 4px;
            display: block;
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis;
        }
        
        .recipe-cat {
            font-size: 0.8rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }

        /* --- BUTTONS (Schwarz/Weiß) --- */
        div.stButton > button {
            background-color: #000000;
            color: #ffffff;
            border-radius: 8px;
            font-weight: 500;
            font-size: 14px;
            padding: 10px 20px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }
        
        div.stButton > button:hover {
            background-color: #333333;
            color: #ffffff;
            border-color: transparent;
            transform: scale(1.02);
        }
        
        /* Sekundäre Buttons (z.B. Favorit entfernen) */
        button[kind="secondary"] {
            background-color: #f5f5f7 !important;
            color: #000 !important;
            border: 1px solid #e5e5e5 !important;
        }

        /* INPUT FIELDS */
        .stTextInput > div > div > input {
            background-color: #f5f5f7;
            border: none;
            border-radius: 8px;
            padding: 10px 12px;
            color: #000;
        }
        .stTextInput > div > div > input:focus {
            background-color: #fff;
            box-shadow: 0 0 0 2px #000; /* Schwarzer Focus Ring */
        }
        
        /* Metric Styling */
        div[data-testid="stMetricValue"] {
            color: #000 !important;
            font-weight: 600;
        }
        </style>
    """, unsafe_allow_html=True)