import streamlit as st
from utils.theme import TEXT_PRIMARY, TEXT_MUTED, COLOR_ATTACK

def render_empty_state():
    """Renders a centered empty state when no alerts match filters."""
    st.markdown(f"""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 48px; color: {TEXT_MUTED}; margin-bottom: 16px;">🛡️</div>
            <h2 style="color: {TEXT_PRIMARY}; font-weight: 600; margin: 0 0 8px 0;">No Alerts Detected</h2>
            <p style="color: {TEXT_MUTED}; margin: 0;">Waiting for network traffic...</p>
        </div>
    """, unsafe_allow_html=True)

def render_error_state(message: str):
    """Renders an error state, typically for DB connection issues."""
    st.markdown(f"""
        <div style="text-align: center; padding: 60px 20px; border: 1px solid {COLOR_ATTACK}; border-radius: 14px; background: rgba(231, 76, 60, 0.1);">
            <div style="font-size: 48px; margin-bottom: 16px;">⚠️</div>
            <h2 style="color: {TEXT_PRIMARY}; font-weight: 600; margin: 0 0 8px 0;">Connection Error</h2>
            <p style="color: {TEXT_MUTED}; margin: 0 0 16px 0;">{message}</p>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Retry Connection", use_container_width=True):
        st.rerun()
