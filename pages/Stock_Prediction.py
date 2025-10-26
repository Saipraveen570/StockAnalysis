import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, get_rolling_mean, get_differencing_order, scaling,
    evaluate_model, get_forecast, inverse_scaling
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📈 Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Prediction")

# -------------------------------
# User input
# -------------------------------
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input('🔎 Stock Ticker', 'AAPL')

st.subheader(f"🔮 Predicting Next 30 Days Close Price for: {ticker}")

# -------------------------------
# Fetch and prepare data
# -------------------------------
try:
    close_price = get_data(ticker)
    if close_price.empty:
        st.warning("❌ Could not fetch stock data. Please enter a valid ticker.")
    else:
        rolling_price = get_rolling_mean(close_price)

        differencing_order = get_differencing_order(rolling_price)
        scaled_data, scaler = scaling(rolling_price)
        rmse = evaluate_model(scaled_data, differencing_order)

        st.write(f"🤖 **Model RMSE Score:** {rmse}")

        forecast = get_forecast(scaled_data, differencing_order)
        forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

        # -------------------------------
        # Forecast Table
        # -------------------------------
        st.write('🗂️ Forecast Data (Next 30 days)')
        fig_table = plotly_table(forecast.sort_index(ascending=True).round(3))
        fig_table.update_layout(height=220)
        st.plotly_chart(fig_table, use_container_width=True)

        # -------------------------------
        # Combine historic + forecast for chart
        # -------------------------------
        combined = pd.concat([rolling_price, forecast])
        if len(combined) > 150:
            st.plotly_chart(Moving_average_forecast(combined.iloc[-150:]), use_container_width=True)
        else:
            st.plotly_chart(Moving_average_forecast(combined), use_container_width=True)

except Exception as e:
    st.warning("⚠️ Could not process stock prediction. Please try again later.")
