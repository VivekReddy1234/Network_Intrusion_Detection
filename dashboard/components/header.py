import streamlit as st
import datetime
from utils.formatting import format_number
from utils.theme import COLOR_NORMAL, COLOR_ATTACK, TEXT_MUTED

def render_header(total_packets: int, connection_ok: bool, last_updated: datetime.datetime):
    """Renders the top header with title and status cluster."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
            <h1 style="margin-bottom: 0px;">Network Intrusion Detection System</h1>
            <p style="color: {TEXT_MUTED}; font-size: 1.1em; margin-top: 5px;">Real-Time ML-Powered Traffic Monitoring</p>
        """, unsafe_allow_html=True)
        
    with col2:
        status_color = COLOR_NORMAL if connection_ok else COLOR_ATTACK
        status_text = "Monitoring Active" if connection_ok else "Connection Lost"
        
        # CSS for pulsing dot
        pulse_css = f"""
        <style>
        .blob {{
            background: {status_color};
            border-radius: 50%;
            margin: 10px;
            height: 12px;
            width: 12px;
            box-shadow: 0 0 0 0 rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 1);
            transform: scale(1);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 0.7);
            }}
            70% {{
                transform: scale(1);
                box-shadow: 0 0 0 6px rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 0);
            }}
            100% {{
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba({int(status_color[1:3], 16)}, {int(status_color[3:5], 16)}, {int(status_color[5:7], 16)}, 0);
            }}
        }}
        .status-container {{
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 15px;
            padding-top: 15px;
        }}
        .status-item {{
            text-align: right;
            font-size: 0.9em;
        }}
        </style>
        """
        
        st.markdown(pulse_css, unsafe_allow_html=True)
        
        time_str = last_updated.strftime("%H:%M:%S · %d %b %Y")
        
        st.markdown(f"""
            <div class="status-container">
                <div style="display: flex; align-items: center;">
                    <div class="blob"></div>
                    <span style="font-weight: 600;">{status_text}</span>
                </div>
                <div class="status-item">
                    <div style="color: {TEXT_MUTED}; font-size: 0.8em;">LAST UPDATED</div>
                    <div>{time_str}</div>
                </div>
                <div class="status-item">
                    <div style="color: {TEXT_MUTED}; font-size: 0.8em;">TOTAL PACKETS PROCESSED</div>
                    <div style="font-weight: bold;">{format_number(total_packets)}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 20px; border-color: #2A2F3A;'>", unsafe_allow_html=True)
