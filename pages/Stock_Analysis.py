import streamlit as st
import pandas as pd
import requests
import datetime
import time
import plotly.graph_objects as go
import yfinance as yf

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="📈 Stock Analysis", page_icon="📊", layout="wide")
st.title("📈 Stock Market Analysis Dashboard")

# ------------------- CONFIG -------------------
ALPHA_VANTAGE_KEY = st.secrets.get("ALPHA_VANTAGE_KEY", None)
ALPHA_URL = "https://www.alphavantage.co/query"

if not ALPHA_VANTAGE_KEY:
    st.warning("⚠️ Alpha Vantage API key not found in secrets. Please add it in Streamlit Cloud > Settings > Secrets.")

# ------------------- FETCH FUNCTIONS -------------------
@st.cache_data(ttl=600)
def get_alpha_data(ticker):
    """Primary source: Alpha Vantage"""
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": "full",
        "apikey": ALPHA_VANTAGE_KEY
    }
    for delay in [1, 2, 4, 8]:
        try:
            r = requests.get(ALPHA_URL, params=params, timeout=10)
            if r.status_code == 200:
                js = r.json()
                if "Time Series (Daily)" in js:
                    df = pd.DataFrame(js["Time Series (Daily)"]).T
                    df = df.rename(columns={
                        "1. open": "Open",
                        "2. high": "High",
                        "3. low": "Low",
                        "4. close": "Close",
                        "5. adjusted close": "Adj Close",
                        "6. volume": "Volume"
                    }).astype(float)
                    df.index = pd.to_datetime(df.index)
                    df.sort_index(inplace=True)
                    return df
            time.sleep(delay)
        except Exception:
            time.sleep(delay)
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_yahoo_data(ticker, start_date, end_date):
    """Backup source: Yahoo Finance"""
    for delay in [1, 2, 4, 8]:
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not data.empty:
                return data
        except Exception as e:
            st.warning(f"Yahoo error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_company_info(ticker):
    """Try fetching company info (may fail if Yahoo rate-limited)"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.get_info()
        return info or {}
    except Exception:
        return {}

# ------------------- USER INPUTS -------------------
today = datetime.date.today()
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date", today)

# ------------------- COMPANY INFO -------------------
info = get_company_info(ticker)
if info:
    st.subheader(info.get("longName", ticker))
    st.write(info.get("longBusinessSummary", "Summary unavailable."))
else:
    st.info("ℹ️ Company info unavailable (Yahoo rate-limited).")

# ------------------- FETCH STOCK DATA -------------------
st.markdown("⏳ Fetching stock data...")

data = pd.DataFrame()
data_source = None

# 1️⃣ Try Alpha Vantage first
if ALPHA_VANTAGE_KEY:
    data = get_alpha_data(ticker)
    if not data.empty:
        data_source = "Alpha Vantage"

# 2️⃣ Fallback: Yahoo Finance
if data.empty:
    st.warning("⚠️ Alpha Vantage unavailable or limit reached. Trying Yahoo Finance...")
    data = get_yahoo_data(ticker, start_date, end_date)
    if not data.empty:
        data_source = "Yahoo Finance"

if data.empty:
    st.error("❌ Failed to fetch data from both Alpha Vantage and Yahoo Finance. Please try again later.")
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
st.markdown(f"### 💹 Price Chart with Moving Averages ({data_source})")
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
st.markdown("### 📈 Latest Data Snapshot")
latest = data.tail(1).T
latest.columns = ["Latest"]
st.dataframe(latest.round(3), use_container_width=True)
