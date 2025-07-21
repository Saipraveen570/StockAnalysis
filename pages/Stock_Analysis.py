import streamlit as st
import pandas as pd 
import yfinance as yf 
import plotly.graph_objects as go 
import datetime
import ta 
from pages.utils.plotly_figure import plotly_table, close_chart, candlestick, RSI, Moving_average, MACD

# setting page config
st.set_page_config(
        page_title="Stock Analysis",
        page_icon="📄",
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
    st.write(stock.info['longBusinessSummary'])
    st.write("**Sector:**", stock.info['sector'])
    st.write("**Full Time Employees:**", stock.info['fullTimeEmployees'])
    st.write("**Website:**", stock.info['website'])
except Exception:
    st.error("⚠️ Could not retrieve stock info. The ticker might be invalid or data may not be available.")

col1, col2 = st.columns(2)

# Stock metrics
with col1:
    try:
        df = pd.DataFrame(index=['Market Cap', 'Beta', 'EPS', 'PE Ratio'])
        df[''] = [
            stock.info["marketCap"],
            stock.info["beta"],
            stock.info["trailingEps"],
            stock.info["trailingPE"]
        ]
        fig_df = plotly_table(df)
        st.plotly_chart(fig_df, use_container_width=True)
    except Exception:
        st.warning("⚠️ Unable to load some financial metrics.")

with col2:
    try:
        df = pd.DataFrame(index=['Quick Ratio', 'Revenue per Share', 'Profit Margins',
                                 'Debt to Equity', 'Return on Equity'])
        df[''] = [
            stock.info["quickRatio"],
            stock.info["revenuePerShare"],
            stock.info["profitMargins"],
            stock.info["debtToEquity"],
            stock.info["returnOnEquity"]
        ]
        fig_df = plotly_table(df)
        st.plotly_chart(fig_df, use_container_width=True)
    except Exception:
        st.warning("⚠️ Unable to load some company ratios.")

# Download historical stock data
data = yf.download(ticker, start=start_date, end=end_date)

if len(data) < 1:
    st.write('##### Please enter a valid stock ticker.')
else:
    col1, col2, col3 = st.columns(3)
    daily_change = data['Close'].iloc[-1] - data['Close'].iloc[-2]
    col1.metric("Daily Change", str(round(data['Close'].iloc[-1], 2)), str(round(daily_change, 2)))

    data.index = [str(i)[:10] for i in data.index]
    fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
    fig_tail.update_layout(height=220)
    st.write('##### Historical Data (Last 10 days)')
    st.plotly_chart(fig_tail, use_container_width=True)

    st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" /> """, unsafe_allow_html=True)

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

    # Time range buttons
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12 = st.columns([1]*12)
    num_period = ''
    if col1.button('5D'): num_period = '5d'
    if col2.button('1M'): num_period = '1mo'
    if col3.button('6M'): num_period = '6mo'
    if col4.button('YTD'): num_period = 'ytd'
    if col5.button('1Y'): num_period = '1y'
    if col6.button('5Y'): num_period = '5y'
    if col7.button('MAX'): num_period = 'max'

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        chart_type = st.selectbox('', ('Candle', 'Line'))
    with col2:
        if chart_type == 'Candle':
            indicators = st.selectbox('', ('RSI', 'MACD'))
        else:
            indicators = st.selectbox('', ('RSI', 'Moving Average', 'MACD'))

    # Charting
    try:
        ticker_ = yf.Ticker(ticker)
        new_df1 = ticker_.history(period='max')
        data1 = ticker_.history(period='max')

        if num_period == '':
            if chart_type == 'Candle' and indicators == 'RSI':
                st.plotly_chart(candlestick(data1, '1y'), use_container_width=True)
                st.plotly_chart(RSI(data1, '1y'), use_container_width=True)
            elif chart_type == 'Candle' and indicators == 'MACD':
                st.plotly_chart(candlestick(data1, '1y'), use_container_width=True)
                st.plotly_chart(MACD(data1, '1y'), use_container_width=True)
            elif chart_type == 'Line' and indicators == 'RSI':
                st.plotly_chart(close_chart(data1, '1y'), use_container_width=True)
                st.plotly_chart(RSI(data1, '1y'), use_container_width=True)
            elif chart_type == 'Line' and indicators == 'Moving Average':
                st.plotly_chart(Moving_average(data1, '1y'), use_container_width=True)
            elif chart_type == 'Line' and indicators == 'MACD':
                st.plotly_chart(close_chart(data1, '1y'), use_container_width=True)
                st.plotly_chart(MACD(data1, '1y'), use_container_width=True)
        else:
            if chart_type == 'Candle' and indicators == 'RSI':
                st.plotly_chart(candlestick(new_df1, num_period), use_container_width=True)
                st.plotly_chart(RSI(new_df1, num_period), use_container_width=True)
            elif chart_type == 'Candle' and indicators == 'MACD':
                st.plotly_chart(candlestick(new_df1, num_period), use_container_width=True)
                st.plotly_chart(MACD(new_df1, num_period), use_container_width=True)
            elif chart_type == 'Line' and indicators == 'RSI':
                st.plotly_chart(close_chart(new_df1, num_period), use_container_width=True)
                st.plotly_chart(RSI(new_df1, num_period), use_container_width=True)
            elif chart_type == 'Line' and indicators == 'Moving Average':
                st.plotly_chart(Moving_average(new_df1, num_period), use_container_width=True)
            elif chart_type == 'Line' and indicators == 'MACD':
                st.plotly_chart(close_chart(new_df1, num_period), use_container_width=True)
                st.plotly_chart(MACD(new_df1, num_period), use_container_width=True)
    except Exception:
        st.error("⚠️ Error generating chart. Data may be missing or too short for indicator calculations.")
