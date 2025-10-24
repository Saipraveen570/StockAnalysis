import streamlit as st
import pandas as pd
import time

# Import custom utilities
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

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="📈 Stock Prediction",
    page_icon=":chart_with_upwards_trend:",
    layout="wide"
)

# -------------------- PAGE HEADER --------------------
st.title("🔮 Stock Price Prediction Dashboard")

st.markdown("""
This app predicts the **next 30 days of stock closing prices** using a 
Linear Regression + Moving Average model.  
Enter a stock ticker (e.g. `AAPL`, `GOOG`, `TSLA`) and explore.
""")

col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    ticker = st.text_input("Enter Stock Ticker Symbol:", "AAPL").upper().strip()

# -------------------- DATA FETCHING --------------------
@st.cache_data(show_spinner=False)
def fetch_stock_data(ticker):
    try:
        data = get_data(ticker)
        return data
    except Exception as e:
        st.error(f"❌ Unable to fetch data for {ticker}. Please check ticker symbol.")
        st.stop()

with st.spinner(f"📡 Fetching market data for **{ticker}**..."):
    close_price = fetch_stock_data(ticker)
    time.sleep(0.5)

# -------------------- DATA PREPROCESSING --------------------
with st.spinner("⚙️ Smoothing & preparing data..."):
    rolling_price = get_rolling_mean(close_price)
    differencing_order = get_differencing_order(rolling_price)
    scaled_data, scaler = scaling(rolling_price)
    time.sleep(0.5)

# -------------------- MODEL EVALUATION --------------------
with st.spinner("🧮 Evaluating model performance..."):
    rmse = evaluate_model(scaled_data, differencing_order)
    st.success(f"✅ Model RMSE Score: **{rmse:.3f}**")
    time.sleep(0.5)

# -------------------- FORECASTING --------------------
st.subheader(f"🔮 Predicting Next 30 Days Close Price for: **{ticker}**")

with st.spinner("📊 Generating 30-day forecast..."):
    forecast = get_forecast(scaled_data, differencing_order)
    forecast['Close'] = inverse_scaling(scaler, forecast['Close'])
    time.sleep(0.5)

# -------------------- DISPLAY FORECAST TABLE --------------------
st.write("### 📅 Forecast Data (Next 30 Days)")
forecast_sorted = forecast.sort_index(ascending=True).round(3)
fig_table = plotly_table(forecast_sorted)
fig_table.update_layout(height=250)
st.plotly_chart(fig_table, use_container_width=True)

# -------------------- MOVING AVERAGE VISUAL --------------------
forecast_combined = pd.concat([rolling_price, forecast])
st.write("### 📈 Trend Visualization (Rolling Avg + Forecast)")

fig_forecast = Moving_average_forecast(forecast_combined.iloc[-150:])
st.plotly_chart(fig_forecast, use_container_width=True)

st.info("🕒 Tip: Refresh or change the ticker to compare stock predictions instantly!")

# -------------------- FOOTER --------------------
st.markdown("""
---
**Built with** 🐍 Python, Streamlit, Plotly & Scikit-learn  
**Forecasting Model:** Linear Regression + 7-day Moving Average
""")
