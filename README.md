# fred_prophet

A financial analysis tool that combines Federal Reserve (FRED) macroeconomic data with market indicators to provide historical context and visual exploration of market conditions.

## Vision

fred_prophet aims to answer questions like:
- *What happened to the market the last time the Buffett Indicator was this high?*
- *How does the Fed funds rate correlate with S&P 500 performance over time?*
- *What do technical indicators say about a stock across different historical periods?*

## Planned Features

### 1. FRED Data Integration
- Pull macroeconomic data from the [Federal Reserve Economic Data (FRED) API](https://fred.stlouisfed.org/)
- Key series: GDP, Fed funds rate, CPI (inflation), M2 money supply, unemployment
- Serve as the macroeconomic backbone for market context analysis

### 2. Technical Indicators
Compute standard technical indicators on stock price data:
- **Trend**: Simple Moving Average (SMA), Exponential Moving Average (EMA)
- **Momentum**: MACD (Moving Average Convergence Divergence), RSI
- **Volatility**: Bollinger Bands
- Overlayable on price charts with configurable parameters (e.g. SMA 50 vs SMA 200)

### 3. Buffett Indicator Analysis
- Calculate the **Buffett Indicator**: Total US Market Cap / GDP
- Overlay against S&P 500 historical performance
- Highlight periods where the indicator was elevated and annotate what followed
- Goal: understand historical precedents for current market valuations

### 4. Interactive UI
- Web-based dashboard for visual exploration
- Compare multiple stocks and indicators on the same chart
- Draggable / zoomable timeline for historical navigation
- Overlay macroeconomic events (e.g. rate hikes, recessions) on price charts

## Roadmap

- [ ] Set up FRED API client and data pipeline
- [ ] Implement technical indicator calculations
- [ ] Build Buffett Indicator vs S&P 500 comparison view
- [ ] Design and build interactive web UI
- [ ] Add multi-stock comparison support
- [ ] Add timeline scrubbing / historical playback

## Data Sources

| Source | Data | Access |
|---|---|---|
| [FRED API](https://fred.stlouisfed.org/docs/api/fred/) | Macroeconomic data (GDP, rates, inflation) | Free API key |
| [Yahoo Finance](https://finance.yahoo.com/) / other | Stock price history | TBD |
| [Wilshire 5000](https://fred.stlouisfed.org/series/WILL5000PR) | Total US Market Cap (via FRED) | Free API key |

## License

Apache License 2.0 — see [LICENSE](./LICENSE) for details.
