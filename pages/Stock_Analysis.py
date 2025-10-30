# pages/Stock_Analysis.py
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import plotly.express as px
import plotly.graph_objects as go
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD
import numpy as np

# Optional heavy lib for forecasting (kept optional)
try:
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    sarimax_available = True
except Exception:
    sarimax_available = False

# -------------------------
# Page config / theme
# -------------------------
st.set_page_config(page_title="Stock Analysis", page_icon="💹", layout="wide")
# Theme toggle (dark/light)
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme_toggle = st.sidebar.radio("Theme", options=["dark", "light"], index=0)
st.session_state.theme = theme_toggle

# small CSS tweaks
if st.session_state.theme == "dark":
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #e6eef8; }
        .metric-card { background:#0f1720; padding:10px; border-radius:8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .metric-card { background:#ffffff; padding:10px; border-radius:8px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# Utility helpers
# -------------------------
def safe_scalar(x, default=0.0):
    """Return python float from pandas scalar, robust to types."""
    try:
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except Exception:
        return float(default)


@st.cache_data(ttl=600, show_spinner=False)
def fetch_price_df(symbol: str, period: str = "1y", interval: str = "1d"):
    """
    Fetch price dataframe using yfinance. Cached to reduce calls.
    Returns empty DataFrame on failure.
    """
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, threads=False)
        # ensure we have numeric columns expected
        if df is None or df.empty or "Close" not in df.columns:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_range_df(symbol: str, start: datetime.date, end: datetime.date):
    """Fetch price range (used for data table and metrics)."""
    try:
        df = yf.download(symbol, start=start, end=end, progress=False, threads=False)
        if df is None or df.empty or "Close" not in df.columns:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_company_info_dict(symbol: str):
    """
    Return a serializable dict of company info (only basic primitive types).
    Do not return Ticker object.
    """
    try:
        info = yf.Ticker(symbol).info
        if not isinstance(info, dict):
            return {}
    except Exception:
        info = {}
    # sanitize to primitives only
    clean = {k: v for k, v in info.items() if isinstance(v, (str, int, float, bool, type(None)))}
    return clean


def try_nse_fallback(symbol: str, period="1y", interval="1d"):
    """
    Try original symbol, then attempt common Indian suffixes if no data.
    Returns df and used_symbol.
    """
    df = fetch_price_df(symbol, period=period, interval=interval)
    if not df.empty:
        return df, symbol

    # try with .NS then .BO
    for suffix in [".NS", ".BO"]:
        candidate = symbol + suffix if not symbol.upper().endswith(suffix) else symbol
        df2 = fetch_price_df(candidate, period=period, interval=interval)
        if not df2.empty:
            return df2, candidate

    return pd.DataFrame(), symbol


# -------------------------
# Sidebar / Inputs
# -------------------------
st.sidebar.header("Stock Inputs")
raw_ticker = st.sidebar.text_input("Ticker (example: AAPL, RELIANCE.NS)", value="AAPL").strip()

if raw_ticker == "":
    st.sidebar.error("Enter a ticker to continue.")
    st.stop()

ticker = raw_ticker.upper()

# date inputs (main UI)
today = datetime.date.today()
default_start = today - datetime.timedelta(days=365)
start_date = st.sidebar.date_input("Start date", default_start)
end_date = st.sidebar.date_input("End date", today)
if start_date >= end_date:
    st.sidebar.error("Start date must be before end date.")
    st.stop()

# real-time refresh control (manual)
if "last_price_refresh" not in st.session_state:
    st.session_state.last_price_refresh = None
if "last_price_value" not in st.session_state:
    st.session_state.last_price_value = None
if "used_symbol" not in st.session_state:
    st.session_state.used_symbol = ticker

# Period buttons
periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
if "selected_period" not in st.session_state:
    st.session_state.selected_period = "1Y"
cols = st.sidebar.columns(len(periods))
for i, p in enumerate(periods):
    if cols[i].button(p):
        st.session_state.selected_period = p

# -------------------------
# Header + Company Overview
# -------------------------
st.title("📈 Stock Analysis")
st.markdown(f"**Ticker:** `{ticker}`")

# company info (safe cached)
company_info = get_company_info_dict(ticker)
company_summary = company_info.get("longBusinessSummary", None)
# if company summary missing from dict, fetch separately non-cached (avoid caching unserializable)
if not company_summary:
    try:
        tmp_info = yf.Ticker(ticker).info
        if isinstance(tmp_info, dict):
            company_summary = tmp_info.get("longBusinessSummary", "No summary available.")
        else:
            company_summary = "No summary available."
    except Exception:
        company_summary = "No summary available."

st.subheader("🏢 Company Summary")
st.write(company_summary)

# quick company key metrics (safe access)
st.write("💼 Sector:", company_info.get("sector", "N/A"))
st.write("👥 Full Time Employees:", company_info.get("fullTimeEmployees", "N/A"))
st.write("🌐 Website:", company_info.get("website", "N/A"))

# -------------------------
# Fetch primary datasets
# -------------------------
# For table & metrics: use range fetch (range uses start/end set by user)
df_range = fetch_range_df(ticker, start=start_date, end=end_date)
if df_range.empty:
    # fallback attempts with NSE suffixes (.NS, .BO)
    df_range, used_symbol = try_nse_fallback(ticker, period="1y")
    st.session_state.used_symbol = used_symbol
    if df_range.empty:
        st.error("Invalid ticker or no data available. Try different symbol (e.g., add .NS for NSE).")
        st.stop()
else:
    st.session_state.used_symbol = ticker

# For charts: fetch smaller period based on selected period to reduce payload
selected_period = st.session_state.selected_period  # e.g. "5D" / "1Y"
period_map = {"5D": ("5d", "15m"), "1M": ("1mo", "1h"), "6M": ("6mo", "1d"),
              "YTD": ("ytd", "1d"), "1Y": ("1y", "1d"), "5Y": ("5y", "1d"), "MAX": ("max", "1d")}
period_key, interval_key = period_map.get(selected_period, ("1y", "1d"))

# prefer used_symbol (from fallback)
used_symbol = st.session_state.get("used_symbol", ticker)
df_chart = fetch_price_df(used_symbol, period=period_key, interval=interval_key)
if df_chart.empty:
    # fallback to a 1y daily fetch to at least show something
    df_chart = fetch_price_df(used_symbol, period="1y", interval="1d")
    if df_chart.empty:
        st.error("Unable to fetch chart data for this ticker.")
        st.stop()

# -------------------------
# Real-time price card (manual refresh)
# -------------------------
st.subheader("Real-time Price")
rt_col1, rt_col2, rt_col3 = st.columns([2, 2, 1])

# Refresh button fetches latest 1d 1m/1m depending on availability; cached calls will prevent abuse
if rt_col3.button("Refresh Price"):
    # fetch last minute / day
    latest_df = fetch_price_df(used_symbol, period="5d", interval="1m")
    if latest_df.empty:
        latest_df = fetch_price_df(used_symbol, period="1d", interval="1d")
    if not latest_df.empty:
        last_close = latest_df["Close"].iloc[-1]
        st.session_state.last_price_value = safe_scalar(last_close)
        st.session_state.last_price_refresh = datetime.datetime.now()
    else:
        st.warning("Unable to refresh price (yfinance may be rate-limited).")

# show last saved value if exists, otherwise show last value from df_range
if st.session_state.last_price_value is None:
    # try to pick last close from df_chart or df_range
    if not df_chart.empty:
        st.session_state.last_price_value = safe_scalar(df_chart["Close"].iloc[-1])
    elif not df_range.empty:
        st.session_state.last_price_value = safe_scalar(df_range["Close"].iloc[-1])

price_val = st.session_state.last_price_value
price_refresh = st.session_state.last_price_refresh
rt_col1.markdown(f"<div style='font-size:20px'>**{used_symbol}**</div>", unsafe_allow_html=True)
rt_col2.metric(label="Last Price", value=f"{price_val:.2f}", delta=None)
if price_refresh:
    rt_col1.caption(f"Refreshed: {price_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

# -------------------------
# KPIs and table
# -------------------------
st.markdown("---")
k1, k2, k3 = st.columns(3)

latest_close = safe_scalar(df_range["Close"].iloc[-1])
prev_close = safe_scalar(df_range["Close"].iloc[-2]) if len(df_range) > 1 else latest_close
delta_val = latest_close - prev_close
pct_change = (delta_val / prev_close * 100) if prev_close != 0 else 0.0

k1.metric("Close", f"{latest_close:.2f}", f"{delta_val:.2f}")
k2.metric("Change (%)", f"{pct_change:.2f}%")
k3.metric("Data Points", f"{len(df_range)}")

st.markdown("### Historical (Latest 10 rows)")
display_df = df_range.tail(10).round(3).reset_index()
st.plotly_chart(plotly_table(display_df), use_container_width=True)

# -------------------------
# Charts area (two-column)
# -------------------------
st.markdown("---")
col_left, col_right = st.columns([3, 1])

with col_left:
    # Candlestick with indicator overlays
    st.subheader("Price Chart")
    try:
        st.plotly_chart(candlestick(df_chart, selected_period), use_container_width=True)
    except Exception:
        st.error("Chart rendering failed.")

    # Line close + MA
    try:
        st.plotly_chart(close_chart(df_chart, selected_period), use_container_width=True)
    except Exception:
        st.warning("Close chart unavailable for this period.")

    # Indicator selection
    ind = st.selectbox("Indicator", ["RSI", "Moving Average", "MACD"])
    try:
        if ind == "RSI":
            st.plotly_chart(RSI(df_chart, selected_period, window=14), use_container_width=True)
        elif ind == "Moving Average":
            st.plotly_chart(Moving_average(df_chart, selected_period), use_container_width=True)
        elif ind == "MACD":
            st.plotly_chart(MACD(df_chart, selected_period), use_container_width=True)
    except Exception:
        st.warning("Indicator unavailable for selected period (insufficient data).")

with col_right:
    # Compact summary card and quick links
    st.subheader("Quick Summary")
    st.write("Market Cap:", company_info.get("marketCap", "N/A"))
    st.write("PE Ratio:", company_info.get("trailingPE", "N/A"))
    st.write("EPS:", company_info.get("trailingEps", "N/A"))
    st.write("Sector:", company_info.get("sector", "N/A"))

    st.markdown("---")
    st.write("Quick Actions")
    if st.button("Open Yahoo Finance Page"):
        st.write(f"https://finance.yahoo.com/quote/{used_symbol}")

# -------------------------
# Forecasting (safe)
# -------------------------
st.markdown("---")
st.subheader("Forecasting (Optional)")

if not sarimax_available:
    st.info("SARIMAX forecasting disabled (install `statsmodels` to enable).")
else:
    if st.button("Run SARIMAX 15-step Forecast"):
        with st.spinner("Fitting model..."):
            try:
                # use daily close for model (resample to business days if needed)
                series = df_range["Close"].dropna()
                if len(series) < 60:
                    st.error("Not enough data for forecasting (>=60 points required).")
                else:
                    model = SARIMAX(series, order=(1,1,1), seasonal_order=(0,0,0,0))
                    res = model.fit(disp=False)
                    forecast = res.get_forecast(steps=15)
                    fc_index = pd.date_range(start=series.index[-1] + pd.Timedelta(days=1), periods=15, freq="B")
                    fc_values = forecast.predicted_mean
                    fc_df = pd.Series(fc_values, index=fc_index).to_frame(name="Forecast")
                    fig_fc = go.Figure()
                    fig_fc.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines", name="Historical"))
                    fig_fc.add_trace(go.Scatter(x=fc_df.index, y=fc_df["Forecast"], mode="lines", name="Forecast"))
                    st.plotly_chart(fig_fc, use_container_width=True)
            except Exception as e:
                st.error("Forecasting failed: " + str(e))

# -------------------------
# Performance notes & footer
# -------------------------
st.markdown("---")
st.write(
    "Notes: Data is cached (ttl=10 min). Use the 'Refresh Price' button sparingly to avoid rate limits. "
    "If data doesn't appear for an Indian stock, try adding `.NS` (NSE) or `.BO` (BSE) suffix."
)
