import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.plotly_figure import (
    plotly_table,
    close_chart,
    candlestick,
    RSI,
    Moving_average,
    MACD,
)

# -----------------------
# Caching helpers
# -----------------------
@st.cache_data(show_spinner=False)
def get_company_info(ticker: str):
    try:
        info = yf.Ticker(ticker).info
    except Exception:
        info = {}
    # Keep only simple serializable primitives (safe for Streamlit cache)
    clean = {
        k: v
        for k, v in info.items()
        if isinstance(v, (int, float, str, bool, type(None)))
    }
    return clean


@st.cache_data(show_spinner=False)
def get_company_summary(ticker: str):
    try:
        info = yf.Ticker(ticker).info
        return info.get("longBusinessSummary", "No summary available.")
    except Exception:
        return "No summary available."


@st.cache_data(show_spinner=False)
def load_price_data(ticker: str, start: datetime.date, end: datetime.date):
    try:
        # yfinance accepts datetime.date or strings
        return yf.download(ticker, start=start, end=end, progress=False)
    except Exception:
        return pd.DataFrame()


@st.cache_data(show_spinner=False)
def load_full_price(ticker: str) -> pd.DataFrame:
    try:
        df = yf.Ticker(ticker).history(period="max")
        return df
    except Exception:
        return pd.DataFrame()


# -----------------------
# Page config
# -----------------------
st.set_page_config(page_title="Stock Analysis", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title("Stock Analysis")

today = datetime.date.today()

# Inputs
col1, col2, col3 = st.columns(3)
with col1:
    ticker = st.text_input("Stock Ticker", "AAPL").strip().upper()
with col2:
    start_date = st.date_input("Start Date", today - datetime.timedelta(days=365))
with col3:
    end_date = st.date_input("End Date", today)

if not ticker:
    st.error("Please provide a stock ticker.")
    st.stop()

# Company info
info = get_company_info(ticker)
summary = get_company_summary(ticker)

st.subheader(f"{ticker} Overview")
st.write(summary)
st.write("Sector:", info.get("sector", "N/A"))
st.write("Employees:", info.get("fullTimeEmployees", "N/A"))
st.write("Website:", info.get("website", "N/A"))

# Quick metrics tables
c1, c2 = st.columns(2)
with c1:
    df1 = pd.DataFrame(
        {
            "Metric": ["Market Cap", "Beta", "EPS", "PE Ratio"],
            "Value": [
                info.get("marketCap"),
                info.get("beta"),
                info.get("trailingEps"),
                info.get("trailingPE"),
            ],
        }
    )
    st.plotly_chart(plotly_table(df1), use_container_width=True)

with c2:
    df2 = pd.DataFrame(
        {
            "Metric": ["Quick Ratio", "Rev/Share", "Profit Margin", "Debt/Equity", "ROE"],
            "Value": [
                info.get("quickRatio"),
                info.get("revenuePerShare"),
                info.get("profitMargins"),
                info.get("debtToEquity"),
                info.get("returnOnEquity"),
            ],
        }
    )
    st.plotly_chart(plotly_table(df2), use_container_width=True)

# Price & metrics (range)
df = load_price_data(ticker, start_date, end_date)

if df.empty or "Close" not in df.columns:
    st.warning("No price data available for this ticker in the selected date range.")
else:
    # Safely convert last/latest values
    try:
        latest_val = float(df["Close"].iloc[-1])
    except Exception:
        latest_val = 0.0

    if len(df) > 1:
        try:
            daily_val = float(df["Close"].iloc[-1] - df["Close"].iloc[-2])
        except Exception:
            daily_val = 0.0
    else:
        daily_val = 0.0

    c1, _, _ = st.columns(3)
    c1.metric(label="Daily Close", value=f"{latest_val:.2f}", delta=f"{daily_val:.2f}")

    # format index for a small table
    df_display = df.copy()
    if isinstance(df_display.index, pd.DatetimeIndex):
        df_display.index = df_display.index.date.astype(str)
    else:
        df_display.index = df_display.index.astype(str)

    st.write("Last 10 Days Data")
    st.plotly_chart(plotly_table(df_display.tail(10).round(3).iloc[::-1]), use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Period selector (map to concrete start date)
periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
if "period" not in st.session_state:
    st.session_state.period = "1Y"

cols = st.columns(len(periods))
for i, p in enumerate(periods):
    if cols[i].button(p):
        st.session_state.period = p

period = st.session_state.period  # e.g., "1Y"

# Chart options
c1, c2 = st.columns(2)
with c1:
    chart_type = st.selectbox("Chart Type", ["Candle", "Line"])
with c2:
    if chart_type == "Line":
        indicators = st.selectbox("Indicator", ["RSI", "Moving Average", "MACD"])
    else:
        indicators = st.selectbox("Indicator", ["RSI", "MACD"])

rsi_window = st.slider("RSI Window", 5, 50, 14)

# Load full history and slice according to period selection
data_full = load_full_price(ticker)

if data_full.empty or "Close" not in data_full.columns:
    st.error("Error loading historical data. Check the ticker or internet connection.")
    st.stop()

# compute slice start based on selected period
def slice_for_period(df: pd.DataFrame, period: str, ref_date: datetime.date) -> pd.DataFrame:
    if period == "MAX":
        return df
    if period == "5D":
        start = ref_date - datetime.timedelta(days=7)  # include buffer for weekends
    elif period == "1M":
        start = ref_date - datetime.timedelta(days=30)
    elif period == "6M":
        start = ref_date - datetime.timedelta(days=182)
    elif period == "YTD":
        start = datetime.date(ref_date.year, 1, 1)
    elif period == "1Y":
        start = ref_date - datetime.timedelta(days=365)
    elif period == "5Y":
        start = ref_date - datetime.timedelta(days=365 * 5)
    else:
        start = ref_date - datetime.timedelta(days=365)
    # convert to timestamps compatible with df index
    # ensure we include the start day
    if isinstance(df.index, pd.DatetimeIndex):
        start_ts = pd.to_datetime(start)
        return df.loc[df.index >= start_ts]
    else:
        return df

sliced = slice_for_period(data_full, period, today)

if sliced.empty:
    st.warning("No historical data available for the selected period.")
else:
    # Chart rendering
    if chart_type == "Candle":
        # candlestick expects a dataframe with OHLC data
        st.plotly_chart(candlestick(sliced, period), use_container_width=True)

        if indicators == "RSI":
            st.plotly_chart(RSI(sliced, period, rsi_window), use_container_width=True)
        elif indicators == "MACD":
            st.plotly_chart(MACD(sliced, period), use_container_width=True)

    else:  # Line chart
        st.plotly_chart(close_chart(sliced, period), use_container_width=True)

        if indicators == "RSI":
            st.plotly_chart(RSI(sliced, period, rsi_window), use_container_width=True)
        elif indicators == "Moving Average":
            st.plotly_chart(Moving_average(sliced, period), use_container_width=True)
        elif indicators == "MACD":
            st.plotly_chart(MACD(sliced, period), use_container_width=True)
