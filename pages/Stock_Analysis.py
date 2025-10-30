"""
Stock Analysis Dashboard
Streamlit application for stock data exploration, company info, and technical charts.
Uses Plotly for visualization and YFinance for price + fundamentals.
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from typing import Dict

from pages.utils.plotly_figure import (
    plotly_table,
    close_chart,
    candlestick,
    RSI,
    Moving_average,
    MACD,
)

# ---------------------------
# Helpers: ticker and date utils
# ---------------------------
def safe_ticker_symbol(t: str) -> str:
    """
    Normalize and validate ticker input.
    Return empty string on invalid form.
    """
    if not t:
        return ""
    t = str(t).strip().upper()
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
    if len(t) > 12 or any(ch not in allowed for ch in t):
        return ""
    return t

def iso_date(d: datetime.date) -> str:
    """Convert date/datetime to ISO string, fallback to string conversion."""
    return d.isoformat() if isinstance(d, (datetime.date, datetime.datetime)) else str(d)

# ---------------------------
# SAFE DATA FETCH FUNCTIONS
# ---------------------------
@st.cache_data(show_spinner=False)
def get_ticker_obj(ticker: str):
    try:
        return yf.Ticker(ticker)
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def get_company_info(ticker: str) -> Dict:
    """
    Fetch company metadata and sanitize to simple JSON-friendly fields.
    """
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return {}
    try:
        info = (get_ticker_obj(ticker) or {}).info or {}
    except Exception:
        info = {}
    return {k: v for k, v in info.items() if isinstance(v, (int, float, str, bool, type(None)))}

@st.cache_data(show_spinner=False)
def get_company_summary(ticker: str) -> str:
    """
    Return business summary, safe fallback if unavailable.
    """
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return "No summary available."
    try:
        info = (get_ticker_obj(ticker) or {}).info or {}
        return info.get("longBusinessSummary", "No summary available.")
    except Exception:
        return "No summary available."

@st.cache_data(show_spinner=False)
def load_price_data(ticker: str, start: datetime.date, end: datetime.date) -> pd.DataFrame:
    """
    Download OHLC price data for custom date range.
    Always returns DataFrame (may be empty).
    """
    ticker = safe_ticker_symbol(ticker)
    if not ticker or start is None or end is None:
        return pd.DataFrame()
    if start > end:
        start, end = end, start
    try:
        return yf.download(ticker, start=iso_date(start), end=iso_date(end), progress=False)
    except Exception:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_full_price(ticker: str) -> pd.DataFrame:
    """
    Fetch max-available price history for indicator charts.
    """
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return pd.DataFrame()
    try:
        hist = (get_ticker_obj(ticker) or {}).history(period="max")
        return hist if isinstance(hist, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# ---------------------------
# PAGE CONFIGURATION
# ---------------------------
st.set_page_config(page_title="Stock Analysis", page_icon="💹", layout="wide")
st.title("Stock Analysis")

today = datetime.date.today()
col1, col2, col3 = st.columns(3)

with col1:
    raw_ticker = st.text_input("🔎 Stock Ticker", "AAPL")
    ticker = safe_ticker_symbol(raw_ticker)
    if not ticker:
        st.warning("Enter a valid ticker: A-Z, 0-9, dot, dash.")

with col2:
    start_date = st.date_input("📅 Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("📅 End Date", today)

if not ticker:
    st.stop()

# ---------------------------
# COMPANY PROFILE
# ---------------------------
info = get_company_info(ticker)
summary = get_company_summary(ticker)

st.subheader(f"🏢 {ticker} Overview")
st.write(summary)

def safe_val(x):
    return "N/A" if x is None else x

# Summary metrics
c1, c2 = st.columns(2)

with c1:
    df1 = pd.DataFrame({
        "Metric": ["Market Cap", "Beta", "EPS", "PE Ratio"],
        "Value": [
            safe_val(info.get("marketCap")),
            safe_val(info.get("beta")),
            safe_val(info.get("trailingEps")),
            safe_val(info.get("trailingPE")),
        ]
    })
    try:
        st.plotly_chart(plotly_table(df1), use_container_width=True)
    except Exception:
        st.dataframe(df1)

with c2:
    df2 = pd.DataFrame({
        "Metric": ["Quick Ratio", "Rev/Share", "Profit Margin", "Debt/Equity", "ROE"],
        "Value": [
            safe_val(info.get("quickRatio")),
            safe_val(info.get("revenuePerShare")),
            safe_val(info.get("profitMargins")),
            safe_val(info.get("debtToEquity")),
            safe_val(info.get("returnOnEquity")),
        ]
    })
    try:
        st.plotly_chart(plotly_table(df2), use_container_width=True)
    except Exception:
        st.dataframe(df2)

# ---------------------------
# PRICE DATA
# ---------------------------
df = load_price_data(ticker, start_date, end_date)

if df.empty or "Close" not in df.columns:
    st.warning("No price data for selection. Adjust ticker or dates.")
    st.stop()

df = df.sort_index()

latest = float(df["Close"].iat[-1])
prev = float(df["Close"].iat[-2]) if len(df) > 1 else latest

st.metric("📈 Daily Close", f"{latest:.2f}", f"{latest - prev:.2f}")

disp = df.tail(10).round(3).iloc[::-1].copy()
disp.index = disp.index.astype(str).str[:10]

st.write("🗂️ Last 10 Days")
try:
    st.plotly_chart(plotly_table(disp), use_container_width=True)
except Exception:
    st.dataframe(disp)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------
# PERIOD TOGGLE
# ---------------------------
periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
st.session_state.setdefault("period", "1Y")

cols = st.columns(len(periods))
for i, p in enumerate(periods):
    if cols[i].button(p):
        st.session_state.period = p

period = st.session_state.period

# ---------------------------
# CHART CONTROLS
# ---------------------------
c1, c2 = st.columns(2)
chart_type = c1.selectbox("Chart Type", ["Candle", "Line"])
indicators = c2.selectbox(
    "Indicator",
    ["RSI", "Moving Average", "MACD"] if chart_type == "Line" else ["RSI", "MACD"]
)
rsi_window = st.slider("RSI Window", 5, 50, 14)

data_full = load_full_price(ticker)
if data_full.empty or "Close" not in data_full.columns:
    st.error("Historical data unavailable; using current period only.")
    data_full = df.copy()

# ---------------------------
# SAFE CHART RENDER
# ---------------------------
def safe_plot(func, *args, **kwargs):
    try:
        st.plotly_chart(func(*args, **kwargs), use_container_width=True)
    except Exception as e:
        st.error(f"Chart error: {e}")

if chart_type == "Candle":
    safe_plot(candlestick, data_full, period)
    if indicators == "RSI":
        safe_plot(RSI, data_full, period, rsi_window)
    elif indicators == "MACD":
        safe_plot(MACD, data_full, period)
else:
    safe_plot(close_chart, data_full, period)
    if indicators == "RSI":
        safe_plot(RSI, data_full, period, rsi_window)
    elif indicators == "Moving Average":
        safe_plot(Moving_average, data_full, period)
    elif indicators == "MACD":
        safe_plot(MACD, data_full, period)
