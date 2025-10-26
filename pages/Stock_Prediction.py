import streamlit as st
import pandas as pd
from pages.utils.model_train import get_data, get_rolling_mean, get_differencing_order, scaling, evaluate_model, get_forecast, inverse_scaling
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📈 Stock Prediction",
    page_icon="📊",
    layout="wide",
)

st.title("📈 Stock Prediction")

# -------------------------------
# User input
# -------------------------------
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input("🔎 Stock Ticker", "AAPL")

st.subheader(f"Predicting Next 30 days Close Price for: {ticker}")

# -------------------------------
# Data & Model
# -------------------------------
close_price = get_data(ticker)
rolling_price = get_rolling_mean(close_price)
differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)
rmse = evaluate_model(scaled_data, differencing_order)

st.write("⚙️ **Model RMSE Score:**", rmse)

forecast = get_forecast(scaled_data, differencing_order)
forecast["Close"] = inverse_scaling(scaler, forecast["Close"])

st.write("🗓️ ##### Forecast Data (Next 30 days)")
fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

# Combine historical + forecast for chart
forecast_full = pd.concat([rolling_price, forecast])
st.plotly_chart(Moving_average_forecast(forecast_full.iloc[150:]), use_container_width=True)
