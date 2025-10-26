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
# User Inputs
# -------------------------------
col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input('🔎 Stock Ticker', 'AAPL')
with col2:
    start_date = st.date_input("📅 Start Date", datetime.date(today.year-1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

if ticker:
    st.subheader(f"🏢 {ticker} Overview")

    # Fetch company info safely
    stock = yf.Ticker(ticker)
    info = stock.info

    st.write(info.get('longBusinessSummary', '⚠️ Summary unavailable'))
    st.write("💼 Sector:", info.get('sector', 'N/A'))
    st.write("👥 Full Time Employees:", info.get('fullTimeEmployees', 'N/A'))
    st.write("🌐 Website:", info.get('website', 'N/A'))

    # Metrics tables
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

    # -------------------------------
    # Historical Data
    # -------------------------------
    data = yf.download(ticker, start=start_date, end=end_date)
    if len(data) < 2:
        st.warning('❌ Please enter a valid stock ticker or increase date range')
    else:
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]
        daily_change = last_close - prev_close
        pct_change = (daily_change / prev_close * 100) if prev_close != 0 else 0

        col1, _, _ = st.columns(3)
        col1.metric("📈 Daily Close", f"${last_close:.2f}", f"{daily_change:+.2f} ({pct_change:+.2f}%)")

        # Last 10 days table
        data.index = [str(i)[:10] for i in data.index]
        st.write('🗂️ Historical Data (Last 10 days)')
        st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

        # -------------------------------
        # Chart Options
        # -------------------------------
        st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

        # Period buttons
        periods = ["5D","1M","6M","YTD","1Y","5Y","MAX"]
        col_buttons = st.columns(len(periods))
        num_period = '1y'
        for i, p in enumerate(periods):
            if col_buttons[i].button(f"{p}"):
                num_period = p.lower()

        # Chart type & indicator
        col1, col2 = st.columns([1,1])
        with col1:
            chart_type = st.selectbox('📊 Chart Type', ('Candle','Line'))
        with col2:
            if chart_type == 'Candle':
                indicators = st.selectbox('📈 Indicator', ('RSI','MACD'))
            else:
                indicators = st.selectbox('📈 Indicator', ('RSI','Moving Average','MACD'))

        # RSI Window
        rsi_window = st.slider("🔧 RSI Window (days)", 5, 50, 14)

        df_history = yf.Ticker(ticker).history(period='max')

        # -------------------------------
        # Plot Charts
        # -------------------------------
        if chart_type == 'Candle':
            st.plotly_chart(candlestick(df_history, num_period), use_container_width=True)
            if indicators == 'RSI':
                st.plotly_chart(RSI(df_history, num_period, window=rsi_window), use_container_width=True)
            elif indicators == 'MACD':
                st.plotly_chart(MACD(df_history, num_period), use_container_width=True)
        else:
            if indicators == 'RSI':
                st.plotly_chart(close_chart(df_history, num_period), use_container_width=True)
                st.plotly_chart(RSI(df_history, num_period, window=rsi_window), use_container_width=True)
            elif indicators == 'Moving Average':
                st.plotly_chart(Moving_average(df_history, num_period), use_container_width=True)
            elif indicators == 'MACD':
                st.plotly_chart(close_chart(df_history, num_period), use_container_width=True)
                st.plotly_chart(MACD(df_history, num_period), use_container_width=True)
