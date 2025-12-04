import streamlit as st
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import sys
import os

# Fix import path for utils (for Streamlit Cloud / different layout)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Your project must have pages/utils/plotly_figure.py with candlestick, RSI, Moving_average, MACD functions
from pages.utils.plotly_figure import candlestick, RSI, Moving_average, MACD

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🤖 Stock Price Prediction", layout="wide")
st.title("🤖 Stock Price Prediction Dashboard")

# ------------------- USER INPUT -------------------
ticker = st.text_input("Enter Stock Symbol (e.g. AAPL, TSLA, INFY.NS)", "AAPL").upper()
start_date = st.date_input("Start Date", datetime(2024, 1, 1))
end_date = st.date_input("End Date", datetime.today().date())

if start_date > end_date:
    st.error("Start Date must be before End Date.")
    st.stop()

# ------------------- DATA FETCHING -------------------
st.info("⏳ Fetching data from Yahoo Finance...")

@st.cache_data(ttl=600)
def fetch_yahoo(ticker: str, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    """
    Fetch from Yahoo (yfinance). Make end_date inclusive by adding one day to yf.download end param.
    """
    try:
        df = yf.download(ticker, start=start_date, end=end_date + timedelta(days=1), progress=False)
        if df.empty:
            return pd.DataFrame()
        df.index = pd.to_datetime(df.index)
        return df
    except Exception as e:
        # return empty so fallback triggers
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_alpha(ticker: str, start_date: datetime.date, end_date: datetime.date) -> pd.DataFrame:
    """
    Fallback using Alpha Vantage free tier (compact).
    compact returns approx last 100 daily rows. We'll filter to requested range
    and if no rows found return the available compact data (so user at least sees recent history).
    """
    try:
        # get key from streamlit secrets
        try:
            ALPHA_KEY = st.secrets["general"]["ALPHA_VANTAGE_KEY"]
        except Exception:
            st.error("Alpha Vantage API key not found in st.secrets['general']['ALPHA_VANTAGE_KEY'].")
            return pd.DataFrame()

        ts = TimeSeries(key=ALPHA_KEY, output_format="pandas")
        # IMPORTANT: use compact (free tier)
        data, _ = ts.get_daily(symbol=ticker, outputsize="compact")

        # Rename columns to expected names
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
        data.sort_index(inplace=True)

        # Create Adj Close if missing
        if "Adj Close" not in data.columns and "Close" in data.columns:
            data["Adj Close"] = data["Close"]

        # Filter for requested dates
        filtered = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]

        # If filtered empty but data exists, return full compact data (so user sees recent ~100 rows)
        return filtered if not filtered.empty else data

    except Exception as e:
        st.error(f"Alpha Vantage failed: {e}")
        return pd.DataFrame()

# Try Yahoo first
data = fetch_yahoo(ticker, start_date, end_date)

# If empty, fallback to Alpha
if data.empty:
    st.warning("⚠️ Yahoo Finance returned no data — attempting Alpha Vantage (free: last ~100 days)...")
    data = fetch_alpha(ticker, start_date, end_date)

# Stop if still empty
if data.empty:
    st.error(f"❌ Could not fetch data for {ticker}. Check symbol or API key.")
    st.stop()

# If Alpha provided only recent data and it doesn't cover the requested start_date, warn user
try:
    min_date = data.index.date.min()
    if min_date > start_date:
        st.warning(
            f"Note: available data starts on {min_date}. Alpha Vantage 'compact' returns only ~100 most recent daily rows on free tier."
        )
except Exception:
    pass

# ------------------- CLEAN & VALIDATE -------------------
# Ensure numeric columns are numeric
for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors="coerce")

# Drop rows missing Close
data = data.dropna(subset=["Close"])
if data.empty:
    st.error("No valid 'Close' prices available after cleaning.")
    st.stop()

# Filter again to requested date range (in case fallback returned extra rows)
data = data.loc[(data.index.date >= start_date) & (data.index.date <= end_date)]
if data.empty:
    st.error("No data for selected date range after filtering.")
    st.stop()

st.success(f"✅ Data fetched successfully for {ticker} ({data.index.date.min()} to {data.index.date.max()})")

# ------------------- VISUALIZATIONS -------------------
st.subheader("Technical Analysis Charts")
try:
    st.plotly_chart(candlestick(data), use_container_width=True)
    st.plotly_chart(RSI(data), use_container_width=True)
    st.plotly_chart(Moving_average(data), use_container_width=True)
    st.plotly_chart(MACD(data), use_container_width=True)
except Exception as e:
    st.warning(f"Could not render one or more technical charts: {e}")

# ------------------- SIMPLE LINEAR REGRESSION FORECAST -------------------
st.subheader("📈 30-Day Linear Regression Forecast (Simple)")

# Prepare features - Days since first date
data = data.sort_index()
data = data.reset_index()  # make index a column
if "Date" not in data.columns:
    # depending on source the index column name may differ
    data = data.rename(columns={data.columns[0]: "Date"})
data["Date"] = pd.to_datetime(data["Date"]).dt.date
data["Days"] = (pd.to_datetime(data["Date"]) - pd.to_datetime(data["Date"].iloc[0])).dt.days

# Need enough rows to train a model
MIN_ROWS_TO_TRAIN = 30
if data.shape[0] < MIN_ROWS_TO_TRAIN:
    st.error(f"Not enough data to train model (need at least {MIN_ROWS_TO_TRAIN} rows, got {data.shape[0]}).")
    st.stop()

X = data[["Days"]].values.reshape(-1, 1)
y = data["Close"].values.reshape(-1, 1)

model = LinearRegression()
model.fit(X, y)

future_days = 30
last_day = int(data["Days"].max())
future_range = list(range(last_day + 1, last_day + 1 + future_days))
future_df = pd.DataFrame({"Days": future_range})
future_df["Predicted_Price"] = model.predict(future_df[["Days"]])

# Convert Days back to dates for plotting axis
first_date = pd.to_datetime(data["Date"].iloc[0])
future_df["Date"] = future_df["Days"].apply(lambda d: (first_date + pd.Timedelta(days=int(d))).date())

# Plot predicted prices (use line_chart for simplicity)
plot_df = future_df.set_index("Date")[["Predicted_Price"]]
st.line_chart(plot_df)

st.success("✅ Forecast complete! Scroll above for detailed insights.")

# ------------------- DOWNLOADS -------------------
st.markdown("### 💾 Download historical data")
csv = data.set_index("Date").to_csv()
st.download_button(label="Download CSV", data=csv, file_name=f"{ticker}_data_{start_date}_{end_date}.csv", mime="text/csv")
