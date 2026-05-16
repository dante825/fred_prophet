import os
from functools import lru_cache
from typing import Optional

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()

# FRED series IDs used in this project
SERIES = {
    # Fed Z.1 Financial Accounts: all US equity (domestic + foreign held), millions of USD, quarterly
    "market_cap": "BOGZ1FL893064105Q",
    "gdp": "GDP",          # US Nominal GDP, billions of USD, quarterly (annualised rate)
    "sp500": "SP500",      # S&P 500 index, daily
    "fed_funds": "FEDFUNDS",  # Federal funds rate, monthly
    "cpi": "CPIAUCSL",    # CPI, monthly
    "m2": "M2SL",         # M2 money supply, monthly
}


def _client() -> Fred:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError("FRED_API_KEY not set. Copy .env.example to .env and add your key.")
    return Fred(api_key=api_key)


@lru_cache(maxsize=32)
def fetch_series(series_id: str, start: str = "2000-01-01", end: Optional[str] = None) -> pd.Series:
    """Fetch a single FRED series as a pandas Series indexed by date."""
    client = _client()
    return client.get_series(series_id, observation_start=start, observation_end=end)


def fetch_buffett_indicator(start: str = "2000-01-01", end: Optional[str] = None) -> pd.DataFrame:
    """
    Buffett Indicator = Total Market Cap / GDP, expressed as a percentage.
    Both series are quarterly. Market cap (BOGZ1FL893064105Q) is in millions of USD;
    GDP is in billions of USD at annualised rate — divide market cap by 1000 to align units.
    Returns a DataFrame with columns: market_cap_trn, gdp_trn, buffett_indicator.
    """
    market_cap = fetch_series(SERIES["market_cap"], start, end)
    gdp = fetch_series(SERIES["gdp"], start, end)

    df = pd.DataFrame({
        "market_cap_trn": market_cap / 1_000_000,  # millions → trillions
        "gdp_trn": gdp / 1_000,                    # billions → trillions
    }).dropna()
    df["buffett_indicator"] = df["market_cap_trn"] / df["gdp_trn"] * 100
    return df


def fetch_sp500(start: str = "2000-01-01", end: Optional[str] = None) -> pd.Series:
    return fetch_series(SERIES["sp500"], start, end)


def fetch_macro_overview(start: str = "2000-01-01", end: Optional[str] = None) -> pd.DataFrame:
    """Fetch all macro series and return as a single aligned DataFrame."""
    series_data = {
        name: fetch_series(sid, start, end)
        for name, sid in SERIES.items()
    }
    return pd.DataFrame(series_data)
