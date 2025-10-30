import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta

st.set_page_config(page_title="Stock Analysis", layout="wide")

# =========================
# Cached Data Loader (Robust)
# =========================
@st.cache_data(ttl=3600)
def load_data(symbol: str):
    symbol = symbol.strip().upper()
    
    # Crypto support auto format
    if "-" in symbol and not symbol.endswith("USD"):
        yahoo_symbols = [symbol, symbol.replace("-", "") + "-USD"]
    else:
        # Stock: Try direct + .NS fallback
        yahoo_symbols = [symbol]
        if "." not in symbol:
            yahoo_symbols.append(symbol + ".NS")
    
    for s in yahoo_symbols:
        try:
            ticker = yf.Ticker(s)
            df = ticker.history(period="5y", timeout=15)

            if df is not None and not df.empty:
                df.index = pd.to_datetime(df.index)
                return df
        except Exception:
            continue
    
    return None

# =========================
# Slice Period Function
# =========================
def slice_period(df, period):
    if df is None or df.empty:
        return df

    if period == "1M":
        return df.tail(21)
    if period == "6M":
        return df.tail(126)
    if period == "1Y":
        return df.tail(252)
    if period == "YTD":
        return df[df.index.year == pd.Timestamp.today().year]
    return df

# =========================
# Indicators
# =========================
@st.cache_data
def compute_indicators(df):
    df = df.copy()
    df["MA20"] = df["Close"].rolling(20).mean()
    df["MA50"] = df["Close"].rolling(50).mean()

    rsi = ta.momentum.RSIIndicator(df["Close"], window=14)
    df["RSI"] = rsi.rsi()

    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()

    return df.fillna(method="bfill").fillna(method="ffill")

# =========================
# Chart Functions
# =========================
def plot_price(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], mode="lines", name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], mode="lines", name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], mode="lines", name="MA50"))
    fig.update_layout(title="Price Chart (MA20 & MA50)", template="plotly_white", height=350)
    return fig

def plot_candles(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]
    )])
    fig.update_layout(title="Candlestick Chart", template="plotly_white", height=350)
    return fig

def plot_rsi(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"))
    fig.add_hline(y=70, line=dict(dash="dot"))
    fig.add_hline(y=30, line=dict(dash="dot"))
    fig.update_layout(title="RSI Indicator", template="plotly_white", height=250)
    return fig

def plot_macd(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal"))
    fig.update_layout(title="MACD Indicator", template="plotly_white", height=250)
    return fig

# =========================
# UI
# =========================
st.title("Stock & Crypto Analysis Dashboard")

ticker = st.text_input("Enter Ticker (Examples: AAPL, TSLA, RELIANCE, BTC-USD)", "").strip().upper()

if not ticker:
    st.info("Enter a stock/crypto symbol to begin")
    st.stop()

with st.spinner("Fetching market data..."):
    df = load_data(ticker)

if df is None or df.empty:
    st.error("Invalid symbol or data unavailable. Try: AAPL, TSLA, RELIANCE, BTC-USD")
    st.stop()

df = compute_indicators(df)

# Time Range Selector
period = st.radio("Select Time Range:", ["1M", "6M", "1Y", "YTD", "MAX"], horizontal=True)
df_period = slice_period(df, period)

if df_period is None or df_period.empty:
    st.warning("Not enough data for selected period")
    st.stop()

# Metrics
latest = df_period["Close"].iloc[-1]
prev = df_period["Close"].iloc[-2] if len(df_period) > 1 else latest
daily_change = latest - prev
pct_change = (daily_change / prev) * 100 if prev != 0 else 0

volume = df_period["Volume"].iloc[-1] if "Volume" in df_period.columns else 0

c1, c2, c3 = st.columns(3)
c1.metric("Current Price", f"{latest:.2f}", f"{daily_change:.2f}")
c2.metric("Daily % Change", f"{pct_change:.2f}%")
c3.metric("Volume", f"{int(volume):,}")

# Charts
st.plotly_chart(plot_price(df_period), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_candles(df_period), use_container_width=True)
with col2:
    st.plotly_chart(plot_rsi(df_period), use_container_width=True)

st.plotly_chart(plot_macd(df_period), use_container_width=True)
