import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import time
import plotly.graph_objects as go

st.set_page_config(page_title="📈 Stock Analysis", page_icon="📊", layout="wide")
st.title("📈 Stock Market Analysis Dashboard")

# ---------------- Safe Fetch Functions ----------------
@st.cache_data(ttl=300)
def safe_get_info(ticker):
    stock = yf.Ticker(ticker)
    for delay in [1, 2, 4, 8]:
        try:
            info = stock.get_info()
            if info:
                return info
        except Exception:
            time.sleep(delay)
    return {}

@st.cache_data(ttl=300)
def safe_download(ticker, start, end):
    for delay in [1, 2, 4, 8]:
        try:
            data = yf.download(ticker, start=start, end=end, progress=False, threads=False)
            if not data.empty:
                return data
        except Exception:
            time.sleep(delay)
    return pd.DataFrame()

@st.cache_data(ttl=300)
def safe_history(ticker):
    stock = yf.Ticker(ticker)
    for delay in [1, 2, 4, 8]:
        try:
            hist = stock.history(period="max")
            if not hist.empty:
                return hist
        except Exception:
            time.sleep(delay)
    return pd.DataFrame()

# ---------------- Input Section ----------------
today = datetime.date.today()
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter Stock Ticker:", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date", today)

# ---------------- Fetch Data ----------------
info = safe_get_info(ticker)
if not info:
    st.warning("⚠️ Unable to fetch company info. Yahoo Finance may have rate-limited requests.")
else:
    st.subheader(info.get("longName", ticker))
    st.write(info.get("longBusinessSummary", "Summary unavailable."))

data = safe_download(ticker, start_date, end_date)
if data.empty:
    st.error("🚫 No price data available. Please try again later (Yahoo Finance limit reached).")
    st.stop()

# ---------------- Indicators ----------------
data["MA20"] = data["Close"].rolling(window=20).mean()
data["MA50"] = data["Close"].rolling(window=50).mean()

# RSI
delta = data["Close"].diff()
gain = (delta.where(delta > 0, 0)).rolling(14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
rs = gain / loss
data["RSI"] = 100 - (100 / (1 + rs))

# MACD
exp1 = data["Close"].ewm(span=12, adjust=False).mean()
exp2 = data["Close"].ewm(span=26, adjust=False).mean()
data["MACD"] = exp1 - exp2
data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

# ---------------- Price Chart ----------------
st.markdown("### 💹 Price Chart with Moving Averages")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close", line=dict(color="blue")))
fig_price.add_trace(go.Scatter(x=data.index, y=data["MA20"], mode="lines", name="MA20", line=dict(color="orange", dash="dot")))
fig_price.add_trace(go.Scatter(x=data.index, y=data["MA50"], mode="lines", name="MA50", line=dict(color="green", dash="dot")))
fig_price.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig_price, use_container_width=True)

# ---------------- RSI Chart ----------------
st.markdown("### 📊 RSI Indicator")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], mode="lines", name="RSI", line=dict(color="purple")))
fig_rsi.add_hrect(y0=70, y1=70, line_width=1, line_dash="dash", line_color="red")
fig_rsi.add_hrect(y0=30, y1=30, line_width=1, line_dash="dash", line_color="green")
fig_rsi.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="RSI (14)")
st.plotly_chart(fig_rsi, use_container_width=True)

# ---------------- MACD Chart ----------------
st.markdown("### 📉 MACD Indicator")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"], mode="lines", name="MACD", line=dict(color="blue")))
fig_macd.add_trace(go.Scatter(x=data.index, y=data["Signal"], mode="lines", name="Signal", line=dict(color="orange")))
fig_macd.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="MACD")
st.plotly_chart(fig_macd, use_container_width=True)

# ---------------- Summary Stats ----------------
st.markdown("### 📈 Latest Data Snapshot")
latest = data.tail(1).T
latest.columns = ["Latest"]
st.dataframe(latest.round(3), use_container_width=True)
