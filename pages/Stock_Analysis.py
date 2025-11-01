# =========================
# Stock Analysis Dashboard
# Fixed & Optimized Version
# =========================

import sys
import time
import datetime
import logging
from pathlib import Path
from json.decoder import JSONDecodeError

import streamlit as st
import pandas as pd
import yfinance as yf

# --- Fix import path issues (important when running under Streamlit cloud) ---
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import local utilities
from pages.utils.plotly_figure import (
    plotly_table,
    close_chart,
    candlestick,
    RSI,
    Moving_average,
    MACD,
)

# --- Streamlit page config ---
st.set_page_config(page_title="Stock Analysis", page_icon="📈", layout="wide")
st.title("📈 Stock Analysis")

# --- Logging setup ---
logger = logging.getLogger("stock_app")
logger.setLevel(logging.INFO)

# ================================
# Helper: detect rate-limit errors
# ================================
def _is_rate_limit_error(exc):
    s = str(exc).lower()
    return "too many requests" in s or "429" in s or "rate limit" in s


# ======================
# Safe Yahoo API wrappers
# ======================

@st.cache_data(ttl=600)
def safe_get_info(ticker):
    """Fetch company info safely with retries and fallback."""
    stock = yf.Ticker(ticker)
    info = {}

    # Try fast_info first (cheap)
    try:
        fi = stock.fast_info or {}
        info.update({
            "longName": fi.get("companyName") or fi.get("shortName") or ticker,
            "marketCap": fi.get("marketCap"),
            "trailingPE": fi.get("trailingPE"),
            "beta": fi.get("beta"),
            "currency": fi.get("currency"),
        })
    except Exception as e:
        logger.debug(f"fast_info failed for {ticker}: {e}")

    # Retry get_info (expensive)
    for attempt, delay in enumerate([1, 2, 4, 8], start=1):
        try:
            more = stock.get_info()
            if isinstance(more, dict):
                info.update({k: v for k, v in more.items() if v is not None})
            return info
        except Exception as e:
            logger.warning(f"get_info failed for {ticker} attempt {attempt}: {e}")
            if _is_rate_limit_error(e):
                logger.error(f"Rate limit detected from Yahoo for {ticker}: {e}")
                return info  # return partial
            time.sleep(delay)

    return info


@st.cache_data(ttl=600)
def safe_download(ticker, start, end):
    """Download price data with retries."""
    for attempt, delay in enumerate([1, 2, 4, 8], start=1):
        try:
            df = yf.download(ticker, start=start, end=end, progress=False, threads=False)
            if df is not None and not df.empty:
                return df
            else:
                raise ValueError("Empty dataframe")
        except (JSONDecodeError, ValueError) as e:
            logger.warning(f"safe_download decode/value error for {ticker}: {e}")
        except Exception as e:
            logger.warning(f"safe_download failed attempt {attempt} for {ticker}: {e}")
            if _is_rate_limit_error(e):
                logger.error(f"Rate limit hit during download for {ticker}")
                break
        time.sleep(delay)
    return pd.DataFrame()


@st.cache_data(ttl=600)
def safe_history(ticker):
    """Full history with retries."""
    stock = yf.Ticker(ticker)
    for attempt, delay in enumerate([1, 2, 4, 8], start=1):
        try:
            df = stock.history(period="max")
            if df is not None and not df.empty:
                return df
        except (JSONDecodeError, ValueError) as e:
            logger.warning(f"history decode/value error for {ticker}: {e}")
        except Exception as e:
            logger.warning(f"history failed for {ticker} attempt {attempt}: {e}")
            if _is_rate_limit_error(e):
                logger.error(f"Rate limit hit during history for {ticker}")
                break
        time.sleep(delay)
    return pd.DataFrame()


# =====================
# Streamlit UI elements
# =====================

today = datetime.date.today()
col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.text_input("Stock Ticker", "AAPL").upper()

with col2:
    start_date = st.date_input(
        "Start Date", datetime.date(today.year - 1, today.month, today.day)
    )

with col3:
    end_date = st.date_input("End Date", today)


# -------------------------
# Fetch company information
# -------------------------
info = safe_get_info(ticker)

if not info:
    st.warning("⚠️ Unable to fetch company info. Yahoo Finance API limit reached. Try again later.")
else:
    st.subheader(info.get("longName", ticker))
    st.write(info.get("longBusinessSummary", "Company summary unavailable due to API limits."))

    stats1 = pd.DataFrame({
        "": ["Market Cap", "Beta", "EPS", "PE Ratio"],
        "Value": [
            info.get("marketCap", "N/A"),
            info.get("beta", "N/A"),
            info.get("trailingEps", "N/A"),
            info.get("trailingPE", "N/A"),
        ],
    }).set_index("")

    stats2 = pd.DataFrame({
        "": ["Quick Ratio", "Revenue/Share", "Profit Margin", "Debt/Equity", "ROE"],
        "Value": [
            info.get("quickRatio", "N/A"),
            info.get("revenuePerShare", "N/A"),
            info.get("profitMargins", "N/A"),
            info.get("debtToEquity", "N/A"),
            info.get("returnOnEquity", "N/A"),
        ],
    }).set_index("")

    colA, colB = st.columns(2)
    colA.plotly_chart(plotly_table(stats1), use_container_width=True)
    colB.plotly_chart(plotly_table(stats2), use_container_width=True)


# -------------------------
# Fetch price data
# -------------------------
data = safe_download(ticker, start_date, end_date)

if data.empty:
    st.error("🚫 Price data unavailable. Yahoo Finance might be blocking requests.")
else:
    colA, colB, colC = st.columns(3)
    if len(data) > 1:
        daily_change = data["Close"].iloc[-1] - data["Close"].iloc[-2]
        colA.metric("Daily Close", round(data["Close"].iloc[-1], 2), round(daily_change, 2))

    data.index = [str(i)[:10] for i in data.index]
    fig_tail = plotly_table(data.tail(10).sort_index(ascending=False).round(3))
    fig_tail.update_layout(height=220)

    st.write("##### Historical Data (Last 10 days)")
    st.plotly_chart(fig_tail, use_container_width=True)


st.markdown(
    """<hr style="height:2px;border:none;color:#0078ff;background-color:#0078ff;" />""",
    unsafe_allow_html=True,
)

# -------------------------
# Chart period selection
# -------------------------
period_buttons = ["5d", "1mo", "6mo", "ytd", "1y", "5y", "max"]
labels = ["5D", "1M", "6M", "YTD", "1Y", "5Y", "MAX"]
period = ""

cols = st.columns(len(labels))
for i, (c, p, l) in enumerate(zip(cols, period_buttons, labels)):
    if c.button(l, key=f"period_{i}"):
        period = p

# -------------------------
# Chart type and indicator
# -------------------------
col1, col2, _ = st.columns([1, 1, 4])
chart_type = col1.selectbox("Chart Type", ["Candle", "Line"], label_visibility="collapsed")
indicators = col2.selectbox(
    "Indicator",
    ["RSI", "Moving Average", "MACD"] if chart_type == "Line" else ["RSI", "MACD"],
    label_visibility="collapsed",
)

# -------------------------
# Historical chart display
# -------------------------
hist = safe_history(ticker)

if hist.empty:
    st.error("⚠️ Unable to load full price history. Try again later.")
else:
    plot_period = period if period else "1y"

    if chart_type == "Candle":
        st.plotly_chart(candlestick(hist, plot_period), use_container_width=True)
        if indicators == "RSI":
            st.plotly_chart(RSI(hist, plot_period), use_container_width=True)
        elif indicators == "MACD":
            st.plotly_chart(MACD(hist, plot_period), use_container_width=True)

    else:  # Line chart
        if indicators == "Moving Average":
            st.plotly_chart(Moving_average(hist, plot_period), use_container_width=True)
        else:
            st.plotly_chart(close_chart(hist, plot_period), use_container_width=True)
            if indicators == "RSI":
                st.plotly_chart(RSI(hist, plot_period), use_container_width=True)
            elif indicators == "MACD":
                st.plotly_chart(MACD(hist, plot_period), use_container_width=True)
