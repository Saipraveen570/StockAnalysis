import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import yfinance as yf
from datetime import datetime, timedelta
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

st.set_page_config(
    page_title="Stock Prediction",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Prediction")

col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')

st.subheader(f'🔮 Predicting Next 30 Days Close Price for: {ticker}')

# --- Step 1: Get Data ---
@st.cache_data(show_spinner="Fetching stock data...")
def get_data(ticker):
    start_date = (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d')
    stock_data = yf.download(ticker, start=start_date)
    return stock_data[['Close']]

@st.cache_data(show_spinner="Computing rolling mean...")
def get_rolling_mean(close_price):
    return close_price.rolling(window=7).mean().dropna()

# --- Step 2: Fast Linear Regression Forecast ---
def get_forecast_linear(data):
    data = data.reset_index()
    data['day'] = np.arange(len(data))

    X = data[['day']]
    y = data['Close']

    model = LinearRegression()
    model.fit(X, y)

    future_days = np.arange(len(data), len(data) + 30).reshape(-1, 1)
    predictions = model.predict(future_days)

    forecast_index = pd.date_range(start=datetime.today(), periods=30)
    return pd.DataFrame(predictions, index=forecast_index, columns=["Close"])

# --- Processing ---
close_price = get_data(ticker)
rolling_price = get_rolling_mean(close_price)

# --- Forecasting ---
forecast = get_forecast_linear(rolling_price)

# --- Display Forecast Table ---
st.write('🗓️ **Forecast Data (Next 30 days)**')
fig_tail = plotly_table(forecast.round(2))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

# --- Combined Plot ---
combined = pd.concat([rolling_price, forecast])
st.plotly_chart(Moving_average_forecast(combined.tail(150)), use_container_width=True)
