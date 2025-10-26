import streamlit as st
import yfinance as yf
import pandas as pd
from pages.utils.plotly_figure import candlestick, RSI, Moving_average

# Page config
st.set_page_config(page_title="📊 Stock Analysis", page_icon="💹", layout="wide")
st.title("📊 Stock Analysis (Light Version)")

# Inputs
ticker = st.text_input("🔎 Stock Ticker", "AAPL")
period = st.selectbox("⏱️ Period", ["1y", "6mo", "3mo", "1mo"], index=0)
chart_type = st.selectbox("📊 Chart Type", ["Line", "Candle"])
indicator = st.selectbox("📈 Indicator", ["RSI", "Moving Average", "MACD"])
rsi_window = st.slider("🔧 RSI Window", 5, 50, 14)

if ticker:
    # Fetch data once
    data = yf.Ticker(ticker).history(period=period)
    
    if data.empty:
        st.warning("❌ No data found. Enter a valid ticker.")
    else:
        # Latest price
        latest_close = data['Close'].iloc[-1]
        daily_change = latest_close - data['Close'].iloc[-2]
        st.metric(f"{ticker} Latest Close", round(latest_close,2), round(daily_change,2))
        
        # Plot chart
        if chart_type == "Candle":
            st.plotly_chart(candlestick(data), use_container_width=True)
        else:
            st.plotly_chart(data['Close'], use_container_width=True)
        
        # Indicators
        if indicator == "RSI":
            st.plotly_chart(RSI(data, window=rsi_window), use_container_width=True)
        elif indicator == "Moving Average":
            st.plotly_chart(Moving_average(data), use_container_width=True)
        elif indicator == "MACD":
            from pages.utils.plotly_figure import MACD
            st.plotly_chart(MACD(data), use_container_width=True)
