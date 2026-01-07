import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* --- FONT: INTER & GLOBAL --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
        
        :root {
            --bg-color: #ffffff;
            --card-bg: #ffffff;
            --text-color: #111111;
            --sub-text: #666666;
            --accent-color: #000000;
            --nav-hover: #f0f2f6;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
        }

        /* --- SIDEBAR MENU (Modern Button Look) --- */
        [data-testid="stSidebar"] {
            background-color: #f9f9f9;
            padding-top: 20px;
        }
        
        /* Radio Buttons verstecken und Styling ändern */
        .stRadio > div {
            gap: 10px;
        }
        
        /* Das Label des Radio Buttons (der Text) */
        .stRadio label {
            background-color: white;
            padding: 12px 16px !important;
            border-radius: 12px;
            border: 1px solid #e5e5e5;
            cursor: pointer;
            transition: all 0.2s;
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            width: 100%;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }
        
        /* Verstecke den eigentlichen Radio-Kreis */
        .stRadio div[role="radiogroup"] > label > div:first-child {
            display: none;
        }
        
        /* Text im Button */
        .stRadio label p {
            font-size: 16px !important; /* Größer wie gewünscht */
            font-weight: 500;
            margin: 0;
            color: #333;
        }

        /* Hover Effekt */
        .stRadio label:hover {
            border-color: #ccc;
            background-color: #fafafa;
        }

        /* AKTIVER STATUS (Ausgewählt) */
        .stRadio label[data-checked="true"] {
            background-color: #000000 !important;
            border-color: #000000 !important;
            color: white !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        
        .stRadio label[data-checked="true"] p {
            color: #ffffff !important;
        }

        /* --- REZEPT KARTEN --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: none;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            border-radius: 16px; /* Rundere Ecken */
            overflow: hidden;
            background: white;
            transition: transform 0.2s;
            margin-bottom: 10px;
        }
        
        /* BILD HOCHFORMAT (Portrait) */
        .recipe-card-img {
            width: 100%;
            padding-top: 150%; /* 1:1.5 Verhältnis (Hochformat) */
            background-size: cover;
            background-position: center;
            border-bottom: 1px solid #f0f0f0;
        }

        /* TEXT BODY */
        .card-content {
            padding: 12px;
        }

        .recipe-title {
            font-weight: 700;
            font-size: 16px; /* +3px größer */
            color: #000;
            line-height: 1.3;
            margin-bottom: 4px;
            display: -webkit-box;
            -webkit-line-clamp: 2; /* Max 2 Zeilen */
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        
        .recipe-cat {
            font-size: 12px; /* Auch größer */
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 12px;
            display: block;
        }

        /* BUTTONS IN KARTE */
        div.stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            padding: 0.5rem 1rem;
            border: 1px solid #eee;
            background-color: #f7f7f7;
            color: #333;
            width: 100%;
            transition: all 0.2s;
        }
        div.stButton > button:hover {
            background-color: #e0e0e0;
            border-color: #ccc;
        }
        /* Favoriten Stern Button transparent */
        div.stButton > button:focus:not(:active) {
            border-color: #000;
            color: #000;
        }

        /* --- MOBILE LAYOUT OPTIMIERUNG (< 768px) --- */
        @media (max-width: 768px) {
            
            /* Zwingt Spalten nebeneinander (2 Spalten Layout) */
            [data-testid="column"] {
                width: 50% !important;
                flex: 1 1 50% !important;
                min-width: 50% !important;
                padding: 0 6px !important; /* Abstand zwischen Spalten */
            }
            
            /* Text Anpassung Mobile */
            .recipe-title {
                font-size: 15px !important; /* Gut lesbar */
            }
            .recipe-cat {
                font-size: 11px !important;
            }
            
            /* Buttons kompakter auf Mobile */
            div.stButton > button {
                font-size: 13px !important;
                padding: 6px 4px !important;
            }
            
            /* Container Abstände */
            .block-container {
                padding-top: 2rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)
