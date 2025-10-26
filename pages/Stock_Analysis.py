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
    start_date = st.date_input("📅 Start Date", datetime.date(today.year-1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

if ticker:
    st.subheader(f"🏢 {ticker} Overview")

    # -------------------------------
    # Fetch company info
    # -------------------------------
    stock = yf.Ticker(ticker)
    st.write(stock.info.get('longBusinessSummary', '⚠️ Summary temporarily unavailable.'))
    st.write("💼 Sector:", stock.info.get('sector', 'N/A'))
    st.write("👥 Full Time Employees:", stock.info.get('fullTimeEmployees', 'N/A'))
    st.write("🌐 Website:", stock.info.get('website', 'N/A'))

    # -------------------------------
    # Metrics tables
    # -------------------------------
    col1, col2 = st.columns(2)
    with col1:
        df1 = pd.DataFrame(index=['Market Cap','Beta','EPS','PE Ratio'])
        df1['Value'] = [
            stock.info.get("marketCap"), stock.info.get("beta"),
            stock.info.get("trailingEps"), stock.info.get("trailingPE")
        ]
        st.plotly_chart(plotly_table(df1), use_container_width=True)
    with col2:
        df2 = pd.DataFrame(index=['Quick Ratio','Revenue per share','Profit Margins','Debt to Equity','Return on Equity'])
        df2['Value'] = [
            stock.info.get("quickRatio"), stock.info.get("revenuePerShare"),
            stock.info.get("profitMargins"), stock.info.get("debtToEquity"),
            stock.info.get("returnOnEquity")
        ]
        st.plotly_chart(plotly_table(df2), use_container_width=True)

    # -------------------------------
    # Historical stock data
    # -------------------------------
    data = yf.download(ticker, start=start_date, end=end_date)
    if len(data) < 1:
        st.warning('❌ Please enter a valid stock ticker')
    else:
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2] if len(data) > 1 else None
        daily_change = last_close - prev_close if prev_close is not None else 0
        pct_change = (daily_change / prev_close * 100) if prev_close is not None and pd.notna(prev_close) else 0

        col1, _, _ = st.columns(3)
        col1.metric("📈 Last Close", f"${last_close:.2f}", f"{daily_change:+.2f} ({pct_change:+.2f}%)")

        # Display last 10 rows
        data.index = [str(i)[:10] for i in data.index]
        st.write("🗂️ Historical Data (Last 10 Days)")
        st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

        st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

        # -------------------------------
        # Charts
        # -------------------------------
        st.write("📊 Stock Chart")
        st.plotly_chart(candlestick(data, period="1y"), use_container_width=True)
        st.plotly_chart(close_chart(data, period="1y"), use_container_width=True)
        st.plotly_chart(RSI(data, period="1y", window=14), use_container_width=True)
        st.plotly_chart(Moving_average(data, period="1y"), use_container_width=True)
        st.plotly_chart(MACD(data, period="1y"), use_container_width=True)
