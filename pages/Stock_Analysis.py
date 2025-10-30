import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.arima.model import ARIMA
from functools import lru_cache

# ------------------------
# Streamlit Page Config
# ------------------------
st.set_page_config(page_title="Stock Price Forecasting", page_icon="💹", layout="wide")
st.title("📈 Stock Price Forecasting App")

# ------------------------
# Fetch data with cache
# ------------------------
@st.cache_data(show_spinner=True)
def fetch_data(ticker):
    data = yf.download(
        ticker,
        period="5y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False
    )

    if data is None or data.empty:
        raise ValueError("Unable to fetch data. Invalid ticker or data unavailable.")

    return data["Close"].to_frame(name="Close")

# ------------------------
# Forecast function (cached)
# ------------------------
@lru_cache(maxsize=50)
def forecast_prices(series, steps=30):
    try:
        model = ARIMA(series, order=(3,1,2))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return forecast
    except Exception:
        model = ARIMA(series, order=(1,1,1))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        return forecast

# ------------------------
# User Input
# ------------------------
ticker = st.text_input("Enter Stock Ticker (Example: AAPL, TSLA, MSFT)", "AAPL").upper()

# ------------------------
# Load Data + Forecast
# ------------------------
try:
    close_df = fetch_data(ticker)

    st.subheader(f"📊 Historical Close Prices for {ticker}")
    st.line_chart(close_df)

    st.subheader(f"🔮 Forecasting Next 30 Days for {ticker}")
    series = tuple(close_df["Close"].values)

    forecast_vals = forecast_prices(series)
    future_dates = pd.date_range(start=close_df.index[-1], periods=31, freq="D")[1:]

    forecast_df = pd.DataFrame({"Date": future_dates, "Forecast": forecast_vals})
    forecast_df.set_index("Date", inplace=True)

    st.line_chart(forecast_df)

    st.subheader("📝 Forecast Table")
    st.dataframe(forecast_df.round(2))

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Try another ticker (e.g., GOOGL, META, NVDA) or check internet.")
