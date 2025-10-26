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
    page_title="📊 Stock Analysis & Prediction",
    page_icon="📈",
    layout="wide"
)
st.title("📈 Stock Analysis & Prediction")

# -------------------------------
# Inputs
# -------------------------------
col1, col2, col3 = st.columns(3)
today = datetime.today().date()

with col1:
    ticker = st.text_input("🏦 Stock Ticker", "AAPL").upper()
with col2:
    start_date = st.date_input("📅 Start Date", datetime(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

# -------------------------------
# Fetch Stock Info Safely
# -------------------------------
@st.cache_data(ttl=3600)
def get_stock_info(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return info
    except Exception:
        return {}

@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end)
        if data.empty:
            return pd.DataFrame()
        return data
    except Exception:
        return pd.DataFrame()

# -------------------------------
# Display Summary
# -------------------------------
info = get_stock_info(ticker)
if info:
    st.subheader(f"🏢 {ticker} Overview")
    st.write(info.get("longBusinessSummary", "No summary available"))
    st.write("**🌐 Website:**", info.get("website", "N/A"))
    st.write("**🏭 Sector:**", info.get("sector", "N/A"))
    st.write("**👥 Full-Time Employees:**", info.get("fullTimeEmployees", "N/A"))

    col1, col2 = st.columns(2)
    with col1:
        df1 = pd.DataFrame(index=["Market Cap", "Beta", "EPS", "PE Ratio"])
        df1[""] = [
            info.get("marketCap", "N/A"),
            info.get("beta", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("trailingPE", "N/A")
        ]
        st.plotly_chart(plotly_table(df1), use_container_width=True)
    with col2:
        df2 = pd.DataFrame(index=["Quick Ratio", "Revenue per Share", "Profit Margins", "Debt to Equity", "Return on Equity"])
        df2[""] = [
            info.get("quickRatio", "N/A"),
            info.get("revenuePerShare", "N/A"),
            info.get("profitMargins", "N/A"),
            info.get("debtToEquity", "N/A"),
            info.get("returnOnEquity", "N/A")
        ]
        st.plotly_chart(plotly_table(df2), use_container_width=True)
else:
    st.info("⚠️ Could not load company summary. Try again later.")

# -------------------------------
# Historical Stock Data
# -------------------------------
data = get_stock_data(ticker, start_date, end_date)
if data.empty:
    st.warning("⚠️ No historical data available. Check ticker or dates.")
else:
    # Metrics
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2] if len(data['Close']) > 1 else last_close
    change = last_close - prev_close
    pct_change = (change / prev_close) * 100 if prev_close else 0
    last_volume = data['Volume'].iloc[-1]

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Last Close", f"${last_close:,.2f}")
    col2.metric("📉 % Change", f"{pct_change:.2f}%")
    col3.metric("📊 Volume", f"{int(last_volume):,}")

    # Recent 10-day table
    st.subheader("🗓️ Recent 10-Day Data")
    data.index = [str(i)[:10] for i in data.index]
    fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
    fig_tail.update_layout(height=220)
    st.plotly_chart(fig_tail, use_container_width=True)

# -------------------------------
# Forecasting: Linear Regression + 7-day MA
# -------------------------------
st.subheader("🔮 Forecast Next 30 Days")

@st.cache_data(ttl=3600)
def forecast_prices(data):
    if data.empty:
        return pd.DataFrame()
    close_price = data['Close'].reset_index(drop=True)
    rolling_price = close_price.rolling(window=7).mean().dropna()
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
    fig_forecast = plotly_table(forecast_df.round(2))
    fig_forecast.update_layout(height=220)
    st.plotly_chart(fig_forecast, use_container_width=True)

    # Combined Plot: Historical + Forecast
    combined = pd.concat([data['Close'].rolling(7).mean(), forecast_df])
    st.plotly_chart(Moving_average_forecast(combined.tail(150)), use_container_width=True)
