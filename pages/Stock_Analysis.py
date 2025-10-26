import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📊 Stock Analysis",
    page_icon="💹",
    layout="wide",
)

st.title("📊 Stock Analysis")

# -------------------------------
# User input
# -------------------------------
col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input("🔎 Stock Ticker", "AAPL")
with col2:
    start_date = st.date_input("📅 Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

if ticker:
    st.subheader(f"🏢 {ticker} Overview")

    # -------------------------------
    # Fetch company info safely
    # -------------------------------
    stock = yf.Ticker(ticker)
    info = stock.info
    st.write(info.get('longBusinessSummary', '⚠️ Company summary temporarily unavailable'))
    st.write("💼 Sector:", info.get('sector', 'N/A'))
    st.write("👥 Full Time Employees:", info.get('fullTimeEmployees', 'N/A'))
    st.write("🌐 Website:", info.get('website', 'N/A'))

    # -------------------------------
    # Metrics tables
    # -------------------------------
    col1, col2 = st.columns(2)
    with col1:
        df1 = pd.DataFrame(index=['Market Cap', 'Beta', 'EPS', 'PE Ratio'])
        df1['Value'] = [
            info.get('marketCap', 'N/A'),
            info.get('beta', 'N/A'),
            info.get('trailingEps', 'N/A'),
            info.get('trailingPE', 'N/A')
        ]
        st.plotly_chart(plotly_table(df1), use_container_width=True)

    with col2:
        df2 = pd.DataFrame(index=['Quick Ratio', 'Revenue per share', 'Profit Margins', 'Debt to Equity', 'Return on Equity'])
        df2['Value'] = [
            info.get('quickRatio', 'N/A'),
            info.get('revenuePerShare', 'N/A'),
            info.get('profitMargins', 'N/A'),
            info.get('debtToEquity', 'N/A'),
            info.get('returnOnEquity', 'N/A')
        ]
        st.plotly_chart(plotly_table(df2), use_container_width=True)

    # -------------------------------
    # Historical data
    # -------------------------------
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        st.warning("❌ Please enter a valid stock ticker or check date range")
    else:
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else last_close
        daily_change = last_close - prev_close
        pct_change = (daily_change / prev_close * 100) if prev_close else 0

        col1, _, _ = st.columns(3)
        col1.metric("💰 Last Close", f"${last_close:.2f}", f"{daily_change:+.2f} ({pct_change:+.2f}%)")
        col3.metric("📊 Volume", f"{data['Volume'].iloc[-1]:,}")

        st.write("🗂️ Historical Data (Last 10 Days)")
        st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

        st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

        # -------------------------------
        # Period buttons
        # -------------------------------
        periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
        col_buttons = st.columns(len(periods))
        num_period = ''
        for i, p in enumerate(periods):
            if col_buttons[i].button(p):
                num_period = p.lower()
        if num_period == '':
            num_period = '1y'

        # -------------------------------
        # Chart type & indicator selection
        # -------------------------------
        col1, col2 = st.columns([1,1])
        with col1:
            chart_type = st.selectbox("📊 Chart Type", ("Candle", "Line"))
        with col2:
            if chart_type == "Candle":
                indicators = st.selectbox("📈 Indicator", ("RSI", "MACD"))
            else:
                indicators = st.selectbox("📈 Indicator", ("RSI", "Moving Average", "MACD"))

        # RSI slider
        rsi_window = st.slider("🔧 Select RSI Window (days)", 5, 50, 14)

        df_history = yf.Ticker(ticker).history(period="max")

        # -------------------------------
        # Chart rendering
        # -------------------------------
        if chart_type == "Candle":
            st.plotly_chart(candlestick(df_history, num_period), use_container_width=True)
            if indicators == "RSI":
                st.plotly_chart(RSI(df_history, num_period, window=rsi_window), use_container_width=True)
            elif indicators == "MACD":
                st.plotly_chart(MACD(df_history, num_period), use_container_width=True)
        else:
            if indicators == "RSI":
                st.plotly_chart(close_chart(df_history, num_period), use_container_width=True)
                st.plotly_chart(RSI(df_history, num_period, window=rsi_window), use_container_width=True)
            elif indicators == "Moving Average":
                st.plotly_chart(Moving_average(df_history, num_period), use_container_width=True)
            elif indicators == "MACD":
                st.plotly_chart(close_chart(df_history, num_period), use_container_width=True)
                st.plotly_chart(MACD(df_history, num_period), use_container_width=True)
