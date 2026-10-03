import streamlit as st
import datetime

# Must be the very first Streamlit command
st.set_page_config(
    page_title="NIDS Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.theme import apply_custom_css
from services import db, data_service
from components import header, sidebar, kpi_cards, alerts_table, charts, empty_state

# Apply CSS theme
apply_custom_css()

# We check connection and get available options once at the top level
db_ok = db.check_connection()

if not db_ok:
    header.render_header(0, False, datetime.datetime.now())
    empty_state.render_error_state("Could not connect to the alerts database. Please ensure ml-engine is writing to shared/alerts.db.")
    st.stop()

available_filter_options = data_service.get_filter_options()
filters = sidebar.render_sidebar(available_filter_options)

refresh_interval = filters.get("refresh_interval", 5)

# Use st.fragment for partial refresh without whole page reload
# Note: st.fragment(run_every=...) is available in Streamlit >= 1.37
run_every_arg = f"{refresh_interval}s" if refresh_interval > 0 else None

@st.fragment(run_every=run_every_arg)
def render_dashboard_fragment(current_filters):
    # 1. Load Data
    total_packets = data_service.get_total_alerts_count()
    last_updated = datetime.datetime.now()
    kpis = data_service.compute_kpis(current_filters)
    df_alerts = data_service.load_alerts(current_filters)
    
    # 2. Render Header
    header.render_header(total_packets, True, last_updated)
    
    # 3. Check for empty state
    if kpis.get("total_alerts", 0) == 0:
        empty_state.render_empty_state()
        return

    # 4. Render KPIs
    kpi_cards.render_kpis(kpis)
    
    # 5. Render Table
    alerts_table.render_table(df_alerts)
    
    st.markdown("<br><hr style='border-color: #2A2F3A;'><br>", unsafe_allow_html=True)
    
    # 6. Render Charts
    charts.render_charts(current_filters)

# Call the fragment
render_dashboard_fragment(filters)
