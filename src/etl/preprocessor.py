import pandas as pd
import unicodedata
import re
from src.etl.pii_mask import mask_pii
from src.utils.logger import default_logger as logger

def normalize_unicode(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFC', text)
    return text

def clean_text(text):
    if not text:
        return ""

    text = normalize_unicode(text)
    text = mask_pii(text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text

def preprocess_dataframe(df):
    logger.info("Starting preprocessing")

    df['comment_clean'] = df['comment'].apply(clean_text)
    df['comment_lower'] = df['comment_clean'].str.lower()

    df = df[df['comment_clean'] != ""]

    logger.info(f"Preprocessing complete, rows: {len(df)}")
    return df

def tokenize_vietnamese(text):
    try:
        from underthesea import word_tokenize
        return word_tokenize(text, format="text")
    except ImportError:
        logger.warning("underthesea not installed, using basic tokenization")
        return text

def add_tokenized_column(df, input_col="comment_lower", output_col="comment_tokenized"):
    df[output_col] = df[input_col].apply(tokenize_vietnamese)
    return df
