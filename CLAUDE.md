# fred_prophet — Claude Instructions

## Tech Stack Decision

**Current**: Streamlit (chosen to iterate quickly on data pipeline and indicator logic)
**Future**: FastAPI (backend) + React (frontend) — migrate when UI requirements outgrow Streamlit

## Architecture Rule: Keep `core/` Sacred

Business logic must live in `core/` as plain Python with **zero Streamlit imports**.
The `ui/` layer calls `core/` — never the other way around.

```
fred_prophet/
├── core/
│   ├── fred.py          # FRED API client and data fetching
│   ├── indicators.py    # SMA, EMA, MACD, RSI, Bollinger Bands
│   └── buffett.py       # Buffett Indicator vs S&P 500 logic
└── ui/
    └── app.py           # Streamlit UI — calls core/, no business logic here
```

**Why this matters**: when we migrate to FastAPI + React, `core/` becomes the FastAPI route handlers with zero changes. Only `ui/` gets replaced.

## Project Goals (for context)

1. Pull macroeconomic data from the FRED API (St. Louis Fed)
2. Calculate technical indicators: SMA, EMA, MACD, RSI, Bollinger Bands
3. Compare the Buffett Indicator (Market Cap / GDP) against S&P 500 historical performance
4. Interactive UI: multi-stock comparison, indicator overlays, draggable timeline
