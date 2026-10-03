import pandas as pd

def format_number(num: int) -> str:
    """Format large numbers with thousands separators."""
    if pd.isna(num):
        return "0"
    return f"{int(num):,}"

def format_percentage(val: float) -> str:
    """Format a float as a percentage with 1 decimal place."""
    if pd.isna(val):
        return "0.0%"
    return f"{val * 100:.1f}%"
