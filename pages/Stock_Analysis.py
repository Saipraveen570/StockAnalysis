import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from statsmodels.tsa.statespace.sarimax import SARIMAX
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="Stock Analysis", layout="wide")

# ========= Styling =========
st.markdown("""
<style>
.metric-card {
    background-color: #1e1e1e;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #444;
}
</style>
""", unsafe_allow_html=True)

# ========= Functions =========
@st.cache_data(show_spinner=False)
def load_data(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end)
        if data.empty:
            return None
        data["Return"] = data["Close"].pct_change()
        return data
    except:
        return None

def safe_number(x):
    try:
        return round(float(x), 2)
    except:
        return 0.0

# ========= Sidebar =========
st.sidebar.header("Stock Selection")
ticker = st.sidebar.text_input("Ticker Symbol", "AAPL")
start = st.sidebar.date_input("Start Date", datetime(2023, 1, 1))
end = st.sidebar.date_input("End Date", datetime.today())

# ========= Page Header =========
st.title("📊 Stock Market Analysis Dashboard")
st.write("Analyze historical performance, price trends, and forecast movements.")

# ========= Load Data =========
data = load_data(ticker.upper(), start, end)

if data is None:
    st.error("Invalid ticker or no data available. Try another symbol.")
    st.stop()

# ========= KPI Metrics =========
latest = data["Close"].iloc[-1]
prev = data["Close"].iloc[-2]
daily_change = safe_number(latest - prev)
pct_change = safe_number((daily_change / prev) * 100)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Price", f"${safe_number(latest)}", f"{pct_change}%")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Daily Change", f"${daily_change}")
    st.markdown("</div>", unsafe_allow_html=True)

with col3:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.metric("Volatility", f"{safe_number(np.std(data['Return']) * 100)}%")
    st.markdown("</div>", unsafe_allow_html=True)

# ========= Charts =========
st.subheader("📈 Price Chart with Moving Averages")

data["MA20"] = data["Close"].rolling(window=20).mean()
data["MA50"] = data["Close"].rolling(window=50).mean()

fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index, open=data['Open'], high=data['High'],
    low=data['Low'], close=data['Close'], name='Price'
))
fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], mode="lines", name="MA20"))
fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], mode="lines", name="MA50"))
fig.update_layout(height=450, template="plotly_dark", xaxis_rangeslider_visible=False)

st.plotly_chart(fig, use_container_width=True)

# ========= Volume =========
st.subheader("📊 Volume Analysis")
vol_fig = px.bar(data, x=data.index, y="Volume")
vol_fig.update_layout(template="plotly_dark", height=300)
st.plotly_chart(vol_fig, use_container_width=True)

# ========= Forecasting =========
st.subheader("📉 Forecast Prices (SARIMAX)")

if st.button("Run Forecast Model"):
    try:
        model = SARIMAX(data["Close"], order=(1, 1, 1), seasonal_order=(1,1,1,12))
        result = model.fit(disp=False)
        forecast = result.forecast(steps=15)
        forecast_fig = px.line(forecast, title="15-Day Forecast", labels={"index": "Date", "value": "Price"})
        forecast_fig.update_layout(template="plotly_dark")
        st.plotly_chart(forecast_fig, use_container_width=True)
    except Exception:
        st.error("Forecasting failed due to insufficient data or model instability.")

# ========= Raw Data Toggle =========
with st.expander("View Raw Data"):
    st.dataframe(data.tail())
