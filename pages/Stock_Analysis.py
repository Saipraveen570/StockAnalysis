import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# --- Page config ---
st.set_page_config(
    page_title="📊 Stock Analysis",
    page_icon="💹",
    layout="wide",
)

st.title("📊 Stock Analysis")

# --- Columns for input ---
col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input('🔎 Stock Ticker', 'AAPL')
with col2:
    start_date = st.date_input("📅 Start Date", datetime.date(today.year-1, today.month, today.day))
with col3:
    end_date = st.date_input("📅 End Date", today)

st.subheader(f"🏢 {ticker} Overview")

# --- Company Info ---
stock = yf.Ticker(ticker)
st.write(stock.info.get('longBusinessSummary', '⚠️ Summary temporarily unavailable.'))

st.write("💼 Sector:", stock.info.get('sector', 'N/A'))
st.write("👥 Full Time Employees:", stock.info.get('fullTimeEmployees', 'N/A'))
st.write("🌐 Website:", stock.info.get('website', 'N/A'))

# --- Metrics tables ---
col1, col2 = st.columns(2)
with col1:
    df1 = pd.DataFrame(index=['Market Cap','Beta','EPS','PE Ratio'])
    df1['Value'] = [
        stock.info.get("marketCap", 0),
        stock.info.get("beta", 0),
        stock.info.get("trailingEps", 0),
        stock.info.get("trailingPE", 0)
    ]
    st.plotly_chart(plotly_table(df1), use_container_width=True)
with col2:
    df2 = pd.DataFrame(index=['Quick Ratio','Revenue per share','Profit Margins','Debt to Equity','Return on Equity'])
    df2['Value'] = [
        stock.info.get("quickRatio", 0),
        stock.info.get("revenuePerShare", 0),
        stock.info.get("profitMargins", 0),
        stock.info.get("debtToEquity", 0),
        stock.info.get("returnOnEquity", 0)
    ]
    st.plotly_chart(plotly_table(df2), use_container_width=True)

# --- Historical Data ---
data = yf.download(ticker, start=start_date, end=end_date)
if len(data) < 1:
    st.warning('❌ Please enter a valid stock ticker')
else:
    # Safely calculate metrics
    if len(data) > 1:
        last_close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]

        if pd.isna(last_close) or pd.isna(prev_close):
            last_close = 0
            prev_close = 0

        daily_change = last_close - prev_close
        pct_change = (daily_change / prev_close * 100) if prev_close != 0 else 0
    else:
        last_close = 0
        daily_change = 0
        pct_change = 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Daily Close", f"${last_close:.2f}", f"{daily_change:+.2f}")
    col2.metric("📉 % Change", f"{pct_change:+.2f}%")
    col3.metric("💰 Volume", f"{data['Volume'].iloc[-1]:,}" if len(data) > 0 else "0")

    # Historical table
    data.index = [str(i)[:10] for i in data.index]
    st.write('🗂️ Historical Data (Last 10 days)')
    st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

    st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

    # --- Period buttons ---
    periods = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
    col_buttons = st.columns(len(periods))
    num_period = ''
    for i, p in enumerate(periods):
        if col_buttons[i].button(f"{p}"):
            num_period = p.lower()
    if num_period == '':
        num_period = '1y'

    # --- Chart type & indicators ---
    col1, col2 = st.columns([1,1])
    with col1:
        chart_type = st.selectbox('📊 Chart Type', ('Candle','Line'))
    with col2:
        if chart_type == 'Candle':
            indicators = st.selectbox('📈 Indicator', ('RSI','MACD'))
        else:
            indicators = st.selectbox('📈 Indicator', ('RSI','Moving Average','MACD'))

    # RSI window slider
    rsi_window = st.slider("🔧 Select RSI Window (days)", 5, 50, 14)

    df_history = yf.Ticker(ticker).history(period='max')

    # --- Render charts ---
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
