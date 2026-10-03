import streamlit as st
from typing import Dict, Any
from utils.formatting import format_number, format_percentage

def render_kpis(kpis: Dict[str, Any]):
    """Renders the 6 metric cards in a responsive grid."""
    
    # We use Streamlit's native metric component since we have styled it via CSS in theme.py
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Alerts", format_number(kpis.get("total_alerts", 0)))
        st.metric("Maximum Probability", format_percentage(kpis.get("max_prob", 0.0)))
        
    with col2:
        st.metric("High Severity Alerts", format_number(kpis.get("high_severity", 0)))
        st.metric("Unique Source IPs", format_number(kpis.get("unique_src", 0)))
        
    with col3:
        st.metric("Avg Attack Probability", format_percentage(kpis.get("avg_prob", 0.0)))
        st.metric("Unique Destination Ports", format_number(kpis.get("unique_ports", 0)))
    
    st.markdown("<br>", unsafe_allow_html=True)
