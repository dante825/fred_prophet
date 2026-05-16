from typing import List, Optional

import pandas as pd
import yfinance as yf


def fetch_stock(
    ticker: str,
    start: str = "2000-01-01",
    end: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fetch OHLCV data for a ticker via yfinance.
    auto_adjust=True applies split and dividend adjustments so historical
    prices are comparable across the full date range.
    """
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)

    # yfinance 1.x returns a MultiIndex (price_type, ticker) — flatten to just price_type
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index = pd.to_datetime(df.index)
    return df


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def macd(
    series: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """
    Returns a DataFrame with columns: macd, signal, histogram.
    Standard defaults: fast=12, slow=26, signal=9.
    """
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({
        "macd": macd_line,
        "signal": signal_line,
        "histogram": macd_line - signal_line,
    })


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    """
    Wilder's RSI. Uses EMA with com=window-1 (equivalent to Wilder's smoothing),
    which is the industry-standard method used by Bloomberg, TradingView, etc.
    """
    delta = series.diff()
    avg_gain = delta.clip(lower=0).ewm(com=window - 1, adjust=False).mean()
    avg_loss = (-delta.clip(upper=0)).ewm(com=window - 1, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def bollinger_bands(
    series: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> pd.DataFrame:
    """Returns a DataFrame with columns: upper, mid, lower."""
    mid = sma(series, window)
    std = series.rolling(window=window).std()
    return pd.DataFrame({
        "upper": mid + num_std * std,
        "mid": mid,
        "lower": mid - num_std * std,
    })


def add_indicators(
    df: pd.DataFrame,
    sma_windows: List[int] = [50, 200],
    ema_windows: List[int] = [12, 26],
    rsi_window: int = 14,
    bb_window: int = 20,
) -> pd.DataFrame:
    """
    Add all indicators to a stock OHLCV DataFrame (as returned by fetch_stock).
    All indicator columns are added in-place on a copy; original columns are preserved.
    """
    result = df.copy()
    close = result["Close"]

    for w in sma_windows:
        result[f"SMA_{w}"] = sma(close, w)

    for w in ema_windows:
        result[f"EMA_{w}"] = ema(close, w)

    macd_df = macd(close)
    result["MACD"] = macd_df["macd"]
    result["MACD_signal"] = macd_df["signal"]
    result["MACD_hist"] = macd_df["histogram"]

    result["RSI"] = rsi(close, rsi_window)

    bb = bollinger_bands(close, bb_window)
    result["BB_upper"] = bb["upper"]
    result["BB_mid"] = bb["mid"]
    result["BB_lower"] = bb["lower"]

    return result
