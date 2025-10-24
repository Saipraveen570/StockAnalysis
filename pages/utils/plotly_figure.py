import plotly.graph_objects as go
import pandas as pd
import numpy as np


# ------------------------ 1. TABLE VIEW ------------------------
def plotly_table(df: pd.DataFrame):
    """
    Creates a compact and responsive Plotly Table for display in Streamlit.
    """
    try:
        fig = go.Figure(
            data=[
                go.Table(
                    header=dict(
                        values=["<b>Index</b>", "<b>Value</b>"],
                        fill_color="#0078ff",
                        font=dict(color="white", size=13),
                        align="center",
                        height=30,
                    ),
                    cells=dict(
                        values=[df.index.astype(str), df.iloc[:, 0].astype(str)],
                        fill_color=[["#f9f9f9", "#ffffff"] * (len(df)//2 + 1)],
                        align="center",
                        font=dict(size=12),
                        height=28,
                    ),
                )
            ]
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=250,
        )
        return fig

    except Exception as e:
        print(f"Error creating table: {e}")
        return go.Figure()


# ------------------------ 2. LINE CHART (CLOSE PRICE) ------------------------
def close_chart(data: pd.DataFrame, period: str = "1y"):
    """
    Creates a simple close price line chart.
    """
    try:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                line=dict(color="#0078ff", width=2),
                name="Close Price",
            )
        )

        fig.update_layout(
            title=f"Close Price ({period})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            hovermode="x unified",
            height=400,
        )
        return fig

    except Exception as e:
        print(f"Error generating close_chart: {e}")
        return go.Figure()


# ------------------------ 3. MOVING AVERAGE FORECAST ------------------------
def Moving_average_forecast(data: pd.DataFrame):
    """
    Displays historical and forecasted closing prices with a smooth transition.
    """
    try:
        data = data.copy()
        data["Type"] = np.where(data.index < data.index[-30], "Historical", "Forecast")

        fig = go.Figure()

        # Historical
        hist_data = data[data["Type"] == "Historical"]
        fig.add_trace(
            go.Scatter(
                x=hist_data.index,
                y=hist_data["Close"],
                mode="lines",
                name="Historical",
                line=dict(color="#0078ff", width=2),
            )
        )

        # Forecast
        forecast_data = data[data["Type"] == "Forecast"]
        fig.add_trace(
            go.Scatter(
                x=forecast_data.index,
                y=forecast_data["Close"],
                mode="lines",
                name="Forecast",
                line=dict(color="#ff7f0e", dash="dot", width=3),
            )
        )

        fig.update_layout(
            title="📈 Historical vs Forecasted Close Price",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            legend=dict(orientation="h", y=-0.2),
            template="plotly_white",
            hovermode="x unified",
            height=450,
            margin=dict(l=20, r=20, t=50, b=50),
        )
        return fig

    except Exception as e:
        print(f"Error generating forecast chart: {e}")
        return go.Figure()


# ------------------------ 4. RSI (Relative Strength Index) ------------------------
def RSI(data: pd.DataFrame, period: str = "1y", window: int = 14):
    """
    Plots RSI indicator.
    """
    try:
        delta = data["Close"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=rsi, mode="lines", name="RSI", line=dict(color="#0078ff")))
        fig.add_hrect(y0=30, y1=70, fillcolor="lightgray", opacity=0.2, line_width=0)
        fig.update_layout(
            title=f"RSI Indicator ({period})",
            xaxis_title="Date",
            yaxis_title="RSI",
            template="plotly_white",
            height=300,
        )
        return fig
    except Exception as e:
        print(f"Error generating RSI: {e}")
        return go.Figure()


# ------------------------ 5. MACD (Moving Average Convergence Divergence) ------------------------
def MACD(data: pd.DataFrame, period: str = "1y"):
    """
    Plots MACD line and signal line.
    """
    try:
        short_ema = data["Close"].ewm(span=12, adjust=False).mean()
        long_ema = data["Close"].ewm(span=26, adjust=False).mean()
        macd = short_ema - long_ema
        signal = macd.ewm(span=9, adjust=False).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=macd, name="MACD", line=dict(color="#0078ff")))
        fig.add_trace(go.Scatter(x=data.index, y=signal, name="Signal", line=dict(color="#ff7f0e", dash="dot")))
        fig.update_layout(
            title=f"MACD Indicator ({period})",
            xaxis_title="Date",
            yaxis_title="MACD",
            template="plotly_white",
            height=300,
            hovermode="x unified",
        )
        return fig
    except Exception as e:
        print(f"Error generating MACD: {e}")
        return go.Figure()


# ------------------------ 6. MOVING AVERAGE ------------------------
def Moving_average(data: pd.DataFrame, period: str = "1y"):
    """
    Adds 7-day and 21-day moving averages to the close price chart.
    """
    try:
        data["MA7"] = data["Close"].rolling(window=7).mean()
        data["MA21"] = data["Close"].rolling(window=21).mean()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close", line=dict(color="#0078ff")))
        fig.add_trace(go.Scatter(x=data.index, y=data["MA7"], mode="lines", name="7-day MA", line=dict(dash="dot", color="#ff7f0e")))
        fig.add_trace(go.Scatter(x=data.index, y=data["MA21"], mode="lines", name="21-day MA", line=dict(dash="dot", color="#2ca02c")))

        fig.update_layout(
            title=f"Moving Averages ({period})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            legend=dict(orientation="h", y=-0.2),
            template="plotly_white",
            height=400,
        )
        return fig
    except Exception as e:
        print(f"Error generating moving average: {e}")
        return go.Figure()


# ------------------------ 7. CANDLESTICK ------------------------
def candlestick(data: pd.DataFrame, period: str = "1y"):
    """
    Displays a Plotly Candlestick chart for stock OHLC data.
    """
    try:
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=data.index,
                    open=data["Open"],
                    high=data["High"],
                    low=data["Low"],
                    close=data["Close"],
                    name="Candlestick",
                )
            ]
        )
        fig.update_layout(
            title=f"Candlestick Chart ({period})",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            height=450,
            xaxis_rangeslider_visible=False,
        )
        return fig
    except Exception as e:
        print(f"Error generating candlestick: {e}")
        return go.Figure()
