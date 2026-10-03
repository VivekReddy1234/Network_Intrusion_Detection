import streamlit as st
import pandas as pd
from utils.theme import COLOR_NORMAL, COLOR_SUSPICIOUS, COLOR_ATTACK
from utils.formatting import format_percentage

def render_table(df: pd.DataFrame):
    """Renders the paginated, color-coded alerts table."""
    
    if df.empty:
        return
        
    st.markdown(f"### Recent Alerts (Showing latest {len(df)})")
    
    # We use st.column_config to show a progress bar for probability
    
    st.dataframe(
        df,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
            "source_ip": st.column_config.TextColumn("Source IP"),
            "destination_ip": st.column_config.TextColumn("Destination IP"),
            "destination_port": st.column_config.NumberColumn("Destination Port", format="%d"),
            "protocol": st.column_config.TextColumn("Protocol"),
            "probability": st.column_config.ProgressColumn(
                "Probability",
                help="ML attack probability",
                format="%.2f",
                min_value=0.0,
                max_value=1.0,
            ),
            "label": st.column_config.TextColumn("Label")
        },
        use_container_width=True,
        hide_index=True,
        height=400 # Fixed height to make it scrollable
    )
