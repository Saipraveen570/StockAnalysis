import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
from sklearn.linear_model import LinearRegression
from utils.plotly_figure import candlestick, RSI, Moving_average, MACD

st.title("🤖 Stock Price Prediction")

ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS)", "AAPL")
start_date = st.date_input("Start Date", dt.date(2024, 1, 1))
end_date = st.date_input("End Date", dt.date.today())

data = yf.download(ticker, start=start_date, end=end_date)

if data.empty:
    st.error("No data fetched. Try a valid symbol.")
    st.stop()

st.plotly_chart(candlestick(data))
st.plotly_chart(RSI(data))
st.plotly_chart(Moving_average(data))
st.plotly_chart(MACD(data))

# Prediction
data["Days"] = (data.index - data.index[0]).days
X = data[["Days"]]
y = data["Close"]
model = LinearRegression()
model.fit(X, y)

future_days = 30
future = pd.DataFrame({"Days": range(data["Days"].max() + 1, data["Days"].max() + 1 + future_days)})
future["Predicted_Price"] = model.predict(future)

st.subheader("📅 30-Day Linear Regression Forecast")
st.line_chart(future.set_index("Days")["Predicted_Price"])
