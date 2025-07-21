import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from pages.utils.model_train import (
    get_data,
    get_rolling_mean,
    get_differencing_order,
    scaling,
    evaluate_model,
    get_forecast,
    inverse_scaling
)

from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Prediction")

# User input
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')

st.subheader(f'Predicting Next 30 Days Close Price for: {ticker}')

# Load and preprocess data
@st.cache_data
def load_data(ticker):
    close_price = get_data(ticker)
    rolling_price = get_rolling_mean(close_price)
    return close_price, rolling_price

close_price, rolling_price = load_data(ticker)

# Reduce dataset for faster model training
rolling_price = rolling_price[-365:]

# Model preparation
differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)

# Evaluate and train
rmse = evaluate_model(scaled_data, differencing_order)
st.write("**Model RMSE Score:**", round(rmse, 4))

# Forecast
forecast = get_forecast(scaled_data, differencing_order)
forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

# Display forecast table
st.write('##### Forecast Data (Next 30 Days)')
fig_tail = plotly_table(forecast.sort_index().round(3))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

# Combine and visualize
forecast_combined = pd.concat([rolling_price, forecast])
st.plotly_chart(Moving_average_forecast(forecast_combined.iloc[150:]), use_container_width=True)
