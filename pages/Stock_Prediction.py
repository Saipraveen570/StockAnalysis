import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data, train_model, load_model, save_model, forecast
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
    ticker = st.text_input("Enter Stock Ticker", "AAPL", label_visibility="visible").upper()

st.subheader(f"Predicting next 30 days closing price for: {ticker}")

@st.cache_data(ttl=300, show_spinner=True)
def load_stock(tkr):
    df = get_data(tkr)
    return df if not df.empty else None

data = load_stock(ticker)

if data is None:
    st.error("Unable to fetch stock data. Ticker invalid or API rate-limit.")
    st.stop()

if len(data) < 90:
    st.warning("Insufficient data returned. Try another ticker.")
    st.stop()

close = data["Close"]

st.write("Latest Price:", round(close.iloc[-1], 2))

# Load model if exists, else train and save
model, scaler = load_model(ticker)

if model is None:
    with st.spinner("Training SARIMA model..."):
        model, scaler = train_model(data)
        save_model(model, scaler, ticker)

# Forecast
future = forecast(model, scaler, steps=30)
future_dates = pd.date_range(start=data.index[-1] + pd.Timedelta(days=1), periods=30)

forecast_df = pd.DataFrame({
    "Date": future_dates,
    "Predicted Close": future
}).set_index("Date")

st.write("##### Forecast Data (Next 30 Days)")
fig_table = plotly_table(forecast_df.round(3))
fig_table.update_layout(height=250)
st.plotly_chart(fig_table, use_container_width=True)

# Combine history with forecast
combined = pd.concat([close.tail(200), forecast_df["Predicted Close"]])

st.write("##### Forecast vs Historical Trend")
st.plotly_chart(Moving_average(combined), use_container_width=True)
