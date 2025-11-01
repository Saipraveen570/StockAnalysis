import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, get_rolling_mean, get_differencing_order,
    scaling, evaluate_model, get_forecast, inverse_scaling
)
from pages.utils.plotly_figure import plotly_table, Moving_average

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("Stock Prediction")

col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input("Stock Ticker", "AAPL").upper()

st.subheader(f"Predicting next 30 days Close Price for: {ticker}")

@st.cache_data(ttl=300)
def load_stock(tkr):
    try:
        close_price = get_data(tkr)
        if close_price is None or close_price.empty:
            return None
        return close_price
    except Exception:
        return None

close_price = load_stock(ticker)

if close_price is None:
    st.error("Unable to fetch stock data. Ticker may be invalid or Yahoo API limit reached.")
    st.stop()

if len(close_price) < 30:
    st.warning("Insufficient data returned. Yahoo Finance may be rate-limiting. Try again later or change ticker.")

rolling_price = get_rolling_mean(close_price)

try:
    differencing_order = get_differencing_order(rolling_price)
except Exception:
    differencing_order = 1

scaled_data, scaler = scaling(rolling_price)

try:
    rmse = evaluate_model(scaled_data, differencing_order)
except Exception:
    rmse = "N/A"

st.write("**Model RMSE Score:**", rmse)

@st.cache_data(ttl=300)
def do_forecast(data, d):
    try:
        return get_forecast(data, d)
    except Exception:
        return pd.DataFrame()

forecast = do_forecast(scaled_data, differencing_order)

if forecast is None or forecast.empty:
    st.error("Forecast failed. Try again later or use a different ticker.")
    st.stop()

try:
    forecast["Close"] = inverse_scaling(scaler, forecast["Close"])
except Exception:
    st.warning("Inverse scaling failed. Showing raw forecast values.")

st.write("##### Forecast Data (Next 30 Days)")
fig_tail = plotly_table(forecast.sort_index(ascending=True).round(3))
fig_tail.update_layout(height=250)
st.plotly_chart(fig_tail, use_container_width=True)

combined = pd.concat([rolling_price, forecast])

st.write("##### Forecast vs Historical Trend")
st.plotly_chart(Moving_average(combined.iloc[-200:], None), use_container_width=True)
