import plotly.graph_objects as go

def plotly_table(df):
    """
    Create a Plotly table from a DataFrame.
    Automatically handles missing 'Value' column.
    """
    # Prepare values for each column
    table_values = [df.index.astype(str)]  # Always include index as first column
    for col in df.columns:
        table_values.append(df[col].astype(str))  # Convert all values to string
    
    # Column names
    column_names = ["Index"] + list(df.columns)
    
    fig = go.Figure(
        data=[go.Table(
            header=dict(
                values=column_names,
                fill_color='lightblue',
                align='left'
            ),
            cells=dict(
                values=table_values,
                fill_color='lavender',
                align='left'
            )
        )]
    )
    
    fig.update_layout(margin=dict(l=5,r=5,t=5,b=5))
    return fig
