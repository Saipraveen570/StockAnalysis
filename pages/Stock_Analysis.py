import streamlit as st
import pandas as pd
import datetime
import time
import plotly.graph_objects as go
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Stock Analysis", page_icon="📊", layout="wide")
st.title("Stock Market Analysis Dashboard")

# ------------------- CONFIG -------------------
st.markdown("Use this dashboard to analyze stock performance using Yahoo Finance & Alpha Vantage backup API.")

# ------------------- INPUTS -------------------
today = datetime.date.today()
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date", today)

# ------------------- FETCH DATA -------------------
st.markdown("⏳ Fetching stock data...")

@st.cache_data(ttl=600)
def fetch_yahoo_data(ticker, start_date, end_date):
    """Try fetching data from Yahoo Finance"""
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        return data
    except Exception as e:
        st.warning(f"Yahoo Finance failed: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_alpha_data(ticker):
    """Fallback: Fetch data from Alpha Vantage"""
    try:
        # ✅ Securely get API key from Streamlit secrets
        ALPHA_KEY = st.secrets["general"]["ALPHA_VANTAGE_KEY"]

        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        data, _ = ts.get_daily(symbol=ticker, outputsize="full")

        # Rename columns to match Yahoo style
        data = data.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            }
        )
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)
        return data
    except Exception as e:
        st.error(f"Alpha Vantage failed: {e}")
        return pd.DataFrame()

# Fetch from Yahoo first
data = fetch_yahoo_data(ticker, start_date, end_date)

# If Yahoo fails, try Alpha
if data.empty:
    st.warning("⚠️ Yahoo Finance failed. Trying Alpha Vantage...")
    data = fetch_alpha_data(ticker)

# Stop if no data from both
if data.empty:
    st.error("❌ Failed to fetch data from both Yahoo and Alpha Vantage. Please check symbol or API key.")
    st.stop()

# ------------------- FILTER -------------------
data = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]

# ------------------- INDICATORS -------------------
data["MA20"] = data["Close"].rolling(20).mean()
data["MA50"] = data["Close"].rolling(50).mean()

delta = data["Close"].diff()
gain = delta.clip(lower=0).rolling(14).mean()
loss = -delta.clip(upper=0).rolling(14).mean()
rs = gain / loss
data["RSI"] = 100 - (100 / (1 + rs))

exp1 = data["Close"].ewm(span=12, adjust=False).mean()
exp2 = data["Close"].ewm(span=26, adjust=False).mean()
data["MACD"] = exp1 - exp2
data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

# ------------------- PRICE CHART -------------------
st.markdown("### 💹 Price Chart with Moving Averages")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20", line=dict(color="orange", dash="dot")))
fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50", line=dict(color="green", dash="dot")))
fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig, use_container_width=True)

# ------------------- RSI -------------------
st.markdown("### 📊 RSI Indicator")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], line=dict(color="purple")))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(template="plotly_white", yaxis_title="RSI (14)")
st.plotly_chart(fig_rsi, use_container_width=True)

# ------------------- MACD -------------------
st.markdown("### 📉 MACD Indicator")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD", line=dict(color="blue")))
fig_macd.add_trace(go.Scatter(x=data.index, y=data["Signal"], name="Signal", line=dict(color="orange")))
fig_macd.update_layout(template="plotly_white", yaxis_title="MACD")
st.plotly_chart(fig_macd, use_container_width=True)

# ------------------- SNAPSHOT -------------------
st.markdown("### Latest Data Snapshot")
latest = data.tail(1).T
latest.columns = ["Latest"]
st.dataframe(latest.round(3), use_container_width=True)
