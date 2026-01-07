import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #111;
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #f9f9f9;
        }
        
        /* Das "Navigation" Label sauber verstecken (nur das obere) */
        [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            display: none !important;
        }

        /* RADIO BUTTONS (Kacheln) */
        .stRadio > div { gap: 6px; }
        
        .stRadio label {
            background-color: white;
            padding: 10px 12px !important;
            border-radius: 8px;
            border: 1px solid #e5e5e5;
            cursor: pointer;
            margin-bottom: 2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }
        
        .stRadio div[role="radiogroup"] > label > div:first-child { display: none; }
        
        .stRadio label p {
            font-size: 15px !important;
            font-weight: 500;
            margin: 0;
            color: #444;
        }

        /* Active State */
        .stRadio label[data-checked="true"] {
            background-color: #000000 !important;
            border-color: #000000 !important;
        }
        .stRadio label[data-checked="true"] p { color: #ffffff !important; }

        /* --- LIST CARD (Container) --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 1px solid #f0f0f0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.04);
            border-radius: 12px;
            background: white;
            margin-bottom: 12px;
            padding: 8px !important; /* Innenabstand für den Rahmen */
        }
        
        /* BILD (Links) */
        .list-img {
            width: 100%;
            height: 100px; /* Feste Höhe für Einheitlichkeit */
            background-size: cover;
            background-position: center;
            border-radius: 8px;
        }

        /* TITEL */
        .recipe-title {
            font-weight: 700;
            font-size: 16px;
            color: #000;
            line-height: 1.2;
            margin-bottom: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 2; /* Max 2 Zeilen Text */
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        /* KATEGORIE */
        .recipe-cat {
            font-size: 11px;
            color: #888;
            font-weight: 600;
            text-transform: uppercase;
            margin-bottom: 8px;
            display: block;
        }

        /* BUTTONS (Kompakt) */
        div.stButton > button {
            border-radius: 6px;
            font-weight: 500;
            font-size: 12px !important;
            padding: 2px 0px;
            min-height: 32px;
            border: 1px solid #eee;
            background-color: #fff;
        }
        
        /* Mobile Anpassungen */
        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                margin-bottom: 8px;
            }
        }
        </style>
    """, unsafe_allow_html=True)
