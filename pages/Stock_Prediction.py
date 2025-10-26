import streamlit as st
import pandas as pd
from pages.utils.model_train import (
    get_data,
    get_rolling_mean,
    get_differencing_order,
    scaling,
    evaluate_model,
    get_forecast,
    inverse_scaling
)
from pages.utils.plotly_figure import (
    plotly_table,
    Moving_average_forecast,
    close_chart,
    candlestick,
    RSI,
    Moving_average,
    MACD
)

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="📊 Stock Prediction",
    page_icon="💹",
    layout="wide",
)

st.title("📊 Stock Prediction")

# -------------------------------
# User input
# -------------------------------
col1, _, _ = st.columns(3)
with col1:
    ticker = st.text_input("🔎 Stock Ticker", "AAPL")

if ticker:
    st.subheader(f"🔮 Predicting Next 30 Days Close Price for: {ticker}")

    # -------------------------------
    # Fetch & process data
    # -------------------------------
    close_price = get_data(ticker)
    rolling_price = get_rolling_mean(close_price)
    differencing_order = get_differencing_order(rolling_price)
    scaled_data, scaler = scaling(rolling_price)

    # -------------------------------
    # Compute RMSE
    # -------------------------------
    rmse = evaluate_model(scaled_data, differencing_order)
    st.write(f"📊 **Model RMSE Score:** {rmse:.4f}")

    # -------------------------------
    # Forecast next 30 days
    # -------------------------------
    forecast = get_forecast(scaled_data, differencing_order)
    forecast['Close'] = inverse_scaling(scaler, forecast['Close'])

    st.write(f"🗓️ ##### Forecast Data (Next 30 Days) for {ticker}")
    st.plotly_chart(
        plotly_table(forecast.sort_index().round(3)),
        use_container_width=True
    )

    # -------------------------------
    # Combined chart with rolling mean
    # -------------------------------
    combined = pd.concat([rolling_price, forecast])
    combined['MA7'] = combined['Close'].rolling(7).mean()
    fig = Moving_average_forecast(combined.iloc[-150:])
    fig.update_layout(title=f"{ticker} Close Price Forecast with 7-day MA")
    st.plotly_chart(fig, use_container_width=True)

    # -------------------------------
    # Optional: Candle/Line chart with indicators
    # -------------------------------
    col1, col2 = st.columns([1, 1])
    with col1:
        chart_type = st.selectbox('📊 Chart Type', ('Candle', 'Line'))
    with col2:
        if chart_type == 'Candle':
            indicator = st.selectbox('📈 Indicator', ('RSI', 'MACD'))
        else:
            indicator = st.selectbox('📈 Indicator', ('RSI', 'Moving Average', 'MACD'))

    # RSI window slider
    rsi_window = st.slider("🔧 Select RSI Window (days)", 5, 50, 14)

    history_df = get_data(ticker, period='max')  # fetch max history

    # -------------------------------
    # Chart rendering with title
    # -------------------------------
    if chart_type == 'Candle':
        st.plotly_chart(candlestick(history_df, 'max').update_layout(title=f"{ticker} Candlestick Chart"), use_container_width=True)
        if indicator == 'RSI':
            st.plotly_chart(RSI(history_df, 'max', window=rsi_window).update_layout(title=f"{ticker} RSI ({rsi_window}-day)"), use_container_width=True)
        elif indicator == 'MACD':
            st.plotly_chart(MACD(history_df, 'max').update_layout(title=f"{ticker} MACD"), use_container_width=True)
    else:
        if indicator == 'RSI':
            st.plotly_chart(close_chart(history_df, 'max').update_layout(title=f"{ticker} Close Price Chart"), use_container_width=True)
            st.plotly_chart(RSI(history_df, 'max', window=rsi_window).update_layout(title=f"{ticker} RSI ({rsi_window}-day)"), use_container_width=True)
        elif indicator == 'Moving Average':
            st.plotly_chart(Moving_average(history_df, 'max').update_layout(title=f"{ticker} Close Price with MA7"), use_container_width=True)
        elif indicator == 'MACD':
            st.plotly_chart(close_chart(history_df, 'max').update_layout(title=f"{ticker} Close Price Chart"), use_container_width=True)
            st.plotly_chart(MACD(history_df, 'max').update_layout(title=f"{ticker} MACD"), use_container_width=True)
