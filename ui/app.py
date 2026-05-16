import os
import sys

# Ensure the project root is on sys.path so `core` is importable
# regardless of which directory Streamlit is launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from core.buffett import ZONES, current_level, historical_context, zone_summary
from core.indicators import add_indicators, fetch_stock

# ── Zone styling ──────────────────────────────────────────────────────────────

ZONE_FILL = {
    "Undervalued": "rgba(34, 197, 94, 0.12)",
    "Fair Value":  "rgba(59, 130, 246, 0.12)",
    "Overvalued":  "rgba(251, 146, 60, 0.12)",
    "Extreme":     "rgba(239, 68, 68, 0.12)",
}

# ── Cached data loaders ───────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def load_buffett(start: str, end: Optional[str] = None) -> pd.DataFrame:
    return historical_context(start, end)


@st.cache_data(ttl=3600)
def load_stock(ticker: str, start: str, end: Optional[str] = None) -> Optional[pd.DataFrame]:
    df = fetch_stock(ticker, start=start, end=end)
    if df.empty:
        return None
    return add_indicators(df)


# ── Chart builders ────────────────────────────────────────────────────────────

def build_buffett_chart(df: pd.DataFrame) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Shaded valuation zones
    max_val = df["buffett_indicator"].max() * 1.15
    for zone_name, (low, high) in ZONES.items():
        high_clipped = min(high, max_val) if high != float("inf") else max_val
        if low >= max_val:
            continue
        fig.add_hrect(
            y0=low, y1=high_clipped,
            fillcolor=ZONE_FILL[zone_name],
            line_width=0, layer="below",
        )
        fig.add_annotation(
            x=df.index[3],
            y=(low + high_clipped) / 2,
            text=zone_name,
            showarrow=False,
            font=dict(size=11, color="gray"),
        )

    # S&P 500 on secondary y-axis
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["sp500"],
            name="S&P 500",
            line=dict(color="rgba(80,80,80,0.45)", width=1.5, dash="dot"),
        ),
        secondary_y=True,
    )

    # Buffett Indicator
    fig.add_trace(
        go.Scatter(
            x=df.index, y=df["buffett_indicator"],
            name="Buffett Indicator (%)",
            line=dict(color="#e63946", width=2.5),
            fill="tozeroy",
            fillcolor="rgba(230,57,70,0.07)",
        ),
        secondary_y=False,
    )

    fig.update_layout(
        title="Buffett Indicator vs S&P 500",
        hovermode="x unified",
        legend=dict(orientation="h", y=1.06),
        height=480,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    fig.update_yaxes(title_text="Buffett Indicator (%)", secondary_y=False)
    fig.update_yaxes(title_text="S&P 500", secondary_y=True, showgrid=False)
    return fig


def build_stock_chart(
    df: pd.DataFrame,
    ticker: str,
    show_sma: bool,
    show_ema: bool,
    show_bb: bool,
) -> go.Figure:
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.03,
        subplot_titles=("Price", "MACD", "RSI"),
    )

    # ── Row 1: Price ──
    if show_bb:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_upper"],
            line=dict(color="rgba(100,100,200,0.35)", width=1),
            name="BB Upper", showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_lower"],
            line=dict(color="rgba(100,100,200,0.35)", width=1),
            fill="tonexty", fillcolor="rgba(100,100,200,0.06)",
            name="Bollinger Bands",
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_mid"],
            line=dict(color="rgba(100,100,200,0.45)", width=1, dash="dot"),
            name="BB Mid", showlegend=False,
        ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"],
        name="Close", line=dict(color="#1d3557", width=2),
    ), row=1, col=1)

    if show_sma:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA_50"],
            name="SMA 50", line=dict(color="#e9c46a", width=1.5),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["SMA_200"],
            name="SMA 200", line=dict(color="#f4a261", width=1.5),
        ), row=1, col=1)

    if show_ema:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA_12"],
            name="EMA 12", line=dict(color="#2a9d8f", width=1.5, dash="dot"),
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["EMA_26"],
            name="EMA 26", line=dict(color="#264653", width=1.5, dash="dot"),
        ), row=1, col=1)

    # ── Row 2: MACD ──
    hist_colors = [
        "#2a9d8f" if v >= 0 else "#e63946"
        for v in df["MACD_hist"].fillna(0)
    ]
    fig.add_trace(go.Bar(
        x=df.index, y=df["MACD_hist"],
        marker_color=hist_colors, name="Histogram", showlegend=False,
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD"],
        name="MACD", line=dict(color="#e63946", width=1.5),
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MACD_signal"],
        name="Signal", line=dict(color="#457b9d", width=1.5),
    ), row=2, col=1)

    # ── Row 3: RSI ──
    fig.add_trace(go.Scatter(
        x=df.index, y=df["RSI"],
        name="RSI", line=dict(color="#6a4c93", width=1.5),
    ), row=3, col=1)
    fig.add_hline(y=70, line=dict(color="rgba(230,57,70,0.5)", dash="dash", width=1), row=3, col=1)
    fig.add_hline(y=30, line=dict(color="rgba(42,157,143,0.5)", dash="dash", width=1), row=3, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="rgba(230,57,70,0.05)", line_width=0, row=3, col=1)
    fig.add_hrect(y0=0,  y1=30,  fillcolor="rgba(42,157,143,0.05)", line_width=0, row=3, col=1)

    fig.update_layout(
        title=f"{ticker} — Price & Indicators",
        hovermode="x unified",
        height=720,
        legend=dict(orientation="h", y=1.02),
        margin=dict(l=0, r=0, t=60, b=0),
        xaxis3_rangeslider_visible=False,
        barmode="relative",
    )
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    return fig


# ── Page layout ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="fred_prophet", layout="wide", page_icon="📈")
st.title("📈 fred_prophet")
st.caption("Federal Reserve data meets market analysis")

tab_buffett, tab_tech = st.tabs(["📊 Buffett Indicator", "🕯️ Technical Indicators"])

# ── Tab 1: Buffett Indicator ──────────────────────────────────────────────────

with tab_buffett:
    c1, c2 = st.columns(2)
    b_start = c1.date_input("Start", value=date(2000, 1, 1), key="b_start")
    b_end   = c2.date_input("End",   value=date.today(),     key="b_end")

    with st.spinner("Loading Buffett Indicator data…"):
        df_buffett = load_buffett(str(b_start), str(b_end))

    if df_buffett.empty:
        st.error("No data for this date range.")
    else:
        info = current_level(df_buffett)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Buffett Indicator", f"{info['buffett_indicator']}%")
        m2.metric("Valuation Zone",    info["zone"])
        m3.metric("Total Market Cap",  f"${info['market_cap_trn']:.1f}T")
        m4.metric("US GDP",            f"${info['gdp_trn']:.1f}T")

        st.plotly_chart(build_buffett_chart(df_buffett), use_container_width=True)

        st.subheader("Average Forward S&P 500 Returns by Zone")
        st.caption("What the market did after each valuation level — blank = not enough history yet.")
        summary = zone_summary(df_buffett)
        rename = {
            c: c.replace("fwd_", "").replace("_mean", " avg %").replace("_count", " n")
            for c in summary.columns
        }
        st.dataframe(summary.rename(columns=rename), use_container_width=True)

# ── Tab 2: Technical Indicators ───────────────────────────────────────────────

with tab_tech:
    with st.sidebar:
        st.header("Stock Settings")
        ticker  = st.text_input("Ticker", value="AAPL").strip().upper()
        t_start = st.date_input("Start", value=date(2020, 1, 1), key="t_start")
        t_end   = st.date_input("End",   value=date.today(),     key="t_end")
        st.divider()
        st.subheader("Overlays")
        show_sma = st.checkbox("SMA (50 / 200)",    value=True)
        show_ema = st.checkbox("EMA (12 / 26)",     value=False)
        show_bb  = st.checkbox("Bollinger Bands",   value=True)

    if ticker:
        with st.spinner(f"Loading {ticker}…"):
            df_stock = load_stock(ticker, str(t_start), str(t_end))

        if df_stock is None or df_stock.empty:
            st.error(f"No data for **{ticker}**. Check the ticker and date range.")
        else:
            latest     = df_stock["Close"].iloc[-1]
            prev_close = df_stock["Close"].iloc[-2]
            chg_pct    = (latest - prev_close) / prev_close * 100

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Last Close", f"${latest:.2f}",              f"{chg_pct:+.2f}%")
            m2.metric("RSI (14)",   f"{df_stock['RSI'].iloc[-1]:.1f}")
            m3.metric("MACD",       f"{df_stock['MACD'].iloc[-1]:.2f}")
            m4.metric("SMA 200",    f"${df_stock['SMA_200'].iloc[-1]:.2f}")

            st.plotly_chart(
                build_stock_chart(df_stock, ticker, show_sma, show_ema, show_bb),
                use_container_width=True,
            )
