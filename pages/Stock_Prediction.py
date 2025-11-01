import streamlit as st
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
import datetime as dt
from sklearn.linear_model import LinearRegression
import os, sys, time

# ✅ Fix path for utils import (for Streamlit Cloud)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.plotly_figure import candlestick, RSI, Moving_average, MACD

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")

# ------------------- INPUT SECTION -------------------
ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS):", "AAPL")
start_date = st.date_input("Start Date", dt.date(2024, 1, 1))
end_date = st.date_input("End Date", dt.date.today())

st.info("⏳ Fetching and merging data from Yahoo Finance & Alpha Vantage...")

# ------------------- FETCH FUNCTIONS -------------------
def fetch_yahoo_data(ticker, start, end, retries=3):
    """Fetch stock data from Yahoo Finance."""
    for i in range(retries):
        try:
            data = yf.download(ticker, start=start, end=end, progress=False, threads=False)
            if not data.empty:
                return data
            stock = yf.Ticker(ticker)
            data = stock.history(start=start, end=end)
            if not data.empty:
                return data
        except Exception as e:
            st.warning(f"Yahoo attempt {i+1} failed: {e}")
        time.sleep(2 ** i)
    return pd.DataFrame()

def fetch_alpha_vantage_data(ticker):
    """Fetch stock data from Alpha Vantage (daily adjusted)."""
    try:
        api_key = st.secrets["ALPHA_VANTAGE_KEY"]
        ts = TimeSeries(key=api_key, output_format='pandas')
        data, meta = ts.get_daily_adjusted(symbol=ticker, outputsize='full')
        data = data.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. adjusted close': 'Adj Close',
            '6. volume': 'Volume'
        })
        data.index = pd.to_datetime(data.index)
        return data.sort_index()
    except Exception as e:
        st.error(f"Alpha Vantage fetch failed: {e}")
        return pd.DataFrame()

# ------------------- MERGING FUNCTION -------------------
def merge_data(yahoo_df, alpha_df):
    """Combine Yahoo + Alpha data, prioritizing Yahoo."""
    if yahoo_df.empty and alpha_df.empty:
        return pd.DataFrame()
    if yahoo_df.empty:
        return alpha_df
    if alpha_df.empty:
        return yahoo_df

    # Merge both datasets
    merged = yahoo_df.combine_first(alpha_df)
    merged = merged.loc[~merged.index.duplicated(keep="first")]
    merged = merged.sort_index()
    return merged

# ------------------- FETCH + MERGE -------------------
yahoo_data = fetch_yahoo_data(ticker, start_date, end_date)
alpha_data = fetch_alpha_vantage_data(ticker)

if yahoo_data.empty and alpha_data.empty:
    st.error("❌ Unable to fetch data from both Yahoo Finance & Alpha Vantage. Try again later or use a valid symbol.")
    st.stop()

data = merge_data(yahoo_data, alpha_data)
data = data[(data.index >= pd.to_datetime(start_date)) & (data.index <= pd.to_datetime(end_date))]

st.success(f"✅ Fetched and merged {len(data)} records for {ticker}")

# ------------------- TECHNICAL CHARTS -------------------
st.subheader("📊 Technical Analysis Charts")
st.plotly_chart(candlestick(data), use_container_width=True)
st.plotly_chart(RSI(data), use_container_width=True)
st.plotly_chart(Moving_average(data), use_container_width=True)
st.plotly_chart(MACD(data), use_container_width=True)

# ------------------- LINEAR REGRESSION FORECAST -------------------
st.subheader("🤖 30-Day Price Forecast (Linear Regression)")

data["Days"] = (data.index - data.index[0]).days
X = data[["Days"]]
y = data["Close"]

model = LinearRegression()
model.fit(X, y)

future_days = 30
future = pd.DataFrame({"Days": range(data["Days"].max() + 1, data["Days"].max() + 1 + future_days)})
future["Predicted_Price"] = model.predict(future)

st.line_chart(future.set_index("Days")["Predicted_Price"])
st.caption("📈 Forecast generated using a simple linear regression model.")

# ------------------- FOOTER -------------------
st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Yahoo Finance, Alpha Vantage & Plotly")
