import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="Stock Analyzer", layout="wide")

st.title("📈 Stock Analysis Dashboard")

# Styling
st.markdown("""
<style>
div.block-container {padding-top: 1.5rem;}
.stButton button {border-radius: 8px; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

def fetch_stock_data(symbol, period="1y", retries=3, delay=2):
    for attempt in range(retries):
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)

            if data is None or data.empty:
                time.sleep(delay)
                continue

            return data

        except Exception:
            time.sleep(delay)

    return None

ticker_input = st.text_input("Enter Stock Symbol", "AAPL").upper()

if st.button("Fetch Stock Data"):

    with st.spinner("Fetching data... please wait"):
        df = fetch_stock_data(ticker_input)

    if df is None or df.empty:
        st.error(f"⚠️ Invalid symbol or data unavailable.\nTry: AAPL, TSLA, RELIANCE.NS, BTC-USD")
    else:
        st.success(f"✅ Data loaded for {ticker_input}")

        st.subheader(f"📊 Closing Price Chart: {ticker_input}")
        st.line_chart(df["Close"])

        st.subheader("📁 Raw Data")
        st.dataframe(df)

        st.download_button(
            label="Download Data as CSV",
            data=df.to_csv().encode("utf-8"),
            file_name=f"{ticker_input}_data.csv",
            mime="text/csv"
        )
