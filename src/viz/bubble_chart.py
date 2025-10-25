import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_bubble_chart(topic_stats_df):
    if topic_stats_df.empty:
        return None

    fig = go.Figure(data=[go.Scatter(
        x=topic_stats_df['topic_label'],
        y=topic_stats_df['avg_sentiment'],
        mode='markers',
        marker=dict(
            size=topic_stats_df['count'],
            sizemode='area',
            sizeref=2.*max(topic_stats_df['count'])/(40.**2),
            sizemin=4,
            color=topic_stats_df['avg_sentiment'],
            colorscale='RdYlGn',
            colorbar=dict(title="Avg Sentiment"),
            line=dict(width=1, color='DarkSlateGrey')
        ),
        text=topic_stats_df.apply(
            lambda row: f"{row['topic_label']}<br>Count: {row['count']}<br>Avg Sentiment: {row['avg_sentiment']:.2f}",
            axis=1
        ),
        hoverinfo='text'
    )])

    fig.update_layout(
        title='Topic Analysis: Sentiment vs Volume',
        xaxis_title='Topic',
        yaxis_title='Average Sentiment Score',
        height=500,
        hovermode='closest',
        xaxis=dict(tickangle=-45)
    )

    return fig

def create_sentiment_distribution_chart(sentiment_counts):
    df = pd.DataFrame(list(sentiment_counts.items()), columns=['Sentiment', 'Count'])

    color_map = {
        'Very Negative': '#d32f2f',
        'Negative': '#f57c00',
        'Neutral': '#fbc02d',
        'Positive': '#689f38',
        'Very Positive': '#388e3c',
        'Mixed': '#757575'
    }

    df['Color'] = df['Sentiment'].map(color_map)

    fig = go.Figure(data=[go.Bar(
        x=df['Sentiment'],
        y=df['Count'],
        marker_color=df['Color'],
        text=df['Count'],
        textposition='auto'
    )])

    fig.update_layout(
        title='Sentiment Distribution',
        xaxis_title='Sentiment',
        yaxis_title='Count',
        height=400
    )

    return fig
