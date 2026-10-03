import pandas as pd
from typing import Dict, Any, List, Tuple
from services.db import execute_query
from utils.config import SEVERITY_THRESHOLD_HIGH

def get_filter_options() -> Dict[str, List[Any]]:
    """Fetch unique values for filters (protocols, labels) from the DB."""
    try:
        df_prot = execute_query("SELECT DISTINCT protocol FROM alerts WHERE protocol IS NOT NULL")
        df_label = execute_query("SELECT DISTINCT label FROM alerts WHERE label IS NOT NULL")
        
        return {
            "protocols": df_prot['protocol'].tolist() if not df_prot.empty else [],
            "labels": df_label['label'].tolist() if not df_label.empty else []
        }
    except Exception:
        return {"protocols": [], "labels": []}

def build_where_clause(filters: Dict[str, Any]) -> Tuple[str, list]:
    """Constructs the WHERE clause and params based on active filters."""
    conditions = []
    params = []
    
    # Protocol filter
    if filters.get("protocols"):
        placeholders = ",".join("?" for _ in filters["protocols"])
        conditions.append(f"protocol IN ({placeholders})")
        params.extend(filters["protocols"])
        
    # Dest Port filter
    if filters.get("dest_port") and filters["dest_port"] != "All":
        conditions.append("dst_port = ?")
        params.append(filters["dest_port"])
        
    # Min Probability filter
    if filters.get("min_probability", 0.0) > 0.0:
        conditions.append("prob >= ?")
        params.append(filters["min_probability"])
        
    # Label filter
    if filters.get("labels"):
        placeholders = ",".join("?" for _ in filters["labels"])
        conditions.append(f"label IN ({placeholders})")
        params.extend(filters["labels"])
        
    # Date Range filter
    if filters.get("date_range") and len(filters["date_range"]) == 2:
        start_date, end_date = filters["date_range"]
        conditions.append("REPLACE(timestamp, 'T', ' ') >= ? AND REPLACE(timestamp, 'T', ' ') <= ?")
        params.extend([f"{start_date} 00:00:00", f"{end_date} 23:59:59"])
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return where_clause, params

def get_total_alerts_count() -> int:
    """Gets the absolute total row count from the alerts table."""
    try:
        df = execute_query("SELECT COUNT(*) as cnt FROM alerts")
        return int(df['cnt'].iloc[0]) if not df.empty else 0
    except Exception:
        return 0

def load_alerts(filters: Dict[str, Any], limit: int = 200) -> pd.DataFrame:
    """Load latest alerts based on filters."""
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT timestamp, src_ip AS source_ip, dst_ip AS destination_ip, dst_port AS destination_port, protocol, prob AS probability, label
        FROM alerts
        {where_clause}
        ORDER BY timestamp DESC
        LIMIT ?
    """
    params.append(limit)
    return execute_query(query, tuple(params))

def compute_kpis(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Compute KPI metrics based on current filters."""
    where_clause, params = build_where_clause(filters)
    
    query = f"""
        SELECT 
            COUNT(*) as total_alerts,
            SUM(CASE WHEN prob >= {SEVERITY_THRESHOLD_HIGH} THEN 1 ELSE 0 END) as high_severity,
            AVG(prob) as avg_prob,
            MAX(prob) as max_prob,
            COUNT(DISTINCT src_ip) as unique_src,
            COUNT(DISTINCT dst_port) as unique_ports
        FROM alerts
        {where_clause}
    """
    df = execute_query(query, tuple(params))
    
    if df.empty or pd.isna(df['total_alerts'].iloc[0]):
        return {
            "total_alerts": 0, "high_severity": 0, "avg_prob": 0.0,
            "max_prob": 0.0, "unique_src": 0, "unique_ports": 0
        }
        
    row = df.iloc[0]
    return {
        "total_alerts": int(row['total_alerts'] or 0),
        "high_severity": int(row['high_severity'] or 0),
        "avg_prob": float(row['avg_prob'] or 0.0),
        "max_prob": float(row['max_prob'] or 0.0),
        "unique_src": int(row['unique_src'] or 0),
        "unique_ports": int(row['unique_ports'] or 0)
    }

def get_chart_data_timeline(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT 
            strftime('%Y-%m-%d %H:00:00', timestamp) as time_bucket,
            COUNT(*) as alert_count,
            AVG(prob) as avg_probability
        FROM alerts
        {where_clause}
        GROUP BY time_bucket
        ORDER BY time_bucket ASC
    """
    return execute_query(query, tuple(params))

def get_chart_data_protocol(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT protocol, COUNT(*) as count
        FROM alerts
        {where_clause}
        GROUP BY protocol
        ORDER BY count DESC
    """
    return execute_query(query, tuple(params))

def get_chart_data_port(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT CAST(dst_port AS TEXT) as port, COUNT(*) as count
        FROM alerts
        {where_clause}
        GROUP BY dst_port
        ORDER BY count DESC
        LIMIT 15
    """
    return execute_query(query, tuple(params))

def get_chart_data_probability_dist(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT prob as probability
        FROM alerts
        {where_clause}
    """
    return execute_query(query, tuple(params))

def get_chart_data_src_ip(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT src_ip as source_ip, COUNT(*) as count
        FROM alerts
        {where_clause}
        GROUP BY src_ip
        ORDER BY count DESC
        LIMIT 10
    """
    return execute_query(query, tuple(params))
    
def get_chart_data_dest_ip(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT dst_ip as destination_ip, COUNT(*) as count
        FROM alerts
        {where_clause}
        GROUP BY dst_ip
        ORDER BY count DESC
        LIMIT 10
    """
    return execute_query(query, tuple(params))

def get_chart_data_labels(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT label, COUNT(*) as count
        FROM alerts
        {where_clause}
        GROUP BY label
        ORDER BY count DESC
    """
    return execute_query(query, tuple(params))

def get_chart_data_heatmap(filters: Dict[str, Any]) -> pd.DataFrame:
    where_clause, params = build_where_clause(filters)
    query = f"""
        SELECT 
            CAST(strftime('%H', timestamp) AS INTEGER) as hour_of_day,
            CAST(strftime('%w', timestamp) AS INTEGER) as day_of_week,
            COUNT(*) as count
        FROM alerts
        {where_clause}
        GROUP BY hour_of_day, day_of_week
    """
    return execute_query(query, tuple(params))

