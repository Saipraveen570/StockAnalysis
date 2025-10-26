import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# --------------------------------------------------
# 🎨 Page Setup
# --------------------------------------------------
st.set_page_config(
    page_title="📊 Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
)
st.title("📈 Stock Analysis")

# --------------------------------------------------
# 🧠 Input Section
# --------------------------------------------------
col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input("🏦 Stock Ticker", "AAPL")
with col2:
    start_date = st.date_input("📅 Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

# --------------------------------------------------
# 🧾 Safe Data Fetching
# --------------------------------------------------
@st.cache_data(ttl=3600)
def get_stock_data(symbol, start, end):
    try:
        data = yf.download(symbol, start=start, end=end)
        return data
    except Exception as e:
        if "rate limit" in str(e).lower():
            st.warning("⚠️ Yahoo Finance API rate limit reached. Please try again later.")
        else:
            st.error(f"❌ Error fetching stock data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_stock_summary(symbol):
    try:
        stock = yf.Ticker(symbol)
        info = stock.get_info()
        return info
    except Exception as e:
        if "rate limit" in str(e).lower():
            st.warning("⚠️ Rate limit reached. Summary temporarily unavailable.")
        else:
            st.error(f"⚠️ Unable to fetch stock summary: {e}")
        return {}

# --------------------------------------------------
# 📊 Stock Summary
# --------------------------------------------------
info = get_stock_summary(ticker)
if info:
    st.subheader(f"🏢 {ticker} - Company Overview")
    st.write(info.get("longBusinessSummary", "No summary available"))
    st.write("**🌐 Website:**", info.get("website", "N/A"))
    st.write("**🏭 Sector:**", info.get("sector", "N/A"))
    st.write("**👥 Full-Time Employees:**", info.get("fullTimeEmployees", "N/A"))

    col1, col2 = st.columns(2)
    with col1:
        df1 = pd.DataFrame(index=["Market Cap", "Beta", "EPS", "PE Ratio"])
        df1[""] = [
            info.get("marketCap", "N/A"),
            info.get("beta", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("trailingPE", "N/A"),
        ]
        st.plotly_chart(plotly_table(df1), use_container_width=True)

    with col2:
        df2 = pd.DataFrame(
            index=["Quick Ratio", "Revenue per Share", "Profit Margins", "Debt to Equity", "Return on Equity"]
        )
        df2[""] = [
            info.get("quickRatio", "N/A"),
            info.get("revenuePerShare", "N/A"),
            info.get("profitMargins", "N/A"),
            info.get("debtToEquity", "N/A"),
            info.get("returnOnEquity", "N/A"),
        ]
        st.plotly_chart(plotly_table(df2), use_container_width=True)
else:
    st.warning("⚠️ Could not load company summary. Try again later.")

# --------------------------------------------------
# 📈 Stock Data and Charts
# --------------------------------------------------
data = get_stock_data(ticker, start_date, end_date)

if len(data) < 1:
    st.error("❌ Please enter a valid stock ticker symbol.")
else:
    st.markdown("---")

    # Daily metrics
    col1, col2, col3 = st.columns(3)
    daily_change = data["Close"].iloc[-1] - data["Close"].iloc[-2]
    pct_change = (daily_change / data["Close"].iloc[-2]) * 100

    col1.metric("💰 Last Close", f"${round(data['Close'].iloc[-1], 2)}", f"{round(daily_change, 2)}")
    col2.metric("📉 % Change", f"{round(pct_change, 2)}%")
    col3.metric("📊 Volume", f"{data['Volume'].iloc[-1]:,}")

    # Recent table
    st.write("### 🗓️ Recent 10-Day Data")
    data.index = [str(i)[:10] for i in data.index]
    fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
    fig_tail.update_layout(height=230)
    st.plotly_chart(fig_tail, use_container_width=True)

    # --------------------------------------------------
    # 🧭 Chart Options
    # --------------------------------------------------
    st.markdown("---")
    st.write("### 📊 Visualization Options")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        chart_type = st.selectbox("📉 Chart Type", ("Candle", "Line"))
    with col2:
        if chart_type == "Candle":
            indicator = st.selectbox("📈 Indicator", ("RSI", "MACD"))
        else:
            indicator = st.selectbox("📈 Indicator", ("RSI", "Moving Average", "MACD"))
    with col3:
        period = st.selectbox("⏱️ Time Period", ("5d", "1mo", "6mo", "ytd", "1y", "5y", "max"))

    ticker_obj = yf.Ticker(ticker)
    hist_data = ticker_obj.history(period=period)

    if chart_type == "Candle":
        st.plotly_chart(candlestick(hist_data, period), use_container_width=True)
        if indicator == "RSI":
            st.plotly_chart(RSI(hist_data, period), use_container_width=True)
        elif indicator == "MACD":
            st.plotly_chart(MACD(hist_data, period), use_container_width=True)

    elif chart_type == "Line":
        if indicator == "RSI":
            st.plotly_chart(close_chart(hist_data, period), use_container_width=True)
            st.plotly_chart(RSI(hist_data, period), use_container_width=True)
        elif indicator == "Moving Average":
            st.plotly_chart(Moving_average(hist_data, period), use_container_width=True)
        elif indicator == "MACD":
            st.plotly_chart(close_chart(hist_data, period), use_container_width=True)
            st.plotly_chart(MACD(hist_data, period), use_container_width=True)

# --------------------------------------------------
# ✅ End
# --------------------------------------------------
st.markdown("---")
st.caption("📊 Built with ❤️ using Streamlit, Plotly & Yahoo Finance")
