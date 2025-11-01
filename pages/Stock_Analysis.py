import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import time
import plotly.graph_objects as go

st.set_page_config(page_title="📈 Stock Analysis", page_icon="📊", layout="wide")
st.title("📈 Stock Market Analysis Dashboard")

# ===============================
#  SAFE FETCH FUNCTIONS
# ===============================
@st.cache_data(ttl=300)
def safe_get_info(ticker):
    stock = yf.Ticker(ticker)
    info = {}
    try:
        fi = stock.fast_info
        info.update({
            "longName": fi.get("companyName", ticker),
            "marketCap": fi.get("marketCap"),
            "trailingPE": fi.get("trailingPE"),
            "beta": fi.get("beta"),
            "currency": fi.get("currency")
        })
    except Exception:
        pass
    for delay in [1, 2, 4]:
        try:
            more = stock.get_info()
            info.update(more)
            return info
        except Exception:
            time.sleep(delay)
    return info


@st.cache_data(ttl=300)
def safe_download(ticker, start, end):
    try:
        data = yf.download(ticker, start=start, end=end, progress=False, threads=False)
        return data if data is not None and not data.empty else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def safe_history(ticker):
    stock = yf.Ticker(ticker)
    for delay in [1, 2, 4]:
        try:
            data = stock.history(period="max")
            if not data.empty:
                return data
        except Exception:
            time.sleep(delay)
    return pd.DataFrame()


# ===============================
#  TECHNICAL INDICATOR FUNCTIONS
# ===============================
def add_moving_average(data, window=20):
    data[f"MA_{window}"] = data["Close"].rolling(window=window).mean()
    return data

def compute_RSI(data, period=14):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))
    return data

def compute_MACD(data, fast=12, slow=26, signal=9):
    exp1 = data["Close"].ewm(span=fast, adjust=False).mean()
    exp2 = data["Close"].ewm(span=slow, adjust=False).mean()
    data["MACD"] = exp1 - exp2
    data["Signal"] = data["MACD"].ewm(span=signal, adjust=False).mean()
    return data


# ===============================
#  INPUT SECTION
# ===============================
today = datetime.date.today()
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Enter Stock Ticker:", "AAPL").upper()
with col2:
    start_date = st.date_input("Start Date", datetime.date(today.year - 1, today.month, today.day))
with col3:
    end_date = st.date_input("End Date", today)

# ===============================
#  COMPANY INFO SECTION
# ===============================
info = safe_get_info(ticker)

if not info:
    st.warning("⚠️ Unable to fetch company info. Yahoo Finance API limit reached. Try again later.")
else:
    st.subheader(info.get("longName", ticker))
    st.write(info.get("longBusinessSummary", "Company summary unavailable due to API limits."))

    stats1 = pd.DataFrame({
        "Metric": ["Market Cap", "Beta", "EPS", "PE Ratio"],
        "Value": [
            info.get("marketCap", "N/A"),
            info.get("beta", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("trailingPE", "N/A"),
        ],
    })
    stats2 = pd.DataFrame({
        "Metric": ["Quick Ratio", "Revenue/Share", "Profit Margin", "Debt/Equity", "ROE"],
        "Value": [
            info.get("quickRatio", "N/A"),
            info.get("revenuePerShare", "N/A"),
            info.get("profitMargins", "N/A"),
            info.get("debtToEquity", "N/A"),
            info.get("returnOnEquity", "N/A"),
        ],
    })

    colA, colB = st.columns(2)
    colA.dataframe(stats1, use_container_width=True)
    colB.dataframe(stats2, use_container_width=True)


# ===============================
#  PRICE DATA SECTION
# ===============================
data = safe_download(ticker, start_date, end_date)

if data.empty:
    st.error("🚫 Price data unavailable. Yahoo Finance might be blocking requests.")
else:
    colA, colB, colC = st.columns(3)
    if len(data) > 1:
        daily_change = data["Close"].iloc[-1] - data["Close"].iloc[-2]
        colA.metric("Last Close", round(data["Close"].iloc[-1], 2), round(daily_change, 2))

    st.write("##### Historical Data (Last 10 days)")
    st.dataframe(data.tail(10).round(3))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index, y=data["Close"], mode="lines", name="Close Price",
        line=dict(width=2.5, color="royalblue")
    ))
    fig.update_layout(title=f"{ticker} Closing Price",
                      xaxis_title="Date", yaxis_title="Price (USD)",
                      template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True)


# ===============================
#  ADVANCED CHARTS + INDICATORS
# ===============================
hist = safe_history(ticker)

if hist.empty:
    st.error("⚠️ Unable to load full price history. Try again later.")
else:
    st.markdown("""<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""",
                unsafe_allow_html=True)

    st.subheader("📊 Technical Analysis Charts")

    chart_type = st.selectbox("Chart Type:", ["Candlestick", "Line"], index=0)
    indicator = st.selectbox("Indicator:", ["None", "Moving Average", "RSI", "MACD"], index=1)
    period = st.selectbox("Time Range:", ["5d", "1mo", "6mo", "ytd", "1y", "5y", "max"], index=3)

    # Use recent data if not max
    if period == "max":
        plot_data = hist
    elif period == "1y":
        plot_data = hist.tail(252)
    elif period == "6mo":
        plot_data = hist.tail(126)
    elif period == "1mo":
        plot_data = hist.tail(21)
    else:
        plot_data = hist.tail(60)

    # Compute indicators
    if indicator == "Moving Average":
        plot_data = add_moving_average(plot_data)
    elif indicator == "RSI":
        plot_data = compute_RSI(plot_data)
    elif indicator == "MACD":
        plot_data = compute_MACD(plot_data)

    # Main price chart
    if chart_type == "Candlestick":
        fig = go.Figure(data=[go.Candlestick(
            x=plot_data.index,
            open=plot_data["Open"],
            high=plot_data["High"],
            low=plot_data["Low"],
            close=plot_data["Close"],
            name="Candlestick"
        )])
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=plot_data.index, y=plot_data["Close"],
            mode="lines", name="Close Price",
            line=dict(color="royalblue", width=2)
        ))

    # Overlay indicators
    if indicator == "Moving Average":
        fig.add_trace(go.Scatter(
            x=plot_data.index, y=plot_data["MA_20"],
            mode="lines", name="20-Day MA",
            line=dict(color="orange", width=2, dash="dash")
        ))

    fig.update_layout(
        title=f"{ticker} Price Chart ({period.upper()})",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        height=600
    )
    st.plotly_chart(fig, use_container_width=True)

    # RSI / MACD charts
    if indicator == "RSI":
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=plot_data.index, y=plot_data["RSI"], mode="lines", name="RSI", line=dict(color="purple", width=2)
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(title="RSI Indicator", yaxis_title="RSI Value (0–100)", height=300, template="plotly_white")
        st.plotly_chart(fig_rsi, use_container_width=True)

    elif indicator == "MACD":
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=plot_data.index, y=plot_data["MACD"], name="MACD", line=dict(color="blue")))
        fig_macd.add_trace(go.Scatter(x=plot_data.index, y=plot_data["Signal"], name="Signal", line=dict(color="orange")))
        fig_macd.update_layout(title="MACD Indicator", yaxis_title="MACD Value", height=300, template="plotly_white")
        st.plotly_chart(fig_macd, use_container_width=True)
