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
# Helpers
# -------------------------------
def safe_ticker_symbol(t: str) -> str:
    if not t:
        return ""
    t = t.strip().upper()
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-")
    if len(t) > 12 or any(ch not in allowed for ch in t):
        return ""
    return t

@st.cache_data(show_spinner=False)
def safe_get_data(ticker: str):
    try:
        return get_data(ticker)
    except Exception:
        return pd.Series(dtype=float)

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Stock Prediction", page_icon="💹", layout="wide")
st.title("Stock Prediction")

# -------------------------------
# Input
# -------------------------------
col1, _, _ = st.columns(3)
with col1:
    raw_ticker = st.text_input("🔎 Stock Ticker", "AAPL")
    ticker = safe_ticker_symbol(raw_ticker)

if not ticker:
    st.warning("Enter a valid stock ticker.")
    st.stop()

st.subheader(f"🔮 Predicting next 30-day Close Price for: {ticker}")

# -------------------------------
# Load data
# -------------------------------
close_price = safe_get_data(ticker)

if close_price.empty:
    st.error("Unable to fetch stock data. Try a different ticker.")
    st.stop()

rolling_price = get_rolling_mean(close_price)

# Guard against insufficient data
if rolling_price.empty or rolling_price.shape[0] < 30:
    st.error("Insufficient data for prediction.")
    st.stop()

# -------------------------------
# Model preparation with fail safes
# -------------------------------
try:
    differencing_order = get_differencing_order(rolling_price)
except Exception:
    differencing_order = 1

try:
    scaled_data, scaler = scaling(rolling_price)
except Exception:
    st.error("Scaling error. Cannot continue prediction.")
    st.stop()

# -------------------------------
# Model evaluation
# -------------------------------
try:
    rmse = evaluate_model(scaled_data, differencing_order)
    st.write(f"📊 **Model RMSE Score:** {rmse:.4f}")
except Exception:
    st.warning("Model evaluation failed. Showing forecast based on available data.")

# -------------------------------
# Forecast
# -------------------------------
try:
    forecast = get_forecast(scaled_data, differencing_order)
    forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
except Exception:
    st.error("Forecast generation failed.")
    st.stop()

# Display forecast table
st.write("🗓️ **Forecast Data (Next 30 Days)**")
try:
    st.plotly_chart(plotly_table(forecast.sort_index().round(3)), use_container_width=True)
except Exception:
    st.dataframe(forecast)

# -------------------------------
# Combined Chart
# -------------------------------
try:
    combined = pd.concat([rolling_price, forecast])
    combined['MA7'] = combined['Close'].rolling(7).mean()
    combined = combined.dropna().iloc[-200:]
    st.plotly_chart(Moving_average_forecast(combined), use_container_width=True)
except Exception:
    st.warning("Unable to render forecast chart.")
