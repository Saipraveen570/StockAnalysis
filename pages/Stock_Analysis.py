import streamlit as st
import pandas as pd
import datetime
import plotly.graph_objects as go
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="📈 Stock Analysis", page_icon="📊", layout="wide")
st.title("📈 Stock Market Analysis Dashboard")
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

if start_date > end_date:
    st.error("Start Date must be before End Date.")
    st.stop()

st.markdown("⏳ Fetching stock data...")

# ------------------- FETCH DATA -------------------
@st.cache_data(ttl=600)
def fetch_yahoo_data(ticker: str, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    """Try fetching data from Yahoo Finance"""
    try:
        data = yf.download(ticker, start=start_date, end=end_date + datetime.timedelta(days=1), progress=False)
        # Ensure columns follow the expected names
        # yfinance returns: Open, High, Low, Close, Adj Close, Volume
        return data
    except Exception as e:
        st.warning(f"Yahoo Finance failed: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_alpha_data(ticker: str, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    """
    Fallback: Fetch data from Alpha Vantage using compact outputsize (free tier).
    This returns approx last 100 daily rows. We'll filter it to the requested date range.
    """
    try:
        # Attempt to get the key from Streamlit secrets
        try:
            ALPHA_KEY = st.secrets["general"]["ALPHA_VANTAGE_KEY"]
        except Exception:
            st.error("Alpha Vantage API key not found in st.secrets['general']['ALPHA_VANTAGE_KEY'].")
            return pd.DataFrame()

        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")

        # IMPORTANT: use 'compact' for free tier (last ~100 data points)
        data, _ = ts.get_daily(symbol=ticker, outputsize="compact")

        # Rename columns to match Yahoo style where possible
        data = data.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            }
        )

        # Convert index to datetime and sort
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)

        # Alpha Vantage does not provide 'Adj Close' — create a copy of 'Close' (so downstream code that expects Adj Close won't fail)
        if "Adj Close" not in data.columns and "Close" in data.columns:
            data["Adj Close"] = data["Close"]

        # Filter to requested dates
        filtered = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]

        # If filtered is empty but data exists (because requested range is older), return full data (so caller can decide)
        return filtered if not filtered.empty else data

    except Exception as e:
        # Provide the error text from Alpha Vantage (e.g. premium feature warning) but keep it friendly
        st.error(f"Alpha Vantage failed: {e}")
        return pd.DataFrame()

# Fetch from Yahoo first
data = fetch_yahoo_data(ticker, start_date, end_date)

# If Yahoo fails or returns empty, try Alpha
if data.empty:
    st.warning("⚠️ Yahoo Finance returned no data. Trying Alpha Vantage (free tier: last ~100 days)...")
    data = fetch_alpha_data(ticker, start_date, end_date)

# Stop if no data from both
if data.empty:
    st.error("❌ Failed to fetch data from both Yahoo and Alpha Vantage. Please check the symbol or API key.")
    st.stop()

# If Alpha returned only recent data and it doesn't cover the requested start_date, warn user
try:
    min_date = data.index.date.min()
    if min_date > start_date:
        st.warning(
            f"Note: Data starts at {min_date}. Alpha Vantage (compact) returns only ~100 most recent daily rows on free tier."
        )
except Exception:
    pass

# ------------------- FILTER -------------------
# Ensure the index is timezone-naive datetime date for comparisons
data.index = pd.to_datetime(data.index)
data = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]

if data.empty:
    st.error("No data available for the selected date range after filtering.")
    st.stop()

# ------------------- CLEAN & PREP -------------------
# Ensure numeric columns are floats
for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

# Drop rows where Close is missing (can't compute indicators)
data = data.dropna(subset=["Close"])
if data.empty:
    st.error("Data does not contain valid 'Close' prices after cleaning.")
    st.stop()

# ------------------- INDICATORS -------------------
data["MA20"] = data["Close"].rolling(window=20, min_periods=1).mean()
data["MA50"] = data["Close"].rolling(window=50, min_periods=1).mean()

# RSI (14)
delta = data["Close"].diff()
gain = delta.clip(lower=0)
loss = -delta.clip(upper=0)
# Use Wilder smoothing (EMA of gains/losses)
avg_gain = gain.rolling(window=14, min_periods=14).mean()
avg_loss = loss.rolling(window=14, min_periods=14).mean()
# For the first RSI values, fallback to simple rolling mean if needed
rs = avg_gain / (avg_loss.replace(0, pd.NA))
data["RSI"] = 100 - (100 / (1 + rs))

# MACD
exp1 = data["Close"].ewm(span=12, adjust=False).mean()
exp2 = data["Close"].ewm(span=26, adjust=False).mean()
data["MACD"] = exp1 - exp2
data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()

# ------------------- PRICE CHART -------------------
st.markdown("### 💹 Price Chart with Moving Averages")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", line=dict(color="blue")))
if "MA20" in data.columns:
    fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20", line=dict(color="orange", dash="dot")))
if "MA50" in data.columns:
    fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50", line=dict(color="green", dash="dot")))
fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

# ------------------- RSI -------------------
st.markdown("### 📊 RSI Indicator")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI", line=dict(color="purple")))
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

# ------------------- EXTRA: Download CSV -------------------
st.markdown("### 💾 Download data")
csv = data.to_csv(index=True)
st.download_button(label="Download CSV", data=csv, file_name=f"{ticker}_data_{start_date}_{end_date}.csv", mime="text/csv")
