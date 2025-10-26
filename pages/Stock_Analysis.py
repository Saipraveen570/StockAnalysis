import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="📈 Stock Analysis Dashboard", layout="wide")

# ---- Header ----
st.title("📊 Stock Analysis Dashboard")
st.markdown("Analyze stock performance, price trends, and key insights using real-time data from Yahoo Finance.")

# ---- User Input ----
symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, MSFT, TSLA):", "AAPL").upper()
period = st.selectbox("Select Time Period:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"])

# ---- Fetch Data ----
@st.cache_data(ttl=3600)
def get_stock_data(symbol, period):
    try:
        data = yf.download(symbol, period=period, progress=False)
        if data.empty:
            return pd.DataFrame()
        data.dropna(inplace=True)
        return data
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_summary(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.get_info()
        return info.get("longBusinessSummary", None)
    except Exception:
        return None

# ---- Data Section ----
data = get_stock_data(symbol, period)

if data.empty:
    st.warning("⚠️ Unable to fetch stock data. Please check the symbol or try again later.")
else:
    # ---- Summary Section ----
    summary = get_stock_summary(symbol)
    if summary:
        with st.expander("🏢 Company Summary", expanded=True):
            st.write(summary)
    else:
        st.info("⚠️ Could not load company summary. Try again later.")

    # ---- Latest Stock Metrics ----
    last_close = data["Close"].iloc[-1] if not data["Close"].empty else None
    prev_close = data["Close"].iloc[-2] if len(data["Close"]) > 1 else None
    change = (last_close - prev_close) if last_close and prev_close else 0
    pct_change = (change / prev_close * 100) if prev_close else 0
    last_volume = data["Volume"].iloc[-1] if not data["Volume"].empty else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Last Close", f"${last_close:,.2f}" if last_close else "N/A")
    col2.metric("📉 % Change", f"{pct_change:.2f}%" if prev_close else "N/A")
    col3.metric("📊 Volume", f"{int(last_volume):,}" if last_volume else "N/A")

    # ---- Chart ----
    st.markdown("### 📈 Price Trend")
    st.line_chart(data["Close"], use_container_width=True)

    # ---- Volume Chart ----
    st.markdown("### 🔹 Volume Traded")
    st.bar_chart(data["Volume"], use_container_width=True)

st.markdown("---")
st.caption("⚡ Data source: Yahoo Finance | Dashboard by Praveen")
