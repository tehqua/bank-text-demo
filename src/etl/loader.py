import pandas as pd
from config.settings import REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from src.utils.logger import default_logger as logger

def load_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        logger.info(f"Loaded CSV: {file_path}, rows: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        raise

def validate_schema(df):
    columns = df.columns.tolist()

    missing_required = [col for col in REQUIRED_COLUMNS if col not in columns]
    if missing_required:
        raise ValueError(f"Missing required columns: {missing_required}")

    for req_col in REQUIRED_COLUMNS:
        null_count = df[req_col].isna().sum()
        if null_count > 0:
            logger.warning(f"Column '{req_col}' has {null_count} null values")

    logger.info("Schema validation passed")
    return True

def add_missing_columns(df):
    for opt_col in OPTIONAL_COLUMNS:
        if opt_col not in df.columns:
            if opt_col == "id":
                df[opt_col] = None
            elif opt_col == "timestamp":
                df[opt_col] = None
            elif opt_col == "source":
                df[opt_col] = "unknown"

    return df

def load_and_validate(file_path):
    df = load_csv(file_path)
    validate_schema(df)
    df = add_missing_columns(df)
    df = df[df['comment'].notna()]
    return df
