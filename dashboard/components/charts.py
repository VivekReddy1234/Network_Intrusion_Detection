import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any
from utils.theme import PLOTLY_TEMPLATE, PLOTLY_BG_COLOR, PLOTLY_PAPER_COLOR, PLOTLY_GRID_COLOR, COLOR_NORMAL, COLOR_SUSPICIOUS, COLOR_ATTACK
from services import data_service

def apply_common_layout(fig, title=""):
    """Applies common dark theme layout to Plotly figures."""
    fig.update_layout(
        title=title,
        template=PLOTLY_TEMPLATE,
        plot_bgcolor=PLOTLY_BG_COLOR,
        paper_bgcolor=PLOTLY_PAPER_COLOR,
        font=dict(color="#E6E6E6", family="-apple-system, Inter, sans-serif"),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor=PLOTLY_GRID_COLOR, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor=PLOTLY_GRID_COLOR, zeroline=False),
        hovermode="closest",
    )
    return fig

def render_charts(filters: Dict[str, Any]):
    """Renders all 8 Plotly charts in a responsive grid."""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 1. Attack Timeline
        df_timeline = data_service.get_chart_data_timeline(filters)
        if not df_timeline.empty:
            fig_tl = px.line(df_timeline, x="time_bucket", y="alert_count", 
                             color_discrete_sequence=[COLOR_ATTACK])
            fig_tl = apply_common_layout(fig_tl, "Attack Timeline (Alerts / Hr)")
            fig_tl.update_traces(fill='tozeroy', fillcolor=f"rgba(231, 76, 60, 0.1)")
            st.plotly_chart(fig_tl, use_container_width=True, config={'displayModeBar': False})
        
        # 3. Destination Port Distribution
        df_ports = data_service.get_chart_data_port(filters)
        if not df_ports.empty:
            # Sort ascending for horizontal bar chart so highest is at top
            df_ports = df_ports.sort_values(by="count", ascending=True)
            fig_ports = px.bar(df_ports, x="count", y="port", orientation='h',
                               color_discrete_sequence=[COLOR_SUSPICIOUS])
            fig_ports = apply_common_layout(fig_ports, "Top Destination Ports")
            st.plotly_chart(fig_ports, use_container_width=True, config={'displayModeBar': False})
            
        # 5. Top Source IPs
        df_src_ip = data_service.get_chart_data_src_ip(filters)
        if not df_src_ip.empty:
            df_src_ip = df_src_ip.sort_values(by="count", ascending=True)
            fig_src = px.bar(df_src_ip, x="count", y="source_ip", orientation='h',
                             color_discrete_sequence=[COLOR_ATTACK])
            fig_src = apply_common_layout(fig_src, "Top Source IPs")
            st.plotly_chart(fig_src, use_container_width=True, config={'displayModeBar': False})
            
        # 7. Attack Labels
        df_labels = data_service.get_chart_data_labels(filters)
        if not df_labels.empty:
            # Use a pie chart
            fig_labels = px.pie(df_labels, values="count", names="label", hole=0.4,
                                color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_labels = apply_common_layout(fig_labels, "Attack Labels Distribution")
            fig_labels.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_labels, use_container_width=True, config={'displayModeBar': False})

    with col2:
        # 2. Protocol Distribution
        df_proto = data_service.get_chart_data_protocol(filters)
        if not df_proto.empty:
            fig_proto = px.pie(df_proto, values="count", names="protocol", hole=0.5,
                               color_discrete_sequence=[COLOR_NORMAL, COLOR_SUSPICIOUS, COLOR_ATTACK, "#9B59B6"])
            fig_proto = apply_common_layout(fig_proto, "Protocol Distribution")
            st.plotly_chart(fig_proto, use_container_width=True, config={'displayModeBar': False})
            
        # 4. Attack Probability Distribution
        df_prob = data_service.get_chart_data_probability_dist(filters)
        if not df_prob.empty:
            # Histogram, color mapping isn't as straightforward with px.histogram for value-based coloring in a single series,
            # so we just use the attack color for the whole dist.
            fig_prob = px.histogram(df_prob, x="probability", nbins=20, 
                                    color_discrete_sequence=[COLOR_ATTACK])
            fig_prob = apply_common_layout(fig_prob, "Probability Distribution")
            st.plotly_chart(fig_prob, use_container_width=True, config={'displayModeBar': False})
            
        # 6. Top Destination IPs
        df_dest_ip = data_service.get_chart_data_dest_ip(filters)
        if not df_dest_ip.empty:
            df_dest_ip = df_dest_ip.sort_values(by="count", ascending=True)
            fig_dest = px.bar(df_dest_ip, x="count", y="destination_ip", orientation='h',
                              color_discrete_sequence=[COLOR_SUSPICIOUS])
            fig_dest = apply_common_layout(fig_dest, "Top Destination IPs")
            st.plotly_chart(fig_dest, use_container_width=True, config={'displayModeBar': False})
            
        # 8. Hourly Activity Heatmap
        df_heatmap = data_service.get_chart_data_heatmap(filters)
        if not df_heatmap.empty:
            # Pivot the dataframe to get hours on X and days on Y
            df_pivot = df_heatmap.pivot(index="day_of_week", columns="hour_of_day", values="count").fillna(0)
            
            # Map day_of_week integers to names (0=Sun, 6=Sat)
            day_map = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
            df_pivot.index = df_pivot.index.map(day_map)
            
            # Ensure all hours 0-23 are present
            for h in range(24):
                if h not in df_pivot.columns:
                    df_pivot[h] = 0
            df_pivot = df_pivot[sorted(df_pivot.columns)]
            
            fig_heat = px.imshow(
                df_pivot, 
                labels=dict(x="Hour of Day", y="Day of Week", color="Alerts"),
                x=[str(i) for i in range(24)],
                color_continuous_scale=[(0, PLOTLY_BG_COLOR), (0.5, COLOR_SUSPICIOUS), (1, COLOR_ATTACK)]
            )
            fig_heat = apply_common_layout(fig_heat, "Hourly Activity Heatmap")
            st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
