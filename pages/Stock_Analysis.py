import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date, timedelta
from sklearn.linear_model import LinearRegression

# --------------------------------------------------
# Streamlit Page Setup
# --------------------------------------------------
st.set_page_config(page_title="📊 Stock Analysis & Forecast", page_icon="📈", layout="wide")

st.title("📊 Stock Analysis & Forecasting Dashboard")
st.markdown("Get real-time data, RSI insights, and 30-day forecasts powered by Linear Regression 💹")

# --------------------------------------------------
# Cached Data Fetchers
# --------------------------------------------------
@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end)
        return data
    except yf.utils.YFRateLimitError:
        st.warning("⚠️ Yahoo Finance API rate limit reached. Please wait a few minutes before retrying.")
        return pd.DataFrame()
    except Exception:
        st.error("❌ Error fetching stock data.")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_summary(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.get_info()
        return info.get('longBusinessSummary', 'No summary available')
    except yf.utils.YFRateLimitError:
        st.warning("⚠️ Rate limit reached. Summary temporarily unavailable.")
        return "Summary unavailable due to rate limit."
    except Exception:
        return "No summary available."

# --------------------------------------------------
# Sidebar Settings
# --------------------------------------------------
st.sidebar.header("⚙️ Settings")
symbol = st.sidebar.text_input("Enter Stock Symbol (e.g., AAPL, INFY.NS):", "AAPL")
start_date = st.sidebar.date_input("Start Date", date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", date.today())

# --------------------------------------------------
# Fetch Stock Data
# --------------------------------------------------
data = get_stock_data(symbol, start_date, end_date)

if data.empty:
    st.warning("⚠️ No data available. Try another stock or date range.")
    st.stop()

# --------------------------------------------------
# Candlestick Chart
# --------------------------------------------------
st.subheader(f"📈 Price Movement for {symbol}")
fig = go.Figure(data=[go.Candlestick(
    x=data.index,
    open=data['Open'],
    high=data['High'],
    low=data['Low'],
    close=data['Close'],
    name="Candlestick"
)])
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    xaxis_rangeslider_visible=False,
    template="plotly_white",
    height=500
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# RSI Calculation
# --------------------------------------------------
st.subheader("📊 Relative Strength Index (RSI - 14 Day)")
delta = data['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

rsi_fig = go.Figure()
rsi_fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI', line=dict(color='orange')))
rsi_fig.add_hline(y=70, line_dash="dot", line_color="red", annotation_text="Overbought")
rsi_fig.add_hline(y=30, line_dash="dot", line_color="green", annotation_text="Oversold")
rsi_fig.update_layout(xaxis_title="Date", yaxis_title="RSI", height=300, template="plotly_white")
st.plotly_chart(rsi_fig, use_container_width=True)

# --------------------------------------------------
# Company Overview
# --------------------------------------------------
st.subheader("🏢 Company Overview")
summary = get_stock_summary(symbol)
st.write(summary)

# --------------------------------------------------
# Forecasting Section
# --------------------------------------------------
st.subheader("📅 30-Day Stock Price Forecast")

def forecast_linear_regression(data, days=30):
    df = data.reset_index()
    df['Days'] = np.arange(len(df))
    X = df[['Days']]
    y = df['Close']

    model = LinearRegression()
    model.fit(X, y)

    # Future dates
    future_days = np.arange(len(df), len(df) + days)
    future_dates = pd.date_range(df['Date'].iloc[-1] + timedelta(days=1), periods=days)
    future_preds = model.predict(future_days.reshape(-1, 1))

    forecast_df = pd.DataFrame({'Date': future_dates, 'Predicted_Close': future_preds})
    return forecast_df

forecast_df = forecast_linear_regression(data)

# Combine with actual
combined = pd.concat([
    pd.DataFrame({'Date': data.index, 'Close': data['Close'], 'Type': 'Actual'}),
    pd.DataFrame({'Date': forecast_df['Date'], 'Close': forecast_df['Predicted_Close'], 'Type': 'Forecast'})
])

forecast_fig = go.Figure()
forecast_fig.add_trace(go.Scatter(
    x=combined[combined['Type'] == 'Actual']['Date'],
    y=combined[combined['Type'] == 'Actual']['Close'],
    mode='lines',
    name='Actual',
    line=dict(color='blue')
))
forecast_fig.add_trace(go.Scatter(
    x=combined[combined['Type'] == 'Forecast']['Date'],
    y=combined[combined['Type'] == 'Forecast']['Close'],
    mode='lines',
    name='Forecast',
    line=dict(color='orange', dash='dot')
))
forecast_fig.update_layout(
    title=f"📊 {symbol} - Next 30 Days Forecast",
    xaxis_title="Date",
    yaxis_title="Close Price (USD)",
    template="plotly_white",
    height=450
)
st.plotly_chart(forecast_fig, use_container_width=True)

# --------------------------------------------------
# Recent Closing Prices
# --------------------------------------------------
st.subheader("💰 Recent Closing Prices")
st.dataframe(data[['Close']].tail(10).style.format("{:.2f}"))
