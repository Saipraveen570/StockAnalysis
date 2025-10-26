import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD, Moving_average_forecast

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="📊 Stock Analysis",
    page_icon="💹",
    layout="wide"
)

st.title("📊 Stock Analysis & Prediction")

# -------------------------------
# Inputs
# -------------------------------
col1, col2, col3 = st.columns(3)
today = datetime.today().date()

with col1:
    ticker = st.text_input("🔎 Stock Ticker", "AAPL").upper()
with col2:
    start_date = st.date_input("📅 Start Date", datetime(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

# -------------------------------
# Fetch Company Info
# -------------------------------
@st.cache_data(ttl=3600)
def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        return stock.info
    except Exception:
        return {}

info = get_stock_info(ticker)

st.subheader(f"🏢 {ticker} Overview")
st.write(info.get("longBusinessSummary", "No summary available"))
st.write("💼 Sector:", info.get("sector", "N/A"))
st.write("👥 Full Time Employees:", info.get("fullTimeEmployees", "N/A"))
st.write("🌐 Website:", info.get("website", "N/A"))

# -------------------------------
# Metrics Tables
# -------------------------------
col1, col2 = st.columns(2)
with col1:
    df1 = pd.DataFrame(index=["Market Cap","Beta","EPS","PE Ratio"])
    df1["Value"] = [info.get("marketCap"), info.get("beta"), info.get("trailingEps"), info.get("trailingPE")]
    st.plotly_chart(plotly_table(df1), use_container_width=True)
with col2:
    df2 = pd.DataFrame(index=["Quick Ratio","Revenue per share","Profit Margins","Debt to Equity","Return on Equity"])
    df2["Value"] = [info.get("quickRatio"), info.get("revenuePerShare"), info.get("profitMargins"), info.get("debtToEquity"), info.get("returnOnEquity")]
    st.plotly_chart(plotly_table(df2), use_container_width=True)

# -------------------------------
# Historical Data
# -------------------------------
@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end)
        if data.empty:
            return pd.DataFrame()
        return data
    except Exception:
        return pd.DataFrame()

data = get_stock_data(ticker, start_date, end_date)

if data.empty:
    st.warning("❌ No historical data available. Check ticker or dates.")
else:
    # Daily Metrics
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2] if len(data['Close']) > 1 else last_close
    change = last_close - prev_close
    pct_change = (change / prev_close * 100) if prev_close else 0
    last_volume = data['Volume'].iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Daily Close", f"${last_close:.2f}", f"{change:.2f}")
    col2.metric("📉 % Change", f"{pct_change:.2f}%")
    col3.metric("📊 Volume", f"{int(last_volume):,}")

    # Historical Table
    st.write("🗂️ Historical Data (Last 10 days)")
    data.index = [str(i)[:10] for i in data.index]
    st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

# -------------------------------
# Chart Controls
# -------------------------------
st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

# Period Buttons
periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
col_buttons = st.columns(len(periods))
num_period = ''
for i, p in enumerate(periods):
    if col_buttons[i].button(f"{p}"):
        num_period = p.lower()
if num_period == '':
    num_period = '1y'

# Chart type & indicators
col1, col2 = st.columns([1,1])
with col1:
    chart_type = st.selectbox("📊 Chart Type", ("Candle", "Line"))
with col2:
    if chart_type == "Candle":
        indicators = st.selectbox("📈 Indicator", ("RSI","MACD"))
    else:
        indicators = st.selectbox("📈 Indicator", ("RSI","Moving Average","MACD"))

# RSI window slider
rsi_window = st.slider("🔧 Select RSI Window (days)", 5, 50, 14)

df_history = yf.Ticker(ticker).history(period="max")

# -------------------------------
# Chart Rendering
# -------------------------------
if chart_type == "Candle":
    st.plotly_chart(candlestick(df_history, num_period), use_container_width=True)
    if indicators == "RSI":
        st.plotly_chart(RSI(df_history, num_period, window=rsi_window), use_container_width=True)
    elif indicators == "MACD":
        st.plotly_chart(MACD(df_history, num_period), use_container_width=True)
else:
    if indicators == "RSI":
        st.plotly_chart(close_chart(df_history, num_period), use_container_width=True)
        st.plotly_chart(RSI(df_history, num_period, window=rsi_window), use_container_width=True)
    elif indicators == "Moving Average":
        st.plotly_chart(Moving_average(df_history, num_period), use_container_width=True)
    elif indicators == "MACD":
        st.plotly_chart(close_chart(df_history, num_period), use_container_width=True)
        st.plotly_chart(MACD(df_history, num_period), use_container_width=True)

# -------------------------------
# Forecasting Section
# -------------------------------
st.subheader("🔮 Forecast Next 30 Days (Linear Regression + 7-day MA)")

@st.cache_data(ttl=3600)
def forecast_prices(data):
    if data.empty:
        return pd.DataFrame()
    close_price = data['Close'].reset_index(drop=True)
    rolling_price = close_price.rolling(7).mean().dropna()
    X = np.arange(len(rolling_price)).reshape(-1,1)
    y = rolling_price.values
    model = LinearRegression()
    model.fit(X, y)
    future_days = np.arange(len(rolling_price), len(rolling_price)+30).reshape(-1,1)
    pred = model.predict(future_days)
    forecast_index = pd.date_range(start=datetime.today(), periods=30)
    return pd.DataFrame(pred, index=forecast_index, columns=["Close"])

forecast_df = forecast_prices(data)
if not forecast_df.empty:
    st.write("Forecast Table:")
    st.plotly_chart(plotly_table(forecast_df.round(2)), use_container_width=True)

    combined = pd.concat([data['Close'].rolling(7).mean(), forecast_df])
    st.plotly_chart(Moving_average_forecast(combined.tail(150)), use_container_width=True)
