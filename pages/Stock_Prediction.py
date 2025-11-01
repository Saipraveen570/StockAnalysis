import streamlit as st
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import sys
import os

# ✅ Fix import path for utils (for Streamlit Cloud)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.utils.plotly_figure import candlestick, RSI, Moving_average, MACD


# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")

# ------------------- USER INPUT -------------------
ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS)", "AAPL")
start_date = st.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.date_input("End Date", datetime.today())

# ------------------- DATA FETCHING -------------------
st.info("⏳ Fetching data from Yahoo Finance...")

try:
    data = yf.download(ticker, start=start_date, end=end_date)
except Exception as e:
    data = pd.DataFrame()

# If Yahoo fails, try Alpha Vantage
if data.empty:
    st.warning("⚠️ Yahoo Finance failed. Trying Alpha Vantage...")

    try:
        # ✅ Get API key securely
        ALPHA_KEY = st.secrets["general"]["ALPHA_VANTAGE_KEY"]

        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        data, _ = ts.get_daily(symbol=ticker, outputsize="full")
        data = data.rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume",
            }
        )
        data.index = pd.to_datetime(data.index)
        data = data[(data.index >= pd.Timestamp(start_date)) & (data.index <= pd.Timestamp(end_date))]
        data.sort_index(inplace=True)

    except Exception as e:
        st.error(f"❌ Could not fetch data for {ticker}. Error: {e}")
        st.stop()

if data.empty:
    st.error("⚠️ No data fetched. Please enter a valid stock symbol.")
    st.stop()

st.success(f"✅ Data fetched successfully for {ticker}")

# ------------------- VISUALIZATIONS -------------------
st.subheader("📊 Technical Analysis Charts")

st.plotly_chart(candlestick(data), use_container_width=True)
st.plotly_chart(RSI(data), use_container_width=True)
st.plotly_chart(Moving_average(data), use_container_width=True)
st.plotly_chart(MACD(data), use_container_width=True)

# ------------------- LINEAR REGRESSION FORECAST -------------------
st.subheader("📈 30-Day Linear Regression Forecast")

data["Days"] = (data.index - data.index[0]).days
X = data[["Days"]]
y = data["Close"]

model = LinearRegression()
model.fit(X, y)

future_days = 30
future = pd.DataFrame(
    {"Days": range(data["Days"].max() + 1, data["Days"].max() + 1 + future_days)}
)
future["Predicted_Price"] = model.predict(future)

st.line_chart(future.set_index("Days")["Predicted_Price"])

st.success("✅ Forecast complete! Scroll above for detailed insights.")
