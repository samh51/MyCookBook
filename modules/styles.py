import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* --- FONT: INTER --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        :root {
            --bg-color: #ffffff;
            --text-color: #111111;
            --sub-text: #666666;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
        }

        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: #f9f9f9;
        }
        
        /* WICHTIG: Versteckt das Label "Navigation" über den Radio Buttons komplett */
        [data-testid="stSidebar"] label {
            display: none !important;
        }

        /* --- RADIO BUTTONS (Kacheln) --- */
        .stRadio > div { gap: 8px; }
        
        .stRadio label {
            background-color: white;
            padding: 10px 14px !important;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            cursor: pointer;
            margin-bottom: 2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }
        
        /* Kreis weg */
        .stRadio div[role="radiogroup"] > label > div:first-child { display: none; }
        
        /* Text Styling */
        .stRadio label p {
            font-size: 15px !important;
            font-weight: 600;
            margin: 0;
            color: #444;
        }

        /* Active State */
        .stRadio label[data-checked="true"] {
            background-color: #000000 !important;
            border-color: #000000 !important;
        }
        .stRadio label[data-checked="true"] p { color: #ffffff !important; }

        /* --- REZEPT KARTEN --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-radius: 12px;
            overflow: hidden;
            background: white;
            margin-bottom: 8px;
        }
        
        /* Bild Hochformat 9:16 Optimiert */
        .recipe-card-img {
            width: 100%;
            padding-top: 130%; /* Hochformat */
            background-size: cover;
            background-position: center;
        }

        /* Text Bereich */
        .card-content { padding: 8px 8px 4px 8px; }

        .recipe-title {
            font-weight: 700;
            font-size: 15px; /* Lesbar */
            color: #000;
            line-height: 1.2;
            margin-bottom: 2px;
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis;
        }
        
        .recipe-cat {
            font-size: 11px;
            color: #888;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 6px;
            display: block;
        }

        /* Buttons */
        div.stButton > button {
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            padding: 4px 0px;
            border: 1px solid #eee;
            background-color: #f7f7f7;
            color: #333;
            width: 100%;
            min-height: 32px;
        }

        /* --- MOBILE LAYOUT FIX (2 SPALTEN ERZWINGEN) --- */
        @media (max-width: 768px) {
            
            /* Container für Spalten */
            [data-testid="column"] {
                width: 48% !important;        /* Etwas weniger als 50% wegen Gaps */
                flex: 0 0 48% !important;     /* Flexgrow verhindern */
                min-width: 0 !important;      /* WICHTIG: Erlaubt Verkleinern */
                padding: 0 4px !important;    /* Engere Abstände */
            }
            
            /* Fix für Streamlit Spalten-Gap */
            [data-testid="column"] > div {
                width: 100% !important;
            }

            /* Container padding reduzieren */
            .block-container {
                padding-top: 1rem !important;
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
            
            /* Schriftgröße auf Mobile leicht anpassen */
            .recipe-title { font-size: 14px !important; }
            .recipe-cat { font-size: 10px !important; }
            
            /* Toast nach oben */
            .stToast { top: 5px; right: 5px; width: 90%; }
        }
        </style>
    """, unsafe_allow_html=True)
