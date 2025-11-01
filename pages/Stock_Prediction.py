import streamlit as st
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# ✅ Load environment variables (works locally)
load_dotenv()

# ✅ Correct import path for your folder structure
from pages.utils.plotly_figure import candlestick, RSI, Moving_average, MACD

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")

# ------------------- SIDEBAR INPUTS -------------------
st.sidebar.header("⚙️ Settings")

data_source = st.sidebar.selectbox("Select Data Source", ["Yahoo Finance", "Alpha Vantage"])
ticker = st.sidebar.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS)", "AAPL")

today = datetime.today()
start_date = st.sidebar.date_input("Start Date", today - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", today)

# ------------------- FETCH FUNCTION -------------------
@st.cache_data(show_spinner=True)
def fetch_stock_data(ticker, start, end, source):
    """Fetch stock data from Yahoo Finance or Alpha Vantage."""
    try:
        if source == "Yahoo Finance":
            df = yf.download(ticker, start=start, end=end)
            df.index = pd.to_datetime(df.index)
            return df

        elif source == "Alpha Vantage":
            api_key = (
                st.secrets.get("ALPHA_VANTAGE_API_KEY")
                if "ALPHA_VANTAGE_API_KEY" in st.secrets
                else os.getenv("ALPHA_VANTAGE_API_KEY")
            )

            if not api_key:
                st.warning("⚠️ Alpha Vantage API key not found. Please set it in Streamlit Secrets or .env file.")
                return pd.DataFrame()

            ts = TimeSeries(key=api_key, output_format="pandas")
            data, _ = ts.get_daily(symbol=ticker, outputsize="full")
            data.rename(
                columns={
                    "1. open": "Open",
                    "2. high": "High",
                    "3. low": "Low",
                    "4. close": "Close",
                    "5. volume": "Volume",
                },
                inplace=True,
            )
            data.index = pd.to_datetime(data.index)
            data = data.sort_index()
            return data.loc[str(start):str(end)]

    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# ------------------- LOAD DATA -------------------
st.info("⏳ Fetching data...")
data = fetch_stock_data(ticker, start_date, end_date, data_source)

if data.empty:
    st.error("⚠️ No data fetched. Please check your symbol or API key.")
    st.stop()

# ------------------- DISPLAY DATA -------------------
st.subheader(f"📊 Historical Data for {ticker}")
st.dataframe(data.tail(10), use_container_width=True)

st.divider()
st.subheader("📈 Technical Charts")

tab1, tab2, tab3, tab4 = st.tabs(["Candlestick", "RSI", "Moving Average", "MACD"])

with tab1:
    st.plotly_chart(candlestick(data), use_container_width=True)
with tab2:
    st.plotly_chart(RSI(data), use_container_width=True)
with tab3:
    st.plotly_chart(Moving_average(data), use_container_width=True)
with tab4:
    st.plotly_chart(MACD(data), use_container_width=True)

# ------------------- LINEAR REGRESSION FORECAST -------------------
st.divider()
st.subheader("📅 30-Day Linear Regression Forecast")

data["Days"] = (data.index - data.index[0]).days
X = data[["Days"]]
y = data["Close"]

model = LinearRegression()
model.fit(X, y)

future_days = 30
future = pd.DataFrame({"Days": range(data["Days"].max() + 1, data["Days"].max() + 1 + future_days)})
future["Predicted_Price"] = model.predict(future[["Days"]])

# ------------------- VISUALIZATION -------------------
st.line_chart(future.set_index("Days")["Predicted_Price"], use_container_width=True)

col1, col2 = st.columns(2)
col1.metric("Current Price", f"${data['Close'].iloc[-1]:.2f}")
col2.metric("Predicted (Next 30 Days)", f"${future['Predicted_Price'].iloc[-1]:.2f}")

st.success("✅ Forecast completed using Linear Regression Model.")
