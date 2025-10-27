import plotly.graph_objects as go
import pandas as pd
import ta

# ----------------------------------------
# RSI Indicator
# ----------------------------------------
def RSI(data: pd.DataFrame, period: str = "1y", window: int = 14):
    """
    Calculate RSI using specified window.
    The Streamlit slider is removed from this function.
    """
    df = data.copy()
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=window).rsi()

    # Slice period
    df = _slice_period(df, period)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines",
                             name=f"RSI ({window}-day)", line=dict(color="#0078FF")))
    fig.add_hline(y=70, line=dict(color="red", dash="dot"))
    fig.add_hline(y=30, line=dict(color="green", dash="dot"))
    fig.update_layout(title=f"RSI Indicator ({window}-day)",
                      xaxis_title="Date", yaxis_title="RSI Value",
                      template="plotly_white", height=300)
    return fig

# ----------------------------------------
# Other plotting functions remain the same
# ----------------------------------------
def plotly_table(df: pd.DataFrame):
    fig = go.Figure(
        data=[go.Table(
            header=dict(values=list(df.reset_index().columns), fill_color="#0078FF", align="center", font=dict(color="white", size=13), height=30),
            cells=dict(values=[df.reset_index()[col] for col in df.reset_index().columns], fill_color="#F9FBFD", align="center", height=25)
        )]
    )
    fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
    return fig

def _slice_period(df: pd.DataFrame, period: str):
    df_copy = df.copy()
    if period == "1y":
        df_copy = df_copy.tail(252)
    elif period == "5y":
        df_copy = df_copy.tail(1260)
    elif period.upper() == "YTD":
        df_copy = df_copy.loc[df_copy.index.year == pd.Timestamp.today().year]
    elif period.lower() == "max":
        pass
    return df_copy

# You can keep other functions (Moving_average, MACD, candlestick, etc.) unchanged
