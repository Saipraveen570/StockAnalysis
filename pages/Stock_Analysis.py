import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import joblib
import os
from model_train import get_data, train_model, forecast, load_model

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------
st.set_page_config(page_title="📊 Stock Forecast Dashboard", layout="wide")
st.title("📈 Smart Stock Analysis & Prediction")

# -----------------------------------------------------------
# API CONFIG (safe)
# -----------------------------------------------------------
ALPHA_KEY = st.secrets.get("general", {}).get("ALPHA_VANTAGE_KEY", None)

# -----------------------------------------------------------
# CACHED MODEL STORAGE
# -----------------------------------------------------------
MODEL_CACHE = {}

# -----------------------------------------------------------
# Fetch company info
# -----------------------------------------------------------
@st.cache_data(ttl=3600)
def get_company_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.get_info()
        return info or {}
    except Exception:
        return {}

# -----------------------------------------------------------
# Fallback Alpha Vantage data fetch
# -----------------------------------------------------------
@st.cache_data(ttl=3600)
def get_alpha_data(ticker):
    if not ALPHA_KEY:
        return pd.DataFrame()
    try:
        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        data, _ = ts.get_daily(symbol=ticker, outputsize="full")
        data = data.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)
        return data
    except Exception:
        return pd.DataFrame()

# -----------------------------------------------------------
# INPUTS
# -----------------------------------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, INFY.NS):", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", datetime.date.today() - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date", datetime.date.today())

# -----------------------------------------------------------
# FETCH DATA
# -----------------------------------------------------------
st.info("⏳ Fetching data from Yahoo Finance...")
data = get_data(ticker)

if data.empty:
    st.warning("⚠️ Yahoo Finance failed. Trying Alpha Vantage...")
    data = get_alpha_data(ticker)

if data.empty:
    st.error("❌ Failed to fetch data from both Yahoo and Alpha Vantage. Please check the symbol or API key.")
    st.stop()

# Filter by date range
data = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]

# -----------------------------------------------------------
# INDICATORS
# -----------------------------------------------------------
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

# -----------------------------------------------------------
# PRICE CHART
# -----------------------------------------------------------
st.markdown("### 💹 Price Chart with Moving Averages")
fig = go.Figure()
fig.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Close", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=data.index, y=data["MA20"], name="MA20", line=dict(color="orange", dash="dot")))
fig.add_trace(go.Scatter(x=data.index, y=data["MA50"], name="MA50", line=dict(color="green", dash="dot")))
fig.update_layout(template="plotly_white", xaxis_title="Date", yaxis_title="Price (USD)")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# RSI
# -----------------------------------------------------------
st.markdown("### 📊 RSI Indicator")
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], line=dict(color="purple")))
fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
fig_rsi.update_layout(template="plotly_white", yaxis_title="RSI (14)")
st.plotly_chart(fig_rsi, use_container_width=True)

# -----------------------------------------------------------
# MACD
# -----------------------------------------------------------
st.markdown("### 📉 MACD Indicator")
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD", line=dict(color="blue")))
fig_macd.add_trace(go.Scatter(x=data.index, y=data["Signal"], name="Signal", line=dict(color="orange")))
fig_macd.update_layout(template="plotly_white", yaxis_title="MACD")
st.plotly_chart(fig_macd, use_container_width=True)

# -----------------------------------------------------------
# FORECASTING SECTION (with auto-cache)
# -----------------------------------------------------------
st.markdown("### 🔮 30-Day Price Forecast")

if ticker in MODEL_CACHE:
    model, scaler = MODEL_CACHE[ticker]
else:
    model, scaler = load_model(ticker)
    if model is None:
        st.info("🧠 Training SARIMAX model... please wait (~20 sec)...")
        model, scaler = train_model(data)
        if model:
            joblib.dump(model, f"{ticker}_model.pkl")
            joblib.dump(scaler, f"{ticker}_scaler.pkl")
    MODEL_CACHE[ticker] = (model, scaler)

if model:
    pred = forecast(model, scaler, steps=30)
    if len(pred) > 0:
        future_dates = pd.date_range(data.index[-1] + pd.Timedelta(days=1), periods=30)
        forecast_df = pd.DataFrame({"Date": future_dates, "Forecast": pred})
        st.success("✅ Forecast generated successfully!")

        # Plot forecast
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=data.index, y=data["Close"], name="Historical", line=dict(color="blue")))
        fig_forecast.add_trace(go.Scatter(x=forecast_df["Date"], y=forecast_df["Forecast"],
                                          name="Forecast", line=dict(color="red", dash="dot")))
        fig_forecast.update_layout(template="plotly_white", yaxis_title="Price (USD)", xaxis_title="Date")
        st.plotly_chart(fig_forecast, use_container_width=True)
    else:
        st.warning("⚠️ Forecast could not be generated.")
else:
    st.error("❌ Model training failed. Try again later.")

# -----------------------------------------------------------
# SNAPSHOT
# -----------------------------------------------------------
st.markdown("### 📈 Latest Data Snapshot")
st.dataframe(data.tail(1).T.round(2), use_container_width=True)
