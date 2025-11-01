import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
import datetime as dt
import time
import os

from model_train import get_data, train_model, forecast  # ✅ Import your functions

st.set_page_config(page_title="📈 Stock Price Prediction", layout="wide")

# -----------------------------------------------------------
# 🔹 UI Section
# -----------------------------------------------------------
st.title("🤖 Stock Price Prediction Dashboard")

ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL")
start_date = st.date_input("Start Date", dt.date(2023, 1, 1))
end_date = st.date_input("End Date", dt.date.today())

st.divider()

# -----------------------------------------------------------
# 📊 Fetch Data (with fallback to Alpha Vantage)
# -----------------------------------------------------------
with st.spinner("⏳ Fetching stock data..."):
    df = get_data(ticker)

if df.empty:
    st.warning("⚠️ Yahoo Finance failed. Trying Alpha Vantage...")
    try:
        ALPHA_KEY = st.secrets["general"]["ALPHA_VANTAGE_KEY"]
        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        df, _ = ts.get_daily(symbol=ticker, outputsize="full")

        df = df.rename(columns={
            "1. open": "Open",
            "2. high": "High",
            "3. low": "Low",
            "4. close": "Close",
            "5. volume": "Volume"
        })
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)

        if not df.empty:
            st.success("✅ Data source: Alpha Vantage")
    except Exception as e:
        st.error(f"❌ Failed to fetch data from both Yahoo & Alpha Vantage: {e}")
        st.stop()

# -----------------------------------------------------------
# 📈 Display Historical Chart
# -----------------------------------------------------------
st.subheader(f"📉 Historical Price Chart: {ticker}")

fig = go.Figure(data=[go.Candlestick(
    x=df.index,
    open=df["Open"],
    high=df["High"],
    low=df["Low"],
    close=df["Close"]
)])
fig.update_layout(title=f"{ticker} Candlestick Chart", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------
# 🧠 Model Training and Forecasting
# -----------------------------------------------------------
st.divider()
st.subheader("🧠 Training SARIMAX Model...")

with st.spinner("Training the model..."):
    model, scaler = train_model(df)

if model is None:
    st.error("Model training failed. Please check your dataset.")
    st.stop()

# Forecast Next 30 Days
future_days = 30
pred = forecast(model, scaler, steps=future_days)

if len(pred) == 0:
    st.error("Forecasting failed.")
    st.stop()

# -----------------------------------------------------------
# 📅 Display Forecast Chart
# -----------------------------------------------------------
st.subheader(f"🔮 {future_days}-Day Price Forecast for {ticker}")

future_dates = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=future_days)
forecast_df = pd.DataFrame({"Date": future_dates, "Predicted_Price": pred})

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df.index, y=df["Close"], name="Historical Close", line=dict(color="blue")))
fig2.add_trace(go.Scatter(x=forecast_df["Date"], y=forecast_df["Predicted_Price"], name="Predicted", line=dict(color="orange", dash="dash")))
fig2.update_layout(title="Stock Price Forecast", xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------------------------------
# 📋 Show Forecast Table
# -----------------------------------------------------------
st.subheader("📋 Forecasted Prices (Next 30 Days)")
st.dataframe(forecast_df.set_index("Date"))
