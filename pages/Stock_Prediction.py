import streamlit as st
import pandas as pd
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
    page_title="Stock Prediction",
    page_icon="💹",
    layout="wide",
)

st.title("Stock Prediction")

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
    # Compute dynamic RMSE safely
    # -------------------------------
    try:
        rmse = evaluate_model(scaled_data, differencing_order)
    except Exception:
        rmse = float("nan")
    st.write(f"📊 **Model RMSE Score:** {rmse:.4f}" if not pd.isna(rmse) else "📊 **Model RMSE Score:** N/A")

    # -------------------------------
    # Forecast next 30 days safely
    # -------------------------------
    try:
        forecast = get_forecast(scaled_data, differencing_order)
        forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
    except Exception:
        forecast = pd.DataFrame(columns=['Close'])

    st.write("🗓️ ##### Forecast Data (Next 30 Days)")
    if not forecast.empty:
        st.plotly_chart(
            plotly_table(forecast.sort_index().round(3)),
            use_container_width=True
        )
    else:
        st.warning("⚠️ Forecast data not available.")

    # -------------------------------
    # Combined chart with rolling mean
    # -------------------------------
    combined = pd.concat([rolling_price, forecast])
    if 'Close' in combined.columns:
        combined['MA7'] = combined['Close'].rolling(7).mean()
        st.plotly_chart(
            Moving_average_forecast(combined.iloc[-150:]),
            use_container_width=True
        )
    else:
        st.info("📊 Combined chart cannot be displayed due to missing data.")
