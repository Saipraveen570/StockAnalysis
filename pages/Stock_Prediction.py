import streamlit as st
import pandas as pd
import yfinance as yf
from utils.plotly_figure import plotly_table, Moving_average_forecast
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import datetime

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📉 Stock Prediction",
    page_icon="📈",
    layout="wide",
)

st.title("📉 Stock Prediction")

# -------------------------------
# User input
# -------------------------------
col1, col2 = st.columns(2)
today = datetime.date.today()

with col1:
    ticker = st.text_input('🔎 Stock Ticker', 'AAPL')
with col2:
    start_date = st.date_input("📅 Start Date", datetime.date(today.year-2, today.month, today.day))

st.subheader(f"Predicting Next 30 Days Close Price for: 🏢 {ticker}")

# -------------------------------
# Fetch historical data
# -------------------------------
try:
    data = yf.download(ticker, start=start_date, end=today, progress=False)

    if data.empty:
        st.warning("❌ Please enter a valid stock ticker")
    else:
        # 7-day moving average
        data['MA7'] = data['Close'].rolling(7).mean()

        # Scale Close for prediction
        scaler = MinMaxScaler()
        data_scaled = scaler.fit_transform(data[['Close']])

        # Prepare data for Linear Regression
        X = np.arange(len(data_scaled)).reshape(-1, 1)
        y = data_scaled

        model = LinearRegression()
        model.fit(X, y)

        # Forecast next 30 days
        future_X = np.arange(len(data_scaled), len(data_scaled)+30).reshape(-1, 1)
        forecast_scaled = model.predict(future_X)
        forecast = pd.DataFrame({
            'Date': pd.date_range(start=today + pd.Timedelta(days=1), periods=30),
            'Close': scaler.inverse_transform(forecast_scaled).flatten()
        })
        forecast.set_index('Date', inplace=True)

        st.write('##### Forecast Data (Next 30 days)')
        fig_tail = plotly_table(forecast.round(2))
        fig_tail.update_layout(height=220)
        st.plotly_chart(fig_tail, use_container_width=True)

        # Combine with historical for chart
        combined = pd.concat([data[['Close','MA7']], forecast])

        st.plotly_chart(Moving_average_forecast(combined.iloc[-150:]), use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Could not fetch data or forecast: {e}")
