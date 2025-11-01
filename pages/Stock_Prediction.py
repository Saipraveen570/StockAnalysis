import streamlit as st
import pandas as pd
import yfinance as yf
import datetime as dt
from sklearn.linear_model import LinearRegression
import sys, os

# ✅ Fix import path for Streamlit Cloud
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.plotly_figure import candlestick, RSI, Moving_average, MACD

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")

# ------------------- USER INPUTS -------------------
ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL").upper()
start_date = st.date_input("Start Date", dt.date(2024, 1, 1))
end_date = st.date_input("End Date", dt.date.today())

# ------------------- FETCH DATA -------------------
st.write("⏳ Fetching data from Yahoo Finance...")
data = yf.download(ticker, start=start_date, end=end_date)

if data.empty:
    st.error("⚠️ No data fetched. Please enter a valid stock symbol.")
    st.stop()

# ------------------- SHOW CHARTS -------------------
st.markdown("### 📊 Historical Stock Data Visualizations")
st.plotly_chart(candlestick(data), use_container_width=True)
st.plotly_chart(RSI(data), use_container_width=True)
st.plotly_chart(Moving_average(data), use_container_width=True)
st.plotly_chart(MACD(data), use_container_width=True)

# ------------------- LINEAR REGRESSION MODEL -------------------
st.markdown("---")
st.subheader("📈 30-Day Price Forecast (Linear Regression)")

data["Days"] = (data.index - data.index[0]).days
X = data[["Days"]]
y = data["Close"]

model = LinearRegression()
model.fit(X, y)

# ------------------- FUTURE FORECAST -------------------
future_days = 30
future = pd.DataFrame({
    "Days": range(data["Days"].max() + 1, data["Days"].max() + 1 + future_days)
})
future["Predicted_Price"] = model.predict(future)

# Combine historical + future
predicted_df = pd.concat([
    data[["Close"]].reset_index().rename(columns={"Close": "Actual Price"}),
    future.assign(Date=pd.date_range(data.index[-1] + pd.Timedelta(days=1), periods=future_days))
], ignore_index=True)

# ------------------- PLOT -------------------
st.line_chart(future.set_index("Days")["Predicted_Price"])

# ------------------- DATA DOWNLOAD -------------------
st.download_button(
    label="⬇️ Download Predicted Prices (CSV)",
    data=future.to_csv(index=False).encode("utf-8"),
    file_name=f"{ticker}_30day_forecast.csv",
    mime="text/csv",
)

# ------------------- FOOTER -------------------
st.markdown(
    """
    ---
    💡 **Developed by Praveen P.**  
    Powered by: Streamlit • yFinance • Scikit-learn • Plotly  
    """
)
