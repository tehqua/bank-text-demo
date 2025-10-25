"""
Train Sentiment Model - Standalone Script

Usage:
    python scripts/train_sentiment_model.py
    python scripts/train_sentiment_model.py --data data/labeled/sentiment_training_dataset.csv
"""

import pandas as pd
import numpy as np
import argparse
import sys
from pathlib import Path
import re
import joblib
import json
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Sklearn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    f1_score, precision_score, recall_score
)

# Imbalanced learning
from imblearn.over_sampling import SMOTE

# Vietnamese NLP
try:
    from underthesea import word_tokenize
    UNDERTHESEA_AVAILABLE = True
except ImportError:
    print("⚠️  Warning: underthesea not available. Using basic tokenization.")
    UNDERTHESEA_AVAILABLE = False

# Vietnamese stopwords
VIETNAMESE_STOPWORDS = set([
    'bị', 'bởi', 'cả', 'các', 'cái', 'cần', 'càng', 'chỉ', 'chiếc', 'cho', 'chứ',
    'chưa', 'chuyện', 'có', 'có_thể', 'cứ', 'của', 'cùng', 'cũng', 'đã', 'đang',
    'đây', 'để', 'đến_nỗi', 'đều', 'điều', 'do', 'đó', 'được', 'dưới', 'gì', 'khi',
    'không', 'là', 'lại', 'lên', 'lúc', 'mà', 'mỗi', 'một_cách', 'này', 'nên', 'nếu',
    'ngay', 'nhiều', 'như', 'nhưng', 'những', 'nơi', 'nữa', 'phải', 'qua', 'ra', 'rằng',
    'rất', 'rồi', 'sau', 'sẽ', 'so', 'sự', 'tại', 'theo', 'thì', 'trên', 'trước', 'từ',
    'từng', 'và', 'vẫn', 'vào', 'vậy', 'vì', 'việc', 'với', 'vừa'
])

def clean_text(text):
    """Clean Vietnamese text"""
    if pd.isna(text):
        return ""

    text = str(text)
    text = text.lower()

    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

    # Remove mentions and hashtags
    text = re.sub(r'@\w+|#\w+', '', text)

    # Remove emails
    text = re.sub(r'\S+@\S+', '', text)

    # Remove numbers
    text = re.sub(r'\d+', '', text)

    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def tokenize_vietnamese(text):
    """Tokenize Vietnamese text and remove stopwords"""
    if not text:
        return ""

    try:
        if UNDERTHESEA_AVAILABLE:
            tokens = word_tokenize(text, format="text").split()
        else:
            tokens = text.split()

        # Remove stopwords
        tokens = [word for word in tokens if word not in VIETNAMESE_STOPWORDS]

        # Remove single characters
        tokens = [word for word in tokens if len(word) > 1]

        return ' '.join(tokens)
    except:
        return text

def load_data(file_path):
    """Load training data"""
    print(f"Loading data from: {file_path}")

    df = pd.read_csv(file_path)
    print(f"Loaded {len(df)} samples")

    # Check columns
    if 'comment' not in df.columns or 'sentiment_label' not in df.columns:
        raise ValueError("CSV must have 'comment' and 'sentiment_label' columns")

    # Display info
    print(f"\nSentiment Distribution:")
    print(df['sentiment_label'].value_counts())

    return df

def preprocess_data(df):
    """Preprocess text data"""
    print("\nPreprocessing data...")

    df['text_clean'] = df['comment'].apply(clean_text)
    df['text_tokenized'] = df['text_clean'].apply(tokenize_vietnamese)

    # Remove empty texts
    df = df[df['text_tokenized'].str.len() > 0].reset_index(drop=True)

    print(f"Preprocessing complete! {len(df)} samples remaining")

    return df

def train_models(X_train, X_test, y_train, y_test):
    """Train and compare multiple models"""
    print("\nTraining models...")

    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
        'Naive Bayes': MultinomialNB(),
        'Linear SVM': LinearSVC(max_iter=1000, random_state=42, class_weight='balanced'),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced', n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42)
    }

    results = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'f1_macro': f1_macro,
            'f1_weighted': f1_weighted,
            'predictions': y_pred
        }

        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  F1 (macro): {f1_macro:.4f}")
        print(f"  F1 (weighted): {f1_weighted:.4f}")

    # Find best model
    best_model_name = max(results.items(), key=lambda x: x[1]['f1_weighted'])[0]
    print(f"\nBest Model: {best_model_name}")

    return results, best_model_name

def hyperparameter_tuning(best_model_name, X_train, y_train):
    """Hyperparameter tuning for best model"""
    print(f"\nHyperparameter tuning for {best_model_name}...")

    if best_model_name == 'Logistic Regression':
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'penalty': ['l1', 'l2'],
            'solver': ['liblinear', 'saga']
        }

        grid_search = GridSearchCV(
            LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'),
            param_grid,
            cv=5,
            scoring='f1_weighted',
            n_jobs=-1,
            verbose=0
        )

        grid_search.fit(X_train, y_train)

        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best F1 (weighted): {grid_search.best_score_:.4f}")

        return grid_search.best_estimator_

    else:
        print(f"Hyperparameter tuning not implemented for {best_model_name}")
        print(f"Using default model configuration")
        return None

def save_model(model, vectorizer, metadata, output_dir):
    """Save model and artifacts"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nSaving model artifacts to: {output_dir}")

    # Save vectorizer
    vectorizer_path = output_dir / 'tfidf_vectorizer.pkl'
    joblib.dump(vectorizer, vectorizer_path)
    print(f"  Vectorizer: {vectorizer_path}")

    # Save model
    model_path = output_dir / 'sentiment_model.pkl'
    joblib.dump(model, model_path)
    print(f"  Model: {model_path}")

    # Save metadata
    metadata_path = output_dir / 'model_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  Metadata: {metadata_path}")

    print(f"\nModel saved successfully!")

def main():
    parser = argparse.ArgumentParser(description='Train Sentiment Model')
    parser.add_argument('--data', type=str,
                       default='data/labeled/sentiment_training_dataset.csv',
                       help='Path to training CSV')
    parser.add_argument('--output', type=str,
                       default='data/model_artifacts/sentiment',
                       help='Output directory for model')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set size (default: 0.2)')
    parser.add_argument('--max-features', type=int, default=5000,
                       help='Max TF-IDF features (default: 5000)')
    parser.add_argument('--use-smote', action='store_true',
                       help='Use SMOTE for class balancing')

    args = parser.parse_args()

    print("="*60)
    print("   SENTIMENT MODEL TRAINING")
    print("="*60)

    # Load data
    df = load_data(args.data)

    # Preprocess
    df = preprocess_data(df)

    # Prepare data
    X = df['text_tokenized']
    y = df['sentiment_label']

    # Train-test split
    print(f"\nSplitting data (test_size={args.test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )
    print(f"  Training set: {len(X_train)} samples")
    print(f"  Test set: {len(X_test)} samples")

    # TF-IDF Vectorization
    print(f"\nExtracting TF-IDF features (max_features={args.max_features})...")

    # Determine min_df based on dataset size
    min_df = 2 if len(X_train) > 50 else 1
    max_df = 0.8 if len(X_train) > 50 else 1.0

    tfidf_vectorizer = TfidfVectorizer(
        max_features=args.max_features,
        ngram_range=(1, 2),
        min_df=min_df,
        max_df=max_df,
        sublinear_tf=True
    )

    X_train_tfidf = tfidf_vectorizer.fit_transform(X_train)
    X_test_tfidf = tfidf_vectorizer.transform(X_test)

    print(f"  Feature matrix shape: {X_train_tfidf.shape}")
    print(f"  Vocabulary size: {len(tfidf_vectorizer.vocabulary_)}")

    # Handle class imbalance
    X_train_balanced = X_train_tfidf
    y_train_balanced = y_train

    if args.use_smote:
        class_counts = y_train.value_counts()
        imbalance_ratio = class_counts.max() / class_counts.min()

        if imbalance_ratio > 2.0:
            print(f"\nApplying SMOTE (imbalance ratio: {imbalance_ratio:.2f})...")

            min_class_count = class_counts.min()
            k_neighbors = min(5, min_class_count - 1)

            if k_neighbors > 0:
                smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
                X_train_balanced, y_train_balanced = smote.fit_resample(X_train_tfidf, y_train)
                print(f"  Balanced training set: {X_train_balanced.shape[0]} samples")
            else:
                print(f"  SMOTE skipped: not enough samples in minority class")

    # Train models
    results, best_model_name = train_models(
        X_train_balanced, X_test_tfidf,
        y_train_balanced, y_test
    )

    # Hyperparameter tuning
    tuned_model = hyperparameter_tuning(best_model_name, X_train_balanced, y_train_balanced)

    if tuned_model:
        final_model = tuned_model
    else:
        final_model = results[best_model_name]['model']

    # Final evaluation
    y_pred_final = final_model.predict(X_test_tfidf)

    print("\n" + "="*60)
    print("   FINAL MODEL PERFORMANCE")
    print("="*60)
    print(f"\nModel: {best_model_name}")
    print(f"Accuracy: {accuracy_score(y_test, y_pred_final):.4f}")
    print(f"F1 (macro): {f1_score(y_test, y_pred_final, average='macro', zero_division=0):.4f}")
    print(f"F1 (weighted): {f1_score(y_test, y_pred_final, average='weighted', zero_division=0):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred_final, average='weighted', zero_division=0):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred_final, average='weighted', zero_division=0):.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred_final, zero_division=0))

    # Prepare metadata
    metadata = {
        'model_name': best_model_name,
        'training_date': datetime.now().isoformat(),
        'num_training_samples': int(X_train_balanced.shape[0]),
        'num_test_samples': int(len(X_test)),
        'num_features': int(X_train_tfidf.shape[1]),
        'accuracy': float(accuracy_score(y_test, y_pred_final)),
        'f1_macro': float(f1_score(y_test, y_pred_final, average='macro', zero_division=0)),
        'f1_weighted': float(f1_score(y_test, y_pred_final, average='weighted', zero_division=0)),
        'precision': float(precision_score(y_test, y_pred_final, average='weighted', zero_division=0)),
        'recall': float(recall_score(y_test, y_pred_final, average='weighted', zero_division=0)),
        'labels': sorted(y_train.unique().tolist()),
        'hyperparameters': final_model.get_params() if hasattr(final_model, 'get_params') else {},
        'tfidf_config': {
            'max_features': args.max_features,
            'ngram_range': (1, 2),
            'min_df': min_df,
            'max_df': max_df
        }
    }

    # Save model
    save_model(final_model, tfidf_vectorizer, metadata, args.output)

    # Test predictions
    print("\n" + "="*60)
    print("   TEST PREDICTIONS")
    print("="*60)

    test_texts = [
        "Dich vu rat tuyet voi, toi rat hai long!",
        "App qua te, khong dung duoc",
        "Binh thuong thoi",
        "Giao dien dep nhung hay bi lag",
    ]

    for idx, text in enumerate(test_texts, 1):
        text_clean = clean_text(text)
        text_tokenized = tokenize_vietnamese(text_clean)
        text_vector = tfidf_vectorizer.transform([text_tokenized])
        prediction = final_model.predict(text_vector)[0]

        if hasattr(final_model, 'predict_proba'):
            confidence = final_model.predict_proba(text_vector)[0].max()
        else:
            confidence = 1.0

        print(f"\nTest {idx}: Prediction = {prediction} (confidence: {confidence:.2f})")

    print("\n" + "="*60)
    print("   TRAINING COMPLETE!")
    print("="*60)

if __name__ == "__main__":
    main()
