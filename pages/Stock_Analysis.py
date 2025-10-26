# pages/Stock_Analysis.py
import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD
import ta

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
    ticker = st.text_input('🔎 Stock Ticker', 'AAPL')
with col2:
    start_date = st.date_input("📅 Start Date", datetime.date(today.year-1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

st.subheader(f"🏢 {ticker} Overview")

# -------------------------------
# Fetch company info
# -------------------------------
try:
    stock = yf.Ticker(ticker)
    info = stock.info
    st.write(info.get('longBusinessSummary', '⚠️ Summary unavailable'))
    st.write("💼 Sector:", info.get('sector', 'N/A'))
    st.write("👥 Full Time Employees:", info.get('fullTimeEmployees', 'N/A'))
    st.write("🌐 Website:", info.get('website', 'N/A'))
except Exception:
    st.warning("⚠️ Could not load company information. Try again later.")

# -------------------------------
# Metrics tables
# -------------------------------
try:
    col1, col2 = st.columns(2)
    with col1:
        df1 = pd.DataFrame(index=['Market Cap','Beta','EPS','PE Ratio'])
        df1['Value'] = [info.get("marketCap"), info.get("beta"), info.get("trailingEps"), info.get("trailingPE")]
        st.plotly_chart(plotly_table(df1), use_container_width=True)
    with col2:
        df2 = pd.DataFrame(index=['Quick Ratio','Revenue per share','Profit Margins','Debt to Equity','Return on Equity'])
        df2['Value'] = [info.get("quickRatio"), info.get("revenuePerShare"),
                         info.get("profitMargins"), info.get("debtToEquity"),
                         info.get("returnOnEquity")]
        st.plotly_chart(plotly_table(df2), use_container_width=True)
except Exception:
    st.warning("⚠️ Could not load financial metrics. Try again later.")

# -------------------------------
# Historical data & daily metrics
# -------------------------------
try:
    data = yf.download(ticker, start=start_date, end=end_date)
    if len(data) < 1:
        st.warning('❌ Please enter a valid stock ticker')
    else:
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else None
        daily_change = last_close - prev_close if prev_close is not None else 0
        pct_change = (daily_change / prev_close * 100) if prev_close not in [0, None] else 0

        col1, _, _ = st.columns(3)
        col1.metric("📈 Daily Close", f"${last_close:.2f}", f"{daily_change:+.2f} ({pct_change:+.2f}%)")

        data.index = [str(i)[:10] for i in data.index]
        st.write('🗂️ Historical Data (Last 10 days)')
        st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

        # -------------------------------
        # Moving Average Chart
        # -------------------------------
        data['MA7'] = data['Close'].rolling(7).mean()
        st.plotly_chart(Moving_average(data.iloc[-150:]), use_container_width=True)

except Exception:
    st.warning("⚠️ Could not load historical data or chart. Try again later.")
