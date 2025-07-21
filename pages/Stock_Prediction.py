import streamlit as st
from pages.utils.model_train import (
    get_data, get_rolling_mean, get_differencing_order, 
    scaling, evaluate_model, get_forecast, inverse_scaling
)
import pandas as pd
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Prediction")

# --- UI ---
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')

st.subheader(f'🔮 Predicting Next 30 Days Close Price for: {ticker}')

# --- Cached Data Fetching ---
@st.cache_data(show_spinner="Fetching stock data...")
def fetch_data(ticker):
    return get_data(ticker)

@st.cache_data(show_spinner="Calculating rolling mean...")
def process_rolling_mean(close_price):
    return get_rolling_mean(close_price)

# --- Cached Model Evaluation ---
@st.cache_resource(show_spinner="Training model...")
def train_model(rolling_price):
    differencing_order = get_differencing_order(rolling_price)
    scaled_data, scaler = scaling(rolling_price)
    rmse = evaluate_model(scaled_data, differencing_order)
    forecast = get_forecast(scaled_data, differencing_order)
    return rmse, forecast, scaler, differencing_order, scaled_data

# --- Data Pipeline ---
close_price = fetch_data(ticker)
rolling_price = process_rolling_mean(close_price)

# --- Model Training ---
rmse, forecast, scaler, differencing_order, scaled_data = train_model(rolling_price)

# --- Display RMSE ---
st.write("📊 **Model RMSE Score:**", rmse)

# --- Inverse Scale Forecast ---
forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

# --- Forecast Table ---
st.write('🗓️ **Forecast Data (Next 30 days)**')
fig_tail = plotly_table(forecast.sort_index().round(2))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

# --- Combined Plot ---
full_data = pd.concat([rolling_price, forecast])
st.plotly_chart(Moving_average_forecast(full_data.tail(150)), use_container_width=True)
