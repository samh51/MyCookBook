import streamlit as st

def apply_custom_css():
    st.markdown("""
        <style>
        /* --- FONT: INTER (Wie Apple/Modern UI) --- */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        /* --- GLOBAL VARIABLES --- */
        :root {
            --bg-color: #ffffff;
            --sidebar-bg: #f5f5f7;
            --text-color: #1d1d1f;
            --border-color: #e5e5e5;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
            background-color: var(--bg-color);
        }
        
        /* --- SIDEBAR --- */
        [data-testid="stSidebar"] {
            background-color: var(--sidebar-bg);
        }

        /* --- CARDS (Desktop Standard) --- */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 8px; /* Etwas eckiger für Modern Look */
            padding: 0;
            overflow: hidden;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
        
        /* BILD */
        .recipe-card-img {
            width: 100%;
            padding-top: 75%; /* 4:3 Format statt Quadratisch (Platz sparen) */
            background-size: cover;
            background-position: center;
            border-bottom: 1px solid var(--border-color);
        }

        /* TEXT BODY */
        div[data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(2) {
            padding: 10px;
        }

        .recipe-title {
            font-weight: 600;
            font-size: 1rem;
            color: #000;
            margin-bottom: 2px;
            display: block;
            white-space: nowrap; 
            overflow: hidden; 
            text-overflow: ellipsis;
        }
        
        .recipe-cat {
            font-size: 0.75rem;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
            display: block;
            margin-bottom: 8px;
        }

        /* BUTTONS */
        div.stButton > button {
            border-radius: 6px;
            font-weight: 500;
            border: 1px solid #eee;
            width: 100%;
        }

        /* --- MOBILE OPTIMIERUNG (Das ist der wichtige Teil!) --- */
        @media (max-width: 768px) {
            
            /* Zwingt Streamlit Spalten nebeneinander zu bleiben */
            [data-testid="column"] {
                width: 33.33% !important;
                flex: 1 1 33.33% !important;
                min-width: 0px !important; /* Das verhindert das Umbrechen! */
                padding: 0 2px !important; /* Ganz enge Abstände */
            }
            
            /* Karten kompakter machen */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 6px;
                min-height: 160px; /* Kleiner */
            }
            
            /* Bild flacher machen */
            .recipe-card-img {
                padding-top: 60% !important; 
            }
            
            /* Innenabstand reduzieren */
            div[data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(2) {
                padding: 6px !important;
            }

            /* Schriftarten verkleinern */
            .recipe-title {
                font-size: 11px !important;
                margin-bottom: 0px !important;
            }
            
            .recipe-cat {
                font-size: 8px !important;
                margin-bottom: 4px !important;
            }
            
            /* Buttons winzig machen */
            div.stButton > button {
                font-size: 9px !important;
                padding: 2px 4px !important;
                min-height: 0px !important;
                height: 24px !important;
                line-height: 1 !important;
            }
            
            /* Abstände zwischen den Buttons */
            div[data-testid="column"] > div > div > div {
                gap: 2px !important;
            }
            
            /* Toast Nachrichten oben fixieren, damit sie nicht stören */
            .stToast {
                top: 10px;
                right: 10px;
                width: 80%;
            }
        }
        </style>
    """, unsafe_allow_html=True)
