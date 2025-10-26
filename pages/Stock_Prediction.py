# pages/Stock_Prediction.py
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
from utils.model_train import get_data, get_rolling_mean, scaling, evaluate_model, get_forecast, inverse_scaling
from utils.plotly_figure import plotly_table, Moving_average_forecast

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📊 Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📊 Stock Prediction")

# -------------------------------
# User input
# -------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input('🔎 Stock Ticker', 'AAPL')

st.subheader(f'🔮 Predicting Next 30 days Close Price for: {ticker}')

# -------------------------------
# Model & Forecast
# -------------------------------
try:
    close_price = get_data(ticker)
    rolling_price = get_rolling_mean(close_price)
    scaled_data, scaler = scaling(rolling_price)
    rmse = evaluate_model(scaled_data)
    st.write("🧮 **Model RMSE Score:**", rmse)

    forecast = get_forecast(scaled_data)
    forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

    st.write('📄 ##### Forecast Data (Next 30 days)')
    fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
    fig_tail.update_layout(height=220)
    st.plotly_chart(fig_tail, use_container_width=True)

    # Merge historical + forecast for chart
    forecast_full = pd.concat([rolling_price, forecast])
    st.plotly_chart(Moving_average_forecast(forecast_full.iloc[150:]), use_container_width=True)

except Exception:
    st.warning("⚠️ Could not load prediction data. Check the stock ticker or try again later.")
