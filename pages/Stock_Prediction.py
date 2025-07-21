import streamlit as st
from pages.utils.model_train import (
    get_data, get_rolling_mean,
    get_differencing_order, scaling,
    evaluate_model, get_forecast, inverse_scaling
)
from pages.utils.plotly_figure import plot_forecast

st.set_page_config(page_title="📈 Stock Prediction", layout="centered")

st.title("📈 Stock Prediction")

# Input section
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL):", "AAPL")

if ticker:
    close_data = get_data(ticker.upper())

    if close_data.empty:
        st.error("⚠️ Failed to fetch stock data. Please check the ticker symbol.")
        st.stop()

    st.success(f"✅ Predicting Next 30 Days Close Price for: {ticker.upper()}")

    # Preprocessing
    rolling = get_rolling_mean(close_data)
    differencing_order = get_differencing_order(close_data)
    scaled_data, scaler = scaling(close_data)

    # Model evaluation
    rmse = evaluate_model(scaled_data['Close'], differencing_order)
    st.write(f"📊 **Model RMSE Score**: `{rmse}`")

    # Forecast
    forecast_scaled = get_forecast(scaled_data['Close'], differencing_order)
    if forecast_scaled.empty:
        st.error("🚫 Forecast failed. Try again or use a different ticker.")
        st.stop()

    forecast_unscaled = inverse_scaling(scaler, forecast_scaled)
    forecast_df = forecast_scaled.copy()
    forecast_df['Close'] = forecast_unscaled

    st.subheader("📅 Forecast Data (Next 30 Days)")
    st.dataframe(forecast_df)

    # Plot
    st.plotly_chart(plot_forecast(close_data, forecast_df), use_container_width=True)
