import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, get_rolling_mean, get_differencing_order,
    scaling, evaluate_model, get_forecast, inverse_scaling
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Prediction")

col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input('Enter Stock Ticker Symbol', 'AAPL')

# Define cached functions for performance
@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    return get_data(ticker)

@st.cache_data(ttl=3600)
def prepare_data(close_price):
    rolling = get_rolling_mean(close_price)
    order = get_differencing_order(rolling)
    scaled, scaler = scaling(rolling)
    return rolling, order, scaled, scaler

@st.cache_data(ttl=3600)
def run_prediction_model(scaled, order):
    rmse = evaluate_model(scaled, order)
    forecast = get_forecast(scaled, order)
    return rmse, forecast

if st.button("🔍 Run Forecast"):
    with st.spinner("Running prediction model..."):

        # Step 1: Data
        close_price = fetch_stock_data(ticker)
        rolling_price, diff_order, scaled_data, scaler = prepare_data(close_price)

        # Step 2: Model
        rmse, forecast = run_prediction_model(scaled_data, diff_order)

        # Step 3: Inverse scaling forecast
        forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

        # Display RMSE
        st.markdown(f"### 📊 Model RMSE Score: `{rmse:.3f}`")

        # Display Forecast Table
        st.markdown("#### 📅 30-Day Forecast Table")
        forecast_sorted = forecast.sort_index(ascending=True).round(3)
        fig_table = plotly_table(forecast_sorted.tail(30))
        fig_table.update_layout(height=220)
        st.plotly_chart(fig_table, use_container_width=True)

        # Merge with historical for charting
        forecast_full = pd.concat([rolling_price, forecast])

        # Plot Moving Average Forecast
        st.markdown("#### 🔮 Forecast Chart")
        st.plotly_chart(Moving_average_forecast(forecast_full.iloc[150:]), use_container_width=True)

    st.success("Prediction Complete ✅")
