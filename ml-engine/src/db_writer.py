import sqlite3
import os

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "shared",
            "alerts.db"
        )
    )
)
def init_db():
    con = sqlite3.connect(DB_PATH)
    con.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            src_ip    TEXT,
            dst_ip    TEXT,
            dst_port  INTEGER,
            protocol  TEXT,
            prob      REAL,
            label     TEXT
        )
    ''')
    con.commit()
    con.close()
    print('Database initialized.')

from datetime import datetime

def write_alert(src_ip, dst_ip, dst_port, protocol, prob, label='ATTACK'):
    con = sqlite3.connect(DB_PATH)
    con.execute(
        'INSERT INTO alerts VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)',
        (datetime.now().isoformat(), src_ip, dst_ip, dst_port, protocol, prob, label)
    )
    con.commit()
    con.close()

import pandas as pd

def read_alerts(limit=500):
    con = sqlite3.connect(DB_PATH)
    df = pd.read_sql(
        f'SELECT * FROM alerts ORDER BY timestamp DESC LIMIT {limit}',
        con
    )
    con.close()
    return df 