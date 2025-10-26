import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="Stock Analysis",
    page_icon="💹",
    layout="wide",
)

st.title("Stock Analysis")

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
    st.write(stock.info.get('longBusinessSummary', '⚠️ Summary temporarily unavailable.'))
    st.write("💼 Sector:", stock.info.get('sector', 'N/A'))
    st.write("👥 Full Time Employees:", stock.info.get('fullTimeEmployees', 'N/A'))
    st.write("🌐 Website:", stock.info.get('website', 'N/A'))
except Exception:
    st.warning("⚠️ Could not load company summary. Try again later.")

# -------------------------------
# Metrics tables
# -------------------------------
col1, col2 = st.columns(2)
try:
    with col1:
        df1 = pd.DataFrame(index=['Market Cap','Beta','EPS','PE Ratio'])
        df1['Value'] = [stock.info.get("marketCap"), stock.info.get("beta"), stock.info.get("trailingEps"), stock.info.get("trailingPE")]
        st.plotly_chart(plotly_table(df1), use_container_width=True)

    with col2:
        df2 = pd.DataFrame(index=['Quick Ratio','Revenue per share','Profit Margins','Debt to Equity','Return on Equity'])
        df2['Value'] = [stock.info.get("quickRatio"), stock.info.get("revenuePerShare"),
                         stock.info.get("profitMargins"), stock.info.get("debtToEquity"),
                         stock.info.get("returnOnEquity")]
        st.plotly_chart(plotly_table(df2), use_container_width=True)
except Exception:
    st.warning("⚠️ Could not load metrics table.")

# -------------------------------
# Historical data
# -------------------------------
data = yf.download(ticker, start=start_date, end=end_date)

if len(data) < 1:
    st.warning('❌ Please enter a valid stock ticker')
else:
    # -------------------------------
    # Calculate last close, previous close safely
    # -------------------------------
    last_close = data['Close'].iloc[-1]
    prev_close = data['Close'].iloc[-2] if len(data) > 1 else None

    if prev_close is not None and not pd.isna(prev_close):
        daily_change = last_close - prev_close
        pct_change = (daily_change / prev_close) * 100
    else:
        daily_change = 0
        pct_change = 0

    col1.metric("📈 Last Close", f"${last_close:.2f}", f"{daily_change:+.2f} ({pct_change:+.2f}%)")

    data.index = [str(i)[:10] for i in data.index]
    st.write('🗂️ Historical Data (Last 10 days)')
    st.plotly_chart(plotly_table(data.tail(10).sort_index(ascending=False).round(3)), use_container_width=True)

# -------------------------------
# Charts
# -------------------------------
df_history = yf.Ticker(ticker).history(period='max')

st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""", unsafe_allow_html=True)

st.subheader("📊 Stock Charts")

# Candlestick & Indicators
st.plotly_chart(candlestick(df_history, '1y'), use_container_width=True)
st.plotly_chart(close_chart(df_history, '1y'), use_container_width=True)
st.plotly_chart(RSI(df_history, '1y', window=14), use_container_width=True)
st.plotly_chart(Moving_average(df_history, '1y'), use_container_width=True)
st.plotly_chart(MACD(df_history, '1y'), use_container_width=True)
