import streamlit as st
import pandas as pd 
import yfinance as yf 
import datetime
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# setting page config
st.set_page_config(
        page_title="Stock Analysis",
        page_icon="page_with_curl",
        layout="wide",
)

st.title("Stock Analysis")

col1, col2, col3 = st.columns(3)
today = datetime.date.today()

with col1:
    ticker = st.text_input('Stock Ticker', 'AAPL')
with col2:
    start_date = st.date_input("Start Date", datetime.date(today.year-1, today.month, today.day))
with col3:
    end_date = st.date_input("End Date", datetime.date(today.year, today.month, today.day))

st.subheader(ticker)

# Fetch stock info safely
stock = yf.Ticker(ticker)
try:
    info = stock.get_info()
except Exception:
    info = {}

st.write(info.get('longBusinessSummary', 'Summary not available'))
st.write("**Sector:**", info.get('sector', 'N/A'))
st.write("**Full Time Employees:**", info.get('fullTimeEmployees', 'N/A'))
st.write("**Website:**", info.get('website', 'N/A'))

# Display metrics table safely
col1, col2 = st.columns(2)
with col1:
    df = pd.DataFrame(index=['Market Cap', 'Beta', 'EPS', 'PE Ratio'])
    df[''] = [
        info.get("marketCap", "N/A"),
        info.get("beta", "N/A"),
        info.get("trailingEps", "N/A"),
        info.get("trailingPE", "N/A")
    ]
    fig_df = plotly_table(df)
    st.plotly_chart(fig_df, use_container_width=True)

with col2:
    df = pd.DataFrame(index=['Qucik Ratio', 'Revenue per share', 'Profit Margins', 'Debt to Equity', 'Return on Equity'])
    df[''] = [
        info.get("quickRatio", "N/A"),
        info.get("revenuePerShare", "N/A"),
        info.get("profitMargins", "N/A"),
        info.get("debtToEquity", "N/A"),
        info.get("returnOnEquity", "N/A")
    ]
    fig_df = plotly_table(df)
    st.plotly_chart(fig_df, use_container_width=True)

# Fetch price data safely
try:
    data = yf.download(ticker, start=start_date, end=end_date)
except Exception:
    st.error("Unable to fetch price data. Try a different ticker.")
    st.stop()

if len(data) < 1:
    st.write('##### Please write the name of valid Ticker')
else:
    col1, col2, col3 = st.columns(3)
    daily_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
    col1.metric("Daily Close", round(data['Close'].iloc[-1], 2), round(daily_change, 2))

    data.index = [str(i)[:10] for i in data.index]
    fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
    fig_tail.update_layout(height=220)
    st.write('##### Historical Data (Last 10 days)')
    st.plotly_chart(fig_tail, use_container_width=True)

    st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" /> """, unsafe_allow_html=True)

    # Buttons
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            background-color: #e1efff;
            color:black;
        }
        div.stButton > button:hover {
            background-color: #0078ff;
            color:white;
        }
        </style>""", unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns([1]*12)

    num_period = ''
    if col1.button('5D'): num_period = '5d'
    if col2.button('1M'): num_period = '1mo'
    if col3.button('6M'): num_period = '6mo'
    if col4.button('YTD'): num_period = 'ytd'
    if col5.button('1Y'): num_period = '1y'
    if col6.button('5Y'): num_period = '5y'
    if col7.button('MAX'): num_period = 'max'

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        chart_type = st.selectbox('',('Candle','Line'))
    with col2:
        indicators = st.selectbox('',('RSI','MACD','Moving Average') if chart_type=="Line" else ('RSI','MACD'))

    ticker_ = yf.Ticker(ticker)
    data1 = ticker_.history(period='max')

    if num_period:
        df_plot = data1
        period = num_period
    else:
        df_plot = data1
        period = '1y'

    if chart_type == 'Candle':
        st.plotly_chart(candlestick(df_plot, period), use_container_width=True)
        if indicators == 'RSI': st.plotly_chart(RSI(df_plot, period), use_container_width=True)
        if indicators == 'MACD': st.plotly_chart(MACD(df_plot, period), use_container_width=True)

    else:
        if indicators == 'Moving Average':
            st.plotly_chart(Moving_average(df_plot, period), use_container_width=True)
        else:
            st.plotly_chart(close_chart(df_plot, period), use_container_width=True)
            if indicators == 'RSI': st.plotly_chart(RSI(df_plot, period), use_container_width=True)
            if indicators == 'MACD': st.plotly_chart(MACD(df_plot, period), use_container_width=True)
