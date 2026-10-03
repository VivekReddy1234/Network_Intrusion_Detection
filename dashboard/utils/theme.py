import streamlit as st

# Color Tokens
PAGE_BG = "#0E1117"
CARD_BG = "#161B22"
BORDER = "#2A2F3A"
TEXT_PRIMARY = "#E6E6E6"
TEXT_MUTED = "#8B949E"

COLOR_NORMAL = "#2ECC71"     # Green
COLOR_SUSPICIOUS = "#F39C12" # Orange
COLOR_ATTACK = "#E74C3C"     # Red

# Determine severity color based on probability
def get_severity_color(probability: float) -> str:
    if probability < 0.4:
        return COLOR_NORMAL
    elif probability < 0.7:
        return COLOR_SUSPICIOUS
    return COLOR_ATTACK

# Plotly specific template mapping
PLOTLY_TEMPLATE = "plotly_dark"
PLOTLY_BG_COLOR = PAGE_BG
PLOTLY_PAPER_COLOR = PAGE_BG
PLOTLY_GRID_COLOR = "#2A2F3A"

def apply_custom_css():
    """Injects custom CSS to achieve the dark, professional security-ops aesthetic."""
    st.markdown(f"""
        <style>
        /* Base typography and background */
        .stApp {{
            background-color: {PAGE_BG};
            color: {TEXT_PRIMARY};
            font-family: -apple-system, Inter, "Segoe UI", sans-serif;
        }}
        
        /* Metric Cards */
        div[data-testid="stMetric"] {{
            background: linear-gradient(180deg, {CARD_BG} 0%, #1B212C 100%);
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 16px 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.35);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        div[data-testid="stMetric"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 24px rgba(0,0,0,0.45);
        }}
        
        div[data-testid="stMetricValue"] {{
            font-size: 28px !important;
            font-weight: 700;
        }}
        
        div[data-testid="stMetricLabel"] {{
            font-size: 12px;
            text-transform: uppercase;
            color: {TEXT_MUTED} !important;
        }}

        /* Table custom styles if using raw html, though Streamlit's dataframe handles it well with Pandas styler */
        </style>
    """, unsafe_allow_html=True)
