import pandas as pd

def create_topic_summary_table(df_pandas):
    if df_pandas.empty:
        return pd.DataFrame()

    required_cols = ['topic_label', 'sentiment_score']
    for col in required_cols:
        if col not in df_pandas.columns:
            return pd.DataFrame()

    summary = df_pandas.groupby('topic_label').agg({
        'comment': 'count',
        'sentiment_score': 'mean'
    }).reset_index()

    summary.columns = ['Topic', 'Comment Count', 'Avg Sentiment Score']
    summary = summary.sort_values('Comment Count', ascending=False)

    return summary

def create_sentiment_summary_table(df_pandas):
    if df_pandas.empty or 'sentiment_label' not in df_pandas.columns:
        return pd.DataFrame()

    summary = df_pandas['sentiment_label'].value_counts().reset_index()
    summary.columns = ['Sentiment', 'Count']

    sentiment_order = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive', 'Mixed']
    summary['Order'] = summary['Sentiment'].apply(
        lambda x: sentiment_order.index(x) if x in sentiment_order else 99
    )
    summary = summary.sort_values('Order').drop('Order', axis=1)

    return summary

def filter_dataframe(df_pandas, topic=None, sentiment=None, source=None):
    filtered_df = df_pandas.copy()

    if topic and topic != "All":
        filtered_df = filtered_df[filtered_df['topic_label'] == topic]

    if sentiment and sentiment != "All":
        filtered_df = filtered_df[filtered_df['sentiment_label'] == sentiment]

    if source and source != "All":
        if 'source' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['source'] == source]

    return filtered_df
