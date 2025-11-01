import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import time
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="wide")
st.title("Stock Analysis")

@st.cache_data(ttl=300)
def safe_get_info(ticker):
    stock = yf.Ticker(ticker)
    retries = 3
    for _ in range(retries):
        try:
            return stock.get_info()
        except Exception:
            time.sleep(1.5)
    return {}

@st.cache_data(ttl=300)
def safe_download(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, progress=False)
        if data is None or data.empty:
            return pd.DataFrame()
        return data
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=300)
def safe_history(ticker):
    stock = yf.Ticker(ticker)
    retries = 3
    for _ in range(retries):
        try:
            data = stock.history(period="max")
            if not data.empty:
                return data
        except Exception:
            time.sleep(1.5)
    return pd.DataFrame()

col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input("Stock Ticker", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", datetime.date(today.year-1, today.month, today.day))
with col3:
    end_date = st.date_input("End Date", today)

info = safe_get_info(ticker)

if not info:
    st.warning("Unable to fetch company info due to Yahoo Finance rate limits. Try again later.")
else:
    st.subheader(info.get("longName", ticker))
    st.write(info.get("longBusinessSummary", "Description unavailable"))

    stats1 = pd.DataFrame({
        "": ["Market Cap", "Beta", "EPS", "PE Ratio"],
        "Value": [
            info.get("marketCap", "N/A"),
            info.get("beta", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("trailingPE", "N/A"),
        ],
    }).set_index("")

    stats2 = pd.DataFrame({
        "": ["Quick Ratio", "Revenue/Share", "Profit Margin", "Debt/Equity", "ROE"],
        "Value": [
            info.get("quickRatio", "N/A"),
            info.get("revenuePerShare", "N/A"),
            info.get("profitMargins", "N/A"),
            info.get("debtToEquity", "N/A"),
            info.get("returnOnEquity", "N/A"),
        ],
    }).set_index("")

    colA, colB = st.columns(2)
    colA.plotly_chart(plotly_table(stats1), use_container_width=True)
    colB.plotly_chart(plotly_table(stats2), use_container_width=True)

data = safe_download(ticker, start_date, end_date)

if data.empty:
    st.error("Price data unavailable. Ticker may be incorrect or API temporarily blocked.")
else:
    colA, colB, colC = st.columns(3)
    if len(data) > 1:
        daily_change = data["Close"].iloc[-1] - data["Close"].iloc[-2]
        colA.metric("Daily Close", round(data["Close"].iloc[-1], 2), round(daily_change, 2))

    data.index = [str(i)[:10] for i in data.index]
    fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
    fig_tail.update_layout(height=220)
    st.write("##### Historical Data (Last 10 days)")
    st.plotly_chart(fig_tail, use_container_width=True)

st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

period_buttons = ["5d","1mo","6mo","ytd","1y","5y","max"]
labels = ["5D","1M","6M","YTD","1Y","5Y","MAX"]
period = ""

cols = st.columns(len(labels))
for c, p, l in zip(cols, period_buttons, labels):
    if c.button(l):
        period = p

col1, col2, _ = st.columns([1,1,4])
chart_type = col1.selectbox("", ["Candle", "Line"])
indicators = col2.selectbox("", ["RSI","Moving Average","MACD"] if chart_type=="Line" else ["RSI","MACD"])

hist = safe_history(ticker)

if hist.empty:
    st.error("Unable to load full history (API limit reached). Try again later.")
else:
    plot_period = period if period else "1y"

    if chart_type == "Candle":
        st.plotly_chart(candlestick(hist, plot_period), use_container_width=True)
        if indicators == "RSI":
            st.plotly_chart(RSI(hist, plot_period), use_container_width=True)
        if indicators == "MACD":
            st.plotly_chart(MACD(hist, plot_period), use_container_width=True)

    else:
        if indicators == "Moving Average":
            st.plotly_chart(Moving_average(hist, plot_period), use_container_width=True)
        else:
            st.plotly_chart(close_chart(hist, plot_period), use_container_width=True)
            if indicators == "RSI":
                st.plotly_chart(RSI(hist, plot_period), use_container_width=True)
            if indicators == "MACD":
                st.plotly_chart(MACD(hist, plot_period), use_container_width=True)
