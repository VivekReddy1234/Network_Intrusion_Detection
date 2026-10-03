import os
from pathlib import Path
from dotenv import load_dotenv

# Resolve project root and load .env
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

# DB Path configuration
DB_PATH = PROJECT_ROOT / "shared" / "alerts.db"

# Thresholds
SEVERITY_THRESHOLD_LOW = 0.4
SEVERITY_THRESHOLD_HIGH = 0.7

# Default filter values
DEFAULT_PROBABILITY_MIN = 0.0
DEFAULT_REFRESH_INTERVAL = 5 # seconds

REFRESH_OPTIONS = {
    "5s": 5,
    "10s": 10,
    "30s": 30,
    "60s": 60,
    "Off": 0
}
