import streamlit as st
import pandas as pd
import numpy as np
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

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📊 Stock Prediction",
    page_icon="💹",
    layout="wide",
)

st.title("📊 Stock Prediction")

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
    close_price = get_data(ticker)
    rolling_price = get_rolling_mean(close_price)
    differencing_order = get_differencing_order(rolling_price)
    scaled_data, scaler = scaling(rolling_price)

    # -------------------------------
    # Compute dynamic RMSE
    # -------------------------------
    # Fix for AttributeError: ensure arrays are compatible
    def safe_rmse(df_scaled, pred):
        y_true = df_scaled.values.flatten() if hasattr(df_scaled, "values") else np.array(df_scaled).flatten()
        y_pred = pred.flatten() if hasattr(pred, "flatten") else np.array(pred).flatten()
        return np.sqrt(np.mean((y_true - y_pred) ** 2))

    rmse = safe_rmse(scaled_data, evaluate_model(scaled_data, differencing_order))
    st.write(f"📊 **Model RMSE Score:** {rmse:.4f}")

    # -------------------------------
    # Forecast next 30 days
    # -------------------------------
    forecast = get_forecast(scaled_data, differencing_order)
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
