"""Dashboard Utilities"""
import requests
import pandas as pd
from typing import Dict, Optional

API_URL = "http://localhost:8000"

def call_api(endpoint: str, payload: dict, method: str = "POST") -> dict:
    """Call Meridian API"""
    url = f"{API_URL}/api/v2/{endpoint}"
    try:
        if method == "POST":
            res = requests.post(url, json=payload, timeout=30)
        else:
            res = requests.get(url, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return {"error": str(e), "status": "failed"}

def to_series(timestamps, prices) -> pd.Series:
    """Convert lists to pandas Series"""
    return pd.Series(prices, index=pd.to_datetime(timestamps))

def load_csv_data(uploaded_file) -> Optional[pd.DataFrame]:
    """Load CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        return None

