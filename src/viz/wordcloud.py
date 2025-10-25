from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO

def generate_wordcloud(texts, topic_name="All", max_words=100):
    combined_text = " ".join(texts)

    if not combined_text.strip():
        return None

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        max_words=max_words,
        colormap='viridis',
        font_path=None,
        relative_scaling=0.5
    ).generate(combined_text)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(f'Word Cloud: {topic_name}', fontsize=16)

    return fig

def generate_wordcloud_image(texts, max_words=100):
    combined_text = " ".join(texts)

    if not combined_text.strip():
        return None

    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color='white',
        max_words=max_words,
        colormap='viridis'
    ).generate(combined_text)

    buf = BytesIO()
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)

    return buf
