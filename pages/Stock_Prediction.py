import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
from sklearn.linear_model import LinearRegression
import os, sys, time

# ✅ Fix path for utils if running in Streamlit Cloud
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.plotly_figure import candlestick, RSI, Moving_average, MACD


# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")

# ------------------- INPUT SECTION -------------------
ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL")
start_date = st.date_input("Start Date", dt.date(2024, 1, 1))
end_date = st.date_input("End Date", dt.date.today())

st.info("⏳ Fetching data from Yahoo Finance...")

# ------------------- FETCH FUNCTION (SAFE) -------------------
def fetch_data_safe(ticker, start, end, retries=3):
    """Fetch stock data safely with retry and rate-limit handling."""
    for i in range(retries):
        try:
            # Primary fetch method
            data = yf.download(ticker, start=start, end=end, progress=False, threads=False)
            if not data.empty:
                return data

            # Fallback to Ticker().history() if download fails
            stock = yf.Ticker(ticker)
            data = stock.history(start=start, end=end)
            if not data.empty:
                return data

        except Exception as e:
            st.warning(f"Attempt {i+1} failed: {e}")

        time.sleep(2 ** i)  # Exponential backoff (1s, 2s, 4s)
    return pd.DataFrame()

# ------------------- FETCH DATA -------------------
data = fetch_data_safe(ticker, start_date, end_date)

if data.empty:
    st.error("⚠️ No data fetched. Yahoo Finance may be rate-limiting. Please try again in a few minutes or use a different symbol.")
    st.stop()

st.success(f"✅ Successfully fetched {len(data)} records for {ticker}!")

# ------------------- TECHNICAL CHARTS -------------------
st.subheader("📈 Technical Analysis Charts")
st.plotly_chart(candlestick(data), use_container_width=True)
st.plotly_chart(RSI(data), use_container_width=True)
st.plotly_chart(Moving_average(data), use_container_width=True)
st.plotly_chart(MACD(data), use_container_width=True)

# ------------------- LINEAR REGRESSION PREDICTION -------------------
st.subheader("🤖 30-Day Price Forecast (Linear Regression)")

data["Days"] = (data.index - data.index[0]).days
X = data[["Days"]]
y = data["Close"]

model = LinearRegression()
model.fit(X, y)

future_days = 30
future = pd.DataFrame({"Days": range(data["Days"].max() + 1, data["Days"].max() + 1 + future_days)})
future["Predicted_Price"] = model.predict(future)

# ------------------- DISPLAY FORECAST -------------------
st.line_chart(future.set_index("Days")["Predicted_Price"])
st.caption("📊 Simple linear regression forecast based on past closing prices.")

# ------------------- FOOTER -------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Yahoo Finance, and Plotly")
