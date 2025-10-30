import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# =====================================
# SAFE DATA FUNCTIONS
# =====================================
@st.cache_data(show_spinner=False)
def get_company_info(ticker):
    try:
        info = yf.Ticker(ticker).info
    except:
        info = {}

    clean = {k: v for k, v in info.items() if isinstance(v, (int, float, str, bool, type(None)))}
    return clean  # only return dict (serializable)

@st.cache_data(show_spinner=False)
def get_company_summary(ticker):
    try:
        info = yf.Ticker(ticker).info
        return info.get("longBusinessSummary", "No summary available.")
    except:
        return "No summary available."

@st.cache_data(show_spinner=False)
def load_price_data(ticker, start, end):
    try:
        return yf.download(ticker, start=start, end=end)
    except:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_full_price(ticker):
    try:
        return yf.Ticker(ticker).history(period="max")
    except:
        return pd.DataFrame()

# =====================================
# PAGE CONFIG
# =====================================
st.set_page_config(page_title="Stock Analysis", page_icon="💹", layout="wide")
st.title("Stock Analysis")

today = datetime.date.today()

col1, col2, col3 = st.columns(3)
with col1: ticker = st.text_input("🔎 Stock Ticker", "AAPL")
with col2: start_date = st.date_input("📅 Start Date", today - datetime.timedelta(days=365))
with col3: end_date = st.date_input("📅 End Date", today)

# =====================================
# COMPANY INFO
# =====================================
info = get_company_info(ticker)
summary = get_company_summary(ticker)

st.subheader(f"🏢 {ticker} Overview")
st.write(summary)
st.write("💼 Sector:", info.get("sector", "N/A"))
st.write("👥 Employees:", info.get("fullTimeEmployees", "N/A"))
st.write("🌐 Website:", info.get("website", "N/A"))

c1, c2 = st.columns(2)
with c1:
    df1 = pd.DataFrame({
        "Metric": ["Market Cap", "Beta", "EPS", "PE Ratio"],
        "Value": [
            info.get("marketCap"), info.get("beta"),
            info.get("trailingEps"), info.get("trailingPE"),
        ]
    })
    st.plotly_chart(plotly_table(df1), use_container_width=True)

with c2:
    df2 = pd.DataFrame({
        "Metric": ["Quick Ratio", "Rev/Share", "Profit Margin", "Debt/Equity", "ROE"],
        "Value": [
            info.get("quickRatio"), info.get("revenuePerShare"),
            info.get("profitMargins"), info.get("debtToEquity"),
            info.get("returnOnEquity"),
        ]
    })
    st.plotly_chart(plotly_table(df2), use_container_width=True)

# =============================
# Price & Metrics
# =============================

df = load_price_data(ticker, start_date, end_date)

if df.empty or "Close" not in df.columns:
    st.warning("No price data available for this ticker.")
    st.stop()

latest = df["Close"].iloc[-1]
prev = df["Close"].iloc[-2] if len(df) > 1 else latest
daily_change = latest - prev

# Convert safely (avoids Series warnings)
latest_val = float(latest)
daily_val = float(daily_change)

# Metrics display
c1, _, _ = st.columns(3)
c1.metric(
    label="📈 Daily Close",
    value=f"{latest_val:.2f}",
    delta=f"{daily_val:.2f}"
)

df.index = df.index.astype(str).str[:10]
st.write("🗂️ Last 10 Days Data")
st.plotly_chart(plotly_table(df.tail(10).round(3).iloc[::-1]), use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# =====================================
# PERIOD SELECTOR — Stable Session
# =====================================
periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]

if "period" not in st.session_state:
    st.session_state.period = "1Y"

cols = st.columns(len(periods))
for i, p in enumerate(periods):
    if cols[i].button(p):
        st.session_state.period = p

period = st.session_state.period.lower()
period = "max" if period == "max" else period

# =====================================
# Chart Options
# =====================================
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
    st.error("Error loading historical data.")
    st.stop()

# =====================================
# CHART RENDERING — Stable
# =====================================
if chart_type == "Candle":
    st.plotly_chart(candlestick(data_full, period), use_container_width=True)

    if indicators == "RSI":
        st.plotly_chart(RSI(data_full, period, rsi_window), use_container_width=True)

    elif indicators == "MACD":
        st.plotly_chart(MACD(data_full, period), use_container_width=True)

else:
    st.plotly_chart(close_chart(data_full, period), use_container_width=True)

    if indicators == "RSI":
        st.plotly_chart(RSI(data_full, period, rsi_window), use_container_width=True)

    elif indicators == "Moving Average":
        st.plotly_chart(Moving_average(data_full, period), use_container_width=True)

    elif indicators == "MACD":
        st.plotly_chart(MACD(data_full, period), use_container_width=True)
