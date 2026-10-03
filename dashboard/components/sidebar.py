import streamlit as st
import datetime
from utils.config import DEFAULT_PROBABILITY_MIN, REFRESH_OPTIONS

def render_sidebar(available_options: dict) -> dict:
    """Renders the sidebar filters and returns the current filter state."""
    st.sidebar.header("Filters")
    
    # Session state for reset functionality
    if "reset_trigger" not in st.session_state:
        st.session_state.reset_trigger = False
        
    def reset_filters():
        st.session_state.reset_trigger = not st.session_state.reset_trigger
        
    # We use forms or individual widgets, but auto-applying requires individual widgets.
    # To handle reset, we use a key for each widget that changes on reset, or manage via session_state.
    reset_key = str(st.session_state.reset_trigger)
    
    protocols = st.sidebar.multiselect(
        "Protocol",
        options=available_options.get("protocols", []),
        default=[],
        key=f"prot_{reset_key}"
    )
    
    # Dest Port could be many, using text input for simplicity or number input
    dest_port_input = st.sidebar.text_input(
        "Destination Port", 
        value="All", 
        help="Enter a port number or 'All'",
        key=f"port_{reset_key}"
    )
    dest_port = None
    if dest_port_input.strip().lower() != "all":
        try:
            dest_port = int(dest_port_input.strip())
        except ValueError:
            dest_port = "All"
            
    min_prob = st.sidebar.slider(
        "Minimum Probability",
        min_value=0.0,
        max_value=1.0,
        value=DEFAULT_PROBABILITY_MIN,
        step=0.01,
        key=f"prob_{reset_key}"
    )
    
    labels = st.sidebar.multiselect(
        "Label",
        options=available_options.get("labels", []),
        default=[],
        key=f"label_{reset_key}"
    )
    
    # Date Range - Default to last 24 hours
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(yesterday, today),
        max_value=today,
        key=f"date_{reset_key}"
    )
    
    st.sidebar.markdown("---")
    
    refresh_interval_label = st.sidebar.selectbox(
        "Refresh Interval",
        options=list(REFRESH_OPTIONS.keys()),
        index=0, # Default 5s
        key=f"refresh_{reset_key}"
    )
    refresh_interval = REFRESH_OPTIONS[refresh_interval_label]
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("Refresh Now", use_container_width=True):
            st.rerun()
    with col2:
        st.button("Reset Filters", on_click=reset_filters, use_container_width=True)
        
    return {
        "protocols": protocols,
        "dest_port": dest_port if dest_port != "All" else None,
        "min_probability": min_prob,
        "labels": labels,
        "date_range": date_range,
        "refresh_interval": refresh_interval
    }
