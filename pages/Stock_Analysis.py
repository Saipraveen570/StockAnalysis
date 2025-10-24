import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime
import ta
from pages.utils.plotly_figure import (
    plotly_table,
    close_chart,
    candlestick,
    RSI,
    Moving_average,
    MACD
)

# ---------------- Page Setup ----------------
st.set_page_config(
    page_title="Stock Analysis",
    page_icon="📊",
    layout="wide",
)
st.title("📈 Stock Analysis")

# ---------------- Input Section ----------------
col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')
with col2:
    start_date = st.date_input("Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("End Date", today)

st.subheader(f"{ticker} — Company Overview")

# ---------------- Company Info ----------------
try:
    stock = yf.Ticker(ticker)
    info = stock.info

    st.write(info.get("longBusinessSummary", "No business summary available."))
    st.write("**Sector:**", info.get("sector", "N/A"))
    st.write("**Full Time Employees:**", info.get("fullTimeEmployees", "N/A"))
    st.write("**Website:**", info.get("website", "N/A"))

    col1, col2 = st.columns(2)

    # Financial summary 1
    with col1:
        df1 = pd.DataFrame(index=["Market Cap", "Beta", "EPS", "PE Ratio"])
        df1["Value"] = [
            info.get("marketCap", "N/A"),
            info.get("beta", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("trailingPE", "N/A"),
        ]
        fig1 = plotly_table(df1)
        st.plotly_chart(fig1, use_container_width=True)

    # Financial summary 2
    with col2:
        df2 = pd.DataFrame(index=["Quick Ratio", "Revenue/Share", "Profit Margins", "Debt/Equity", "Return on Equity"])
        df2["Value"] = [
            info.get("quickRatio", "N/A"),
            info.get("revenuePerShare", "N/A"),
            info.get("profitMargins", "N/A"),
            info.get("debtToEquity", "N/A"),
            info.get("returnOnEquity", "N/A"),
        ]
        fig2 = plotly_table(df2)
        st.plotly_chart(fig2, use_container_width=True)

except Exception as e:
    st.warning("⚠️ Unable to fetch company details. Please check ticker symbol.")

# ---------------- Historical Data ----------------
data = yf.download(ticker, start=start_date, end=end_date)

if data.empty:
    st.error("❌ Invalid ticker or no data found. Please enter a valid symbol (e.g., AAPL, MSFT).")
    st.stop()

col1, col2, col3 = st.columns(3)
daily_change = data["Close"].iloc[-1] - data["Close"].iloc[-2]

col1.metric("Last Close", round(data["Close"].iloc[-1], 2))
col2.metric("Daily Change", round(daily_change, 2))
col3.metric("Volume", f"{int(data['Volume'].iloc[-1]):,}")

data.index = [str(i)[:10] for i in data.index]
fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
fig_tail.update_layout(height=220)
st.write("##### Historical Data (Last 10 days)")
st.plotly_chart(fig_tail, use_container_width=True)

st.markdown(
    """<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""",
    unsafe_allow_html=True,
)

# ---------------- Styling ----------------
st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #e1efff;
        color: black;
        font-weight: 500;
    }
    div.stButton > button:hover {
        background-color: #0078ff;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Time Period Buttons ----------------
cols = st.columns(12)
period_buttons = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
period_map = {"5D": "5d", "1M": "1mo", "6M": "6mo", "YTD": "ytd", "1Y": "1y", "5Y": "5y", "MAX": "max"}
num_period = ""

for i, p in enumerate(period_buttons):
    with cols[i]:
        if st.button(p):
            num_period = period_map[p]

# ---------------- Chart Type & Indicators ----------------
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    chart_type = st.selectbox("Chart Type", ("Candle", "Line"))
with col2:
    if chart_type == "Candle":
        indicator = st.selectbox("Indicator", ("RSI", "MACD"))
    else:
        indicator = st.selectbox("Indicator", ("RSI", "Moving Average", "MACD"))

# ---------------- Data for Charts ----------------
ticker_data = yf.Ticker(ticker)
hist_data = ticker_data.history(period="max")

# Default display: 1 year if no button pressed
period_to_use = num_period if num_period else "1y"

# ---------------- Chart Rendering ----------------
try:
    if chart_type == "Candle":
        st.plotly_chart(candlestick(hist_data, period_to_use), use_container_width=True)
        if indicator == "RSI":
            st.plotly_chart(RSI(hist_data, period_to_use), use_container_width=True)
        elif indicator == "MACD":
            st.plotly_chart(MACD(hist_data, period_to_use), use_container_width=True)

    elif chart_type == "Line":
        if indicator == "RSI":
            st.plotly_chart(close_chart(hist_data, period_to_use), use_container_width=True)
            st.plotly_chart(RSI(hist_data, period_to_use), use_container_width=True)
        elif indicator == "Moving Average":
            st.plotly_chart(Moving_average(hist_data, period_to_use), use_container_width=True)
        elif indicator == "MACD":
            st.plotly_chart(close_chart(hist_data, period_to_use), use_container_width=True)
            st.plotly_chart(MACD(hist_data, period_to_use), use_container_width=True)

except Exception as e:
    st.error(f"⚠️ Error rendering charts: {e}")

st.caption("📊 Note: Data and metrics provided by Yahoo Finance. For informational use only.")
