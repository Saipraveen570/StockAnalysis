import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from typing import Dict
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# ---------------------------
# Helper / Validation
# ---------------------------
def safe_ticker_symbol(t: str) -> str:
    """Normalize and validate ticker string. Return empty string if invalid."""
    if not t:
        return ""
    t = str(t).strip().upper()
    # allow letters, numbers, dot, dash; limit length
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
    if len(t) > 12 or any(ch not in allowed for ch in t):
        return ""
    return t

def iso_date(d: datetime.date) -> str:
    return d.isoformat() if isinstance(d, (datetime.date, datetime.datetime)) else str(d)

# ---------------------------
# SAFE DATA FUNCTIONS
# ---------------------------
# Use streamlit caching to avoid repeated downloads; keep time-to-live small if desired via ttl
@st.cache_data(show_spinner=False)
def get_ticker_obj(ticker: str):
    try:
        return yf.Ticker(ticker)
    except Exception:
        return None

@st.cache_data(show_spinner=False)
def get_company_info(ticker: str) -> Dict:
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return {}
    try:
        tobj = get_ticker_obj(ticker)
        if tobj is None:
            return {}
        info = tobj.info or {}
    except Exception:
        info = {}
    # keep only JSON-serializable simple fields
    clean = {k: v for k, v in info.items() if isinstance(v, (int, float, str, bool, type(None)))}
    return clean

@st.cache_data(show_spinner=False)
def get_company_summary(ticker: str) -> str:
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return "No summary available."
    try:
        tobj = get_ticker_obj(ticker)
        if tobj is None:
            return "No summary available."
        info = tobj.info or {}
        return info.get("longBusinessSummary", "No summary available.")
    except Exception:
        return "No summary available."

@st.cache_data(show_spinner=False)
def load_price_data(ticker: str, start: datetime.date, end: datetime.date) -> pd.DataFrame:
    """Downloads price data for the given date range. Returns empty DataFrame on failure."""
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return pd.DataFrame()
    # ensure sensible date order
    if start is None or end is None:
        return pd.DataFrame()
    if start > end:
        start, end = end, start
    try:
        return yf.download(ticker, start=iso_date(start), end=iso_date(end), progress=False)
    except Exception:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_full_price(ticker: str) -> pd.DataFrame:
    ticker = safe_ticker_symbol(ticker)
    if not ticker:
        return pd.DataFrame()
    try:
        tobj = get_ticker_obj(ticker)
        if tobj is None:
            return pd.DataFrame()
        hist = tobj.history(period="max")
        return hist
    except Exception:
        return pd.DataFrame()

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Stock Analysis", page_icon="💹", layout="wide")
st.title("Stock Analysis")

# inputs
today = datetime.date.today()
col1, col2, col3 = st.columns(3)

with col1:
    raw_ticker = st.text_input("🔎 Stock Ticker", "AAPL")
    ticker = safe_ticker_symbol(raw_ticker)
    if not ticker:
        st.warning("Please enter a valid ticker (letters, numbers, ., -).")
with col2:
    start_date = st.date_input("📅 Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("📅 End Date", today)

# if ticker invalid, stop gracefully (no crash)
if not ticker:
    st.info("Enter a valid ticker to load data and company info.")
    st.stop()

# company info
info = get_company_info(ticker)
summary = get_company_summary(ticker)

st.subheader(f"🏢 {ticker} Overview")
st.write(summary)

# Safely display info fields with get and fallback
def safe_val(x):
    return "N/A" if x is None else x

st.write("💼 Sector:", safe_val(info.get("sector")))
st.write("👥 Employees:", safe_val(info.get("fullTimeEmployees")))
st.write("🌐 Website:", safe_val(info.get("website")))

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
    except Exception as e:
        st.error("Unable to render info table (chart).")
        st.write(df1)

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
        st.write(df2)

# ---------------------------
# Price & Metrics
# ---------------------------
df = load_price_data(ticker, start_date, end_date)

if df.empty or "Close" not in df.columns:
    st.warning("No price data available for this ticker and date range.")
    # show helpful suggestions rather than crashing
    st.info("Try a different ticker or expand the date range.")
    st.stop()

# Ensure numeric and sorted index
df = df.sort_index()
if "Close" not in df.columns:
    st.warning("Downloaded data doesn't contain 'Close' column.")
    st.stop()

latest_val = float(df["Close"].iat[-1])
if len(df) > 1:
    daily_val = float(df["Close"].iat[-1] - df["Close"].iat[-2])
else:
    daily_val = 0.0

c1, _, _ = st.columns(3)
c1.metric(
    label="📈 Daily Close",
    value=f"{latest_val:.2f}",
    delta=f"{daily_val:.2f}"
)

# For tabular display use a copy (avoid mutating original index)
display_df = df.copy()
display_df = display_df.tail(10).round(3).iloc[::-1]
# make index safe strings for table
display_df.index = display_df.index.astype(str).str[:10]
st.write("🗂️ Last 10 Days Data")
try:
    st.plotly_chart(plotly_table(display_df), use_container_width=True)
except Exception:
    st.dataframe(display_df)

st.markdown("<hr>", unsafe_allow_html=True)

# ---------------------------
# PERIOD SELECTOR — FIXED
# ---------------------------
periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]

if "period" not in st.session_state:
    st.session_state.period = "1Y"

cols = st.columns(len(periods))
for i, p in enumerate(periods):
    try:
        if cols[i].button(p):
            st.session_state.period = p
    except Exception:
        # in extremely rare UI rendering issues, continue
        pass

period = st.session_state.period

# ---------------------------
# Chart Options
# ---------------------------
c1, c2 = st.columns(2)
with c1:
    chart_type = st.selectbox("📊 Chart Type", ["Candle", "Line"])
with c2:
    indicators = st.selectbox(
        "📈 Indicator",
        ["RSI", "Moving Average", "MACD"] if chart_type == "Line" else ["RSI", "MACD"],
    )

rsi_window = st.slider("RSI Window", 5, 50, 14)

data_full = load_full_price(ticker)

if data_full.empty or "Close" not in data_full.columns:
    st.error("Error loading historical data (full history). Showing available range instead.")
    # fallback: use currently downloaded df as minimal history
    data_full = df.copy()
    if data_full.empty or "Close" not in data_full.columns:
        st.error("No usable historical data available.")
        st.stop()

# ---------------------------
# CHART RENDERING — STABLE
# ---------------------------
def safe_plot(func, *args, **kwargs):
    """Call plotting function and catch errors; displays fallback message."""
    try:
        fig = func(*args, **kwargs)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not render chart: {getattr(e, 'message', str(e))}")

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
