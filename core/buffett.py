from typing import List, Optional

import pandas as pd

from core.fred import fetch_buffett_indicator
from core.indicators import fetch_stock

# Valuation zones based on common interpretations of the Buffett Indicator.
# Buffett himself flagged ~200% as a strong sell signal in his 2001 Fortune article.
ZONES = {
    "Undervalued":     (0,   100),
    "Fair Value":      (100, 150),
    "Overvalued":      (150, 200),
    "Extreme":         (200, float("inf")),
}

# Quarter counts for forward-return windows
FORWARD_QUARTERS = {
    "1Y":  4,
    "2Y":  8,
    "3Y":  12,
    "5Y":  20,
}


def fetch_combined(start: str = "2000-01-01", end: Optional[str] = None) -> pd.DataFrame:
    """
    Merge the Buffett Indicator (quarterly) with S&P 500 (resampled to quarter-end).
    Uses ^GSPC from yfinance for S&P 500 — FRED's SP500 series only starts in 2016.
    Returns a DataFrame indexed by quarter with columns:
      market_cap_trn, gdp_trn, buffett_indicator, sp500.
    """
    buffett_df = fetch_buffett_indicator(start, end)
    sp500_df = fetch_stock("^GSPC", start=start, end=end)

    # Resample S&P 500 to match quarterly Buffett cadence
    sp500_quarterly = sp500_df["Close"].resample("QE").last()

    df = buffett_df.copy()
    df["sp500"] = sp500_quarterly.reindex(df.index, method="ffill")
    return df.dropna()


def _add_forward_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add forward S&P 500 return columns for each window in FORWARD_QUARTERS."""
    result = df.copy()
    for label, quarters in FORWARD_QUARTERS.items():
        # pct_change(n) gives return over next n periods; shift(-n) aligns it to today
        result[f"fwd_{label}"] = result["sp500"].pct_change(quarters).shift(-quarters) * 100
    return result


def zone_label(value: float) -> str:
    for name, (low, high) in ZONES.items():
        if low <= value < high:
            return name
    return "Extreme"


def historical_context(start: str = "2000-01-01", end: Optional[str] = None) -> pd.DataFrame:
    """
    Full dataset: Buffett Indicator + S&P 500 + valuation zone + forward returns.
    This is the primary DataFrame consumed by the UI for charting and analysis.
    """
    df = fetch_combined(start, end)
    df = _add_forward_returns(df)
    df["zone"] = df["buffett_indicator"].apply(zone_label)
    return df


def zone_summary(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Average forward S&P 500 returns grouped by valuation zone.
    Answers: 'When the Buffett Indicator was Extreme, the market returned X% on average over 1Y.'

    Accepts a pre-built DataFrame (e.g. already filtered by date) or fetches fresh data.
    """
    if df is None:
        df = historical_context()

    fwd_cols = [c for c in df.columns if c.startswith("fwd_")]
    summary = df.groupby("zone")[fwd_cols].agg(["mean", "count"]).round(1)

    # Flatten MultiIndex columns for readability: (fwd_1Y, mean) → fwd_1Y_mean
    summary.columns = ["_".join(col) for col in summary.columns]

    # Reorder zones from least to most extreme
    zone_order = list(ZONES.keys())
    return summary.reindex([z for z in zone_order if z in summary.index])


def current_level(df: Optional[pd.DataFrame] = None) -> dict:
    """
    Return the most recent Buffett Indicator reading with its zone label.
    Useful for a dashboard summary card.
    """
    if df is None:
        df = historical_context()

    latest = df.iloc[-1]
    return {
        "date": f"{latest.name.year}-Q{(latest.name.month - 1) // 3 + 1}",
        "buffett_indicator": round(latest["buffett_indicator"], 1),
        "market_cap_trn": round(latest["market_cap_trn"], 1),
        "gdp_trn": round(latest["gdp_trn"], 1),
        "sp500": round(latest["sp500"], 1),
        "zone": latest["zone"],
    }
