import plotly.graph_objects as go
import pandas as pd

# --- Function 1: Forecast Table ---
def plotly_table(df: pd.DataFrame):
    """
    Display forecast data in a styled Plotly table.
    """
    df_display = df.reset_index().rename(columns={'index': 'Date'})
    df_display['Date'] = df_display['Date'].dt.strftime('%Y-%m-%d')

    fig = go.Figure(
        data=[
            go.Table(
                header=dict(
                    values=["<b>Date</b>", "<b>Predicted Close ($)</b>"],
                    fill_color="#2E86C1",
                    align="center",
                    font=dict(color="white", size=13),
                    height=28
                ),
                cells=dict(
                    values=[df_display['Date'], df_display['Close'].round(2)],
                    fill_color="#F4F6F6",
                    align="center",
                    font=dict(color="#2C3E50", size=12),
                    height=26
                )
            )
        ]
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        height=260
    )
    return fig


# --- Function 2: Combined Moving Average + Animated Forecast ---
def Moving_average_forecast(data: pd.DataFrame):
    """
    Plot rolling average and 30-day forecast together using Plotly line chart.
    Includes animation that reveals forecast line over time.
    """
    # Split data
    historical = data.iloc[:-30]
    forecasted = data.iloc[-30:]

    fig = go.Figure()

    # Historical line (static)
    fig.add_trace(
        go.Scatter(
            x=historical.index,
            y=historical['Close'],
            mode="lines",
            name="7-Day Moving Avg (Historical)",
            line=dict(color="#2471A3", width=2.5)
        )
    )

    # Forecast animation frames
    frames = []
    for i in range(1, len(forecasted) + 1):
        frame = go.Frame(
            data=[
                go.Scatter(
                    x=forecasted.index[:i],
                    y=forecasted['Close'][:i],
                    mode="lines+markers",
                    line=dict(color="#E67E22", width=2.5, dash="dash"),
                    marker=dict(size=5)
                )
            ],
            name=str(i)
        )
        frames.append(frame)

    # Add initial empty forecast line
    fig.add_trace(
        go.Scatter(
            x=[],
            y=[],
            mode="lines+markers",
            name="Forecast (Next 30 Days)",
            line=dict(color="#E67E22", width=2.5, dash="dash"),
            marker=dict(size=5)
        )
    )

    # Layout + animation settings
    fig.update_layout(
        title=dict(
            text="📊 7-Day Moving Average & Forecast",
            x=0.5,
            xanchor="center",
            font=dict(size=18)
        ),
        xaxis_title="Date",
        yaxis_title="Stock Price ($)",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=40, r=40, t=60, b=40),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                x=0.1,
                y=-0.15,
                buttons=[
                    dict(
                        label="▶ Play Forecast",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 150, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate"
                            }
                        ]
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[
                            [None],
                            {"mode": "immediate", "frame": {"duration": 0, "redraw": False}, "transition": {"duration": 0}}
                        ]
                    )
                ]
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[[str(k)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}}],
                        label=str(k)
                    )
                    for k in range(1, len(forecasted) + 1)
                ],
                transition={"duration": 0},
                x=0.1,
                y=-0.1,
                currentvalue=dict(prefix="Day: ", visible=True),
                len=0.9
            )
        ]
    )

    fig.update_xaxes(showgrid=True, gridcolor="rgba(200,200,200,0.3)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(200,200,200,0.3)")

    # Attach frames for animation
    fig.frames = frames
    return fig
