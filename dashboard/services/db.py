import sqlite3
import pandas as pd
from contextlib import contextmanager
from utils.config import DB_PATH

@contextmanager
def get_ro_connection():
    """Yields a read-only SQLite connection to the alerts database."""
    # URI mode requires the path to be formatted as a URI.
    # Windows paths need careful handling.
    db_uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    
    conn = None
    try:
        conn = sqlite3.connect(db_uri, uri=True, check_same_thread=False)
        yield conn
    except sqlite3.Error as e:
        # We will catch this in the UI to display the error state
        raise Exception(f"Database connection failed: {e}")
    finally:
        if conn:
            conn.close()

def execute_query(query: str, params: tuple = ()) -> pd.DataFrame:
    """Executes a query and returns a pandas DataFrame."""
    with get_ro_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)

def check_connection() -> bool:
    """Check if we can successfully connect to the database."""
    try:
        with get_ro_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception:
        return False
