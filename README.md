# fred_prophet

A financial analysis tool that combines Federal Reserve (FRED) macroeconomic data with market indicators to provide historical context and visual exploration of market conditions.

## Vision

fred_prophet aims to answer questions like:
- *What happened to the market the last time the Buffett Indicator was this high?*
- *How does the Fed funds rate correlate with S&P 500 performance over time?*
- *What do technical indicators say about a stock across different historical periods?*

## Features

### 1. FRED Data Integration ✅
- FRED API client in `core/fred.py` pulling key macroeconomic series
- GDP, Fed funds rate, CPI, M2 money supply via the [FRED API](https://fred.stlouisfed.org/)
- Total US equity market cap via Federal Reserve Z.1 Financial Accounts (`BOGZ1FL893064105Q`)

### 2. Technical Indicators ✅
Computed in `core/indicators.py` on any stock ticker via yfinance:
- **Trend**: SMA (50, 200), EMA (12, 26)
- **Momentum**: MACD with signal line and histogram, RSI (Wilder's smoothing)
- **Volatility**: Bollinger Bands (SMA 20 ± 2σ)

### 3. Buffett Indicator Analysis ✅
- Buffett Indicator (Total Market Cap / GDP) calculated in `core/buffett.py`
- Overlaid against S&P 500 (via `^GSPC` from yfinance, history back to 2000)
- Valuation zones: Undervalued / Fair Value / Overvalued / Extreme
- Historical forward return table: average S&P 500 returns 1Y/2Y/3Y/5Y after each zone

### 4. Interactive UI ✅
Streamlit dashboard in `ui/app.py` with two tabs:
- **Buffett Indicator tab**: date range picker, summary metrics, interactive chart with zone shading, forward returns table
- **Technical Indicators tab**: any ticker, toggleable SMA/EMA/Bollinger Bands overlays, 3-panel chart (price → MACD → RSI) with shared x-axis zoom

## Roadmap

- [x] Set up FRED API client and data pipeline
- [x] Implement technical indicator calculations
- [x] Build Buffett Indicator vs S&P 500 comparison view
- [x] Design and build interactive Streamlit UI
- [ ] Add disk cache layer (Parquet) to avoid re-fetching on every restart
- [ ] Add multi-stock comparison support
- [ ] Add timeline scrubbing / historical playback
- [ ] Migrate UI to FastAPI + React when Streamlit hits its limits

## Architecture

```
fred_prophet/
├── core/                  # Pure Python — no Streamlit imports
│   ├── fred.py            # FRED API client and macro series
│   ├── indicators.py      # SMA, EMA, MACD, RSI, Bollinger Bands + yfinance fetch
│   └── buffett.py         # Buffett Indicator vs S&P 500 analysis
└── ui/
    └── app.py             # Streamlit UI — calls core/ only
```

`core/` is kept Streamlit-free intentionally — when the UI migrates to FastAPI + React, only `ui/` needs replacing.

## Running

```bash
./start.sh    # start the app — opens at http://localhost:8501
./stop.sh     # stop the app
```

Requires a `.env` file with your [FRED API key](https://fred.stlouisfed.org/docs/api/api_key.html):
```
FRED_API_KEY=your_key_here
```

## Data Sources

| Source | Data | Series |
|---|---|---|
| [FRED API](https://fred.stlouisfed.org/docs/api/fred/) | GDP, Fed funds rate, CPI, M2, market cap | `GDP`, `FEDFUNDS`, `CPIAUCSL`, `M2SL`, `BOGZ1FL893064105Q` |
| [Yahoo Finance](https://finance.yahoo.com/) via yfinance | Stock price history, S&P 500 | Any ticker, `^GSPC` |

## License

Apache License 2.0 — see [LICENSE](./LICENSE) for details.
