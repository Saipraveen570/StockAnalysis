import streamlit as st
import pandas as pd
import requests
import datetime
import time
import plotly.graph_objects as go
import yfinance as yf

# ------------------------------------------------------------
# ⚙️ Streamlit Page Configuration
# ------------------------------------------------------------
st.set_page_config(page_title="📊 Stock Market Analysis", page_icon="📈", layout="wide")
st.title("📊 Stock Market Analysis Dashboard")

# ------------------------------------------------------------
# 🔑 API Configuration (Secure)
# ------------------------------------------------------------
# 👇 Secret key stored securely in Streamlit Cloud / .streamlit/secrets.toml
ALPHA_VANTAGE_KEY = st.secrets.get("ALPHA_VANTAGE_KEY")

if not ALPHA_VANTAGE_KEY:
    st.warning("⚠️ Alpha Vantage API key not found in secrets. Using Yahoo Finance only.")
ALPHA_URL = "https://www.alphavantage.co/query"

# ------------------------------------------------------------
# 🔧 Helper Functions
# ------------------------------------------------------------
@st.cache_data(ttl=600)
def get_yahoo_data(ticker, start, end):
    """Fetch data from Yahoo Finance"""
    try:
        df = yf.download(ticker, start=start, end=end)
        if df is not None and not df.empty:
            df.reset_index(inplace=True)
            df.rename(columns={"Adj Close": "Close"}, inplace=True)
            return df
    except Exception as e:
        print(f"Yahoo error: {e}")
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_alpha_data(ticker):
    """Fetch data from Alpha Vantage"""
    if not ALPHA_VANTAGE_KEY:
        return pd.DataFrame()

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
                    df.reset_index(inplace=True)
                    df.rename(columns={"index": "Date"}, inplace=True)
                    return df
            time.sleep(delay)
        except Exception as e:
            print(f"Alpha fetch failed: {e}")
            time.sleep(delay)
    return pd.DataFrame()

@st.cache_data(ttl=600)
def get_company_info(ticker):
    """Get company info from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.get_info()
        return info or {}
    except Exception:
        return {}

# ------------------------------------------------------------
# 🎯 User Input
# ------------------------------------------------------------
today = datetime.date.today()

col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date", today)

# ------------------------------------------------------------
# 🏢 Company Info
# ------------------------------------------------------------
info = get_company_info(ticker)
if info:
    st.subheader(info.get("longName", ticker))
    st.write(info.get("longBusinessSummary", "Summary unavailable."))
else:
    st.info("ℹ️ Company info unavailable (Yahoo may be restricted).")

# ------------------------------------------------------------
# 🧭 Data Fetching
# ------------------------------------------------------------
st.write("⏳ Fetching data from Yahoo Finance...")

data = get_yahoo_data(ticker, start_date, end_date)
source = "Yahoo Finance"

if data.empty and ALPHA_VANTAGE_KEY:
    st.warning("⚠️ Yahoo Finance failed. Switching to Alpha Vantage...")
    data = get_alpha_data(ticker)
    source = "Alpha Vantage"

if data.empty:
    st.error("❌ Failed to fetch data from both Yahoo and Alpha Vantage. Please check symbol or API key.")
    st.stop()

st.success(f"✅ Data successfully fetched from **{source}**!")

# ------------------------------------------------------------
# ⏳ Filter Data by Date
# ------------------------------------------------------------
data = data.loc[(data["Date"].dt.date >= start_date) & (data["Date"].dt.date <= end_date)]

# ------------------------------------------------------------
# 📈 Technical Indicators
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# 📉 Visualization Section
# ------------------------------------------------------------

# --- Price Chart with MAs ---
st.markdown("### 💹 Stock Price with Moving Averages")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], name="Close", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=data["Date"], y=data["MA20"], name="MA20", line=dict(color="orange", dash="dot")))
fig.add_trace(go.Scatter(x=data["Date"], y=data["MA50"], name="MA50", line=dict(color="green", dash="dot")))
fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig, use_container_width=True)

# --- RSI Indicator ---
st.markdown("### 📊 RSI Indicator")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data["Date"], y=data["RSI"], line=dict(color="purple")))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(template="plotly_white", yaxis_title="RSI (14)")
st.plotly_chart(fig_rsi, use_container_width=True)

# --- MACD Indicator ---
st.markdown("### 📉 MACD Indicator")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=data["Date"], y=data["MACD"], name="MACD", line=dict(color="blue")))
fig_macd.add_trace(go.Scatter(x=data["Date"], y=data["Signal"], name="Signal", line=dict(color="orange")))
fig_macd.update_layout(template="plotly_white", yaxis_title="MACD")
st.plotly_chart(fig_macd, use_container_width=True)

# ------------------------------------------------------------
# 🧾 Latest Snapshot
# ------------------------------------------------------------
st.markdown("### 📈 Latest Data Snapshot")
latest = data.tail(1).T
latest.columns = ["Latest"]
st.dataframe(latest.round(3), use_container_width=True)
