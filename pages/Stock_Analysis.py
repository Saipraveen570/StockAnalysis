import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import yfinance as yf
from datetime import datetime, timedelta
from pages.utils.plotly_figure import plotly_table, Moving_average_forecast

# --- Page Config ---
st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📉",
    layout="wide",
)

st.title("📈 Stock Analysis")

# --- User Input ---
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

# --- Step 2: Linear Regression + Realistic Forecast ---
def get_forecast_linear(data):
    data = data.reset_index()
    data['day'] = np.arange(len(data))

    X = data[['day']]
    y = data['Close']

    # Fit model
    model = LinearRegression()
    model.fit(X, y)

    # Predict trend for next 30 days
    future_days = np.arange(len(data), len(data) + 30).reshape(-1, 1)
    trend_pred = model.predict(future_days).ravel()  # flatten ensures shape compatibility

    # Add realistic volatility (small random variation)
    recent_diff = data['Close'].diff().dropna()
    avg_change = recent_diff.tail(7).mean()
    std_change = recent_diff.tail(7).std()

    np.random.seed(42)
    random_fluctuations = np.random.normal(avg_change, std_change, size=30)
    final_pred = trend_pred + np.cumsum(random_fluctuations)

    # Fix shape issue — ensure index matches
    forecast_index = pd.date_range(start=datetime.today(), periods=30)
    forecast_df = pd.DataFrame({'Close': final_pred}, index=forecast_index)

    # Smooth slightly
    forecast_df['Close'] = forecast_df['Close'].rolling(window=3, min_periods=1).mean()
    return forecast_df

# --- Processing ---
close_price = get_data(ticker)
rolling_price = get_rolling_mean(close_price)

# --- Forecasting ---
forecast = get_forecast_linear(rolling_price)

# --- Display Forecast Table ---
st.write('🗓️ **Forecast Data (Next 30 Days)**')
fig_tail = plotly_table(forecast.round(2))
fig_tail.update_layout(height=220)
st.plotly_chart(fig_tail, use_container_width=True)

# --- Combined Plot with Animation ---
combined = pd.concat([rolling_price, forecast])
st.plotly_chart(Moving_average_forecast(combined.tail(150)), use_container_width=True)

st.caption("⚠️ Note: Forecasts are for educational use only. Not financial advice.")
