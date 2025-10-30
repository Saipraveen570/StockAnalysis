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

# -----------------------------------
# Streamlit Page Config
# -----------------------------------
st.set_page_config(
    page_title="Stock Prediction",
    page_icon="💹",
    layout="wide",
)

st.title("Stock Prediction")

# -----------------------------------
# User Input
# -----------------------------------
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input("🔎 Stock Ticker", "AAPL").strip().upper()

if not ticker:
    st.stop()

st.subheader(f"🔮 Predicting Next 30 Days Close Price for: {ticker}")

# -----------------------------------
# Fetch & Process Data
# -----------------------------------
close_price = get_data(ticker)

if close_price.empty or "Close" not in close_price.columns:
    st.error("Unable to fetch stock data. Ticker may be invalid or data source unavailable.")
    st.stop()

rolling_price = get_rolling_mean(close_price)

if rolling_price.empty:
    st.error("Insufficient data for moving average and prediction. Try a different ticker.")
    st.stop()

differencing_order = get_differencing_order(rolling_price)
scaled_data, scaler = scaling(rolling_price)

# -----------------------------------
# Compute RMSE
# -----------------------------------
try:
    rmse = evaluate_model(scaled_data, differencing_order)
    st.write(f"📊 **Model RMSE Score:** {rmse:.4f}")
except Exception:
    st.warning("Model evaluation failed; continuing with prediction.")

# -----------------------------------
# Forecast Next 30 Days
# -----------------------------------
try:
    forecast = get_forecast(scaled_data, differencing_order)
    forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
except Exception:
    st.error("Forecasting failed. Please retry later.")
    st.stop()

st.write("🗓️ ##### Forecast Data (Next 30 Days)")
try:
    st.plotly_chart(plotly_table(forecast.sort_index().round(3)), use_container_width=True)
except Exception:
    st.dataframe(forecast)

# -----------------------------------
# Combined Chart
# -----------------------------------
combined = pd.concat([rolling_price, forecast])
combined['MA7'] = combined['Close'].rolling(7).mean()

try:
    st.plotly_chart(Moving_average_forecast(combined.iloc[-150:]), use_container_width=True)
except Exception:
    st.warning("Unable to render forecast chart.")
    st.dataframe(combined.tail(30))
