import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, get_rolling_mean, get_differencing_order,
    scaling, evaluate_model, get_forecast, inverse_scaling
)
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📈 Stock Prediction",
    page_icon="💹",
    layout="wide",
)

st.title("📈 Stock Prediction")

# -------------------------------
# User input
# -------------------------------
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input("🔎 Stock Ticker", "AAPL")

if ticker:
    st.subheader(f"🔮 Predicting Next 30 Days Close Price for: {ticker}")

    # -------------------------------
    # Fetch & process data
    # -------------------------------
    try:
        @st.cache_data(ttl=3600)
        def fetch_data(ticker):
            return get_data(ticker)

        close_price = fetch_data(ticker)
        rolling_price = get_rolling_mean(close_price)
        differencing_order = get_differencing_order(rolling_price)
        scaled_data, scaler = scaling(rolling_price)

        # -------------------------------
        # Compute RMSE
        # -------------------------------
        rmse = evaluate_model(rolling_price, differencing_order)
        st.write(f"📊 **Model RMSE Score:** {rmse:.2f}")

        # -------------------------------
        # Forecast next 30 days
        # -------------------------------
        forecast = get_forecast(rolling_price, differencing_order)
        forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
        st.write("🗓️ ##### Forecast Data (Next 30 Days)")
        st.plotly_chart(
            plotly_table(forecast.sort_index().round(3)),
            use_container_width=True
        )

        # -------------------------------
        # Combined chart with rolling mean
        # -------------------------------
        combined = pd.concat([rolling_price, forecast])
        combined['MA7'] = combined['Close'].rolling(7).mean()
        st.plotly_chart(
            Moving_average_forecast(combined.iloc[-150:]),
            use_container_width=True
        )

    except Exception as e:
        st.warning("⚠️ Could not fetch data or compute forecast. Please check ticker or try again later.")
