import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta

st.set_page_config(page_title="Stock Insight & Forecast Console", layout="wide")

# =========================
# Modern UI CSS
# =========================
st.markdown("""
<style>
body { font-family: 'Inter', sans-serif; }
.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #444;
    backdrop-filter: blur(8px);
    margin-bottom: 12px;
}
.chart-container {
    border: 1px solid #3A3A3A;
    padding: 14px;
    border-radius: 10px;
    background: #1e1e1e;
    margin-top: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Title
# =========================
st.title("📊 Stock Insight & Forecast Console")
st.markdown("Real-time performance, trend indicators & actionable metrics.")
st.divider()

# =========================
# Data Fetch with Fallback
# =========================
@st.cache_data(ttl=3600)
def load_data(symbol: str):
    symbol = symbol.upper().strip()

    if "." not in symbol:
        yahoo_symbol = symbol + ".NS"
    else:
        yahoo_symbol = symbol

    for s in [symbol, yahoo_symbol]:
        try:
            df = yf.download(s, period="5y", progress=False)
            if df is not None and not df.empty:
                return df
        except Exception:
            continue
    return None

# =========================
# Technical Indicators
# =========================
@st.cache_data
def add_indicators(df):
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
# Charts
# =========================
def price_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Close"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA20"], name="MA20"))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50"))
    fig.update_layout(title="Price & Moving Averages", template="plotly_dark", height=340)
    return fig

def candle(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"]
    )])
    fig.update_layout(template="plotly_dark", title="Candlestick Chart", height=340)
    return fig

def rsi_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"))
    fig.add_hline(y=70, line_dash="dot")
    fig.add_hline(y=30, line_dash="dot")
    fig.update_layout(template="plotly_dark", title="RSI", height=240)
    return fig

def macd_chart(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"))
    fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal"))
    fig.update_layout(template="plotly_dark", title="MACD", height=240)
    return fig

# =========================
# UI Input
# =========================
col1, col2 = st.columns([3,1])
symbol = col1.text_input("Enter Stock Symbol", value="AAPL")
run = col2.button("Analyze", use_container_width=True)

if not run:
    st.info("Enter a stock symbol and click Analyze.")
    st.stop()

# =========================
# Load Data
# =========================
with st.spinner("Fetching data..."):
    df = load_data(symbol)

if df is None or df.empty:
    st.error("Invalid symbol or data unavailable. Try: AAPL, TSLA, RELIANCE, TCS, INFY")
    st.stop()

df = add_indicators(df)

# =========================
# Metrics Calculation
# =========================
latest = df["Close"].iloc[-1]
prev = df["Close"].iloc[-2]
daily_change = latest - prev
pct_change = (daily_change / prev) * 100

def metric_card(title, value, change):
    color = "green" if change >= 0 else "red"
    st.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
        <p style="color:{color}; font-weight:600">Δ {round(change,2)}</p>
    </div>
    """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
metric_card("Current Price", f"{latest:.2f}", daily_change)
metric_card("Daily % Change", f"{pct_change:.2f}%", pct_change)
metric_card("Volume", f"{df['Volume'].iloc[-1]:,}", 0)

# =========================
# Charts Display
# =========================
st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.plotly_chart(price_chart(df), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

colA, colB = st.columns(2)
with colA:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(candle(df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with colB:
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.plotly_chart(rsi_chart(df), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
st.plotly_chart(macd_chart(df), use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)
