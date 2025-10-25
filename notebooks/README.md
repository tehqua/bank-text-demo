# Sentiment Model Training Notebook

## Overview

Notebook này thực hiện toàn bộ pipeline training model sentiment analysis cho tiếng Việt sử dụng dataset **GreenNode/tweet-sentiment-extraction-vn** từ Hugging Face.

## Dataset Information

**Source:** [GreenNode/tweet-sentiment-extraction-vn](https://huggingface.co/datasets/GreenNode/tweet-sentiment-extraction-vn)

**Description:** Vietnamese tweet sentiment dataset với các nhãn sentiment khác nhau (positive, negative, neutral, v.v.)

## Notebook Contents

### 1. **Setup & Imports**
- Import libraries cần thiết
- Setup visualization style
- Configure environment

### 2. **Data Loading**
- Load dataset từ Hugging Face
- Convert sang pandas DataFrame
- Initial data inspection

### 3. **Exploratory Data Analysis (EDA)**
- Dataset statistics
- Sentiment distribution analysis
- Text length analysis
- Word count analysis
- Sample texts visualization
- Class imbalance detection

### 4. **Text Preprocessing**
- Text cleaning (URLs, mentions, hashtags, numbers, punctuation)
- Vietnamese word tokenization (underthesea)
- Stopword removal
- Special character handling

### 5. **Feature Extraction**
- TF-IDF Vectorization
  - max_features: 5000
  - ngram_range: (1, 2)
  - min_df: 2
  - max_df: 0.8
- Feature importance analysis

### 6. **Data Augmentation**
- Class imbalance handling
- SMOTE (Synthetic Minority Over-sampling Technique)
- Balanced dataset creation

### 7. **Model Training**
Models được train và so sánh:
- ✅ Logistic Regression
- ✅ Naive Bayes
- ✅ Linear SVM
- ✅ Random Forest
- ✅ Gradient Boosting

### 8. **Model Evaluation**
- Accuracy, Precision, Recall, F1 scores
- Confusion matrix
- Classification report
- Model comparison visualization

### 9. **Hyperparameter Tuning**
- GridSearchCV cho best model
- Cross-validation
- Optimal parameter selection

### 10. **Model Export**
Saved artifacts:
- `tfidf_vectorizer.pkl` - TF-IDF vectorizer
- `sentiment_model.pkl` - Trained model
- `label_mapping.pkl` - Label encoding
- `model_metadata.json` - Training metadata

### 11. **Prediction Testing**
- Test trên new texts
- Confidence scores
- Example predictions

## Requirements

```bash
pip install datasets transformers underthesea scikit-learn pandas matplotlib seaborn wordcloud imbalanced-learn nltk
```

## Quick Start

### Option 1: Jupyter Notebook

```bash
cd notebooks
jupyter notebook sentiment_model_training.ipynb
```

### Option 2: JupyterLab

```bash
cd notebooks
jupyter lab
```

### Option 3: VS Code

Open `sentiment_model_training.ipynb` in VS Code with Jupyter extension.

## Usage

### 1. Run All Cells

Execute all cells từ đầu đến cuối để:
- Load và explore data
- Preprocess text
- Train multiple models
- Export best model

### 2. Step-by-Step Execution

Hoặc chạy từng section để hiểu chi tiết:
- EDA: Cells 1-6
- Preprocessing: Cells 7-8
- Feature Extraction: Cells 9-10
- Training: Cells 11-13
- Export: Cell 14

## Output Files

Sau khi chạy xong notebook, các files sau được tạo ra:

```
data/model_artifacts/sentiment/
├── tfidf_vectorizer.pkl      # TF-IDF vectorizer
├── sentiment_model.pkl        # Trained model
├── label_mapping.pkl          # Label encoder
└── model_metadata.json        # Training info
```

## Model Metadata

File `model_metadata.json` chứa:
```json
{
  "model_name": "Logistic Regression",
  "training_date": "2025-10-25T...",
  "num_training_samples": 12000,
  "num_test_samples": 3000,
  "num_features": 5000,
  "accuracy": 0.8742,
  "f1_macro": 0.8563,
  "f1_weighted": 0.8721,
  "labels": ["positive", "negative", "neutral"],
  "hyperparameters": {...}
}
```

## Integration with Main App

### Load Trained Model

```python
import joblib

# Load artifacts
model = joblib.load('data/model_artifacts/sentiment/sentiment_model.pkl')
vectorizer = joblib.load('data/model_artifacts/sentiment/tfidf_vectorizer.pkl')

# Preprocess new text
def clean_text(text):
    # Your preprocessing logic
    return cleaned_text

# Predict
text = "Dịch vụ ngân hàng rất tốt!"
text_clean = clean_text(text)
text_vector = vectorizer.transform([text_clean])
prediction = model.predict(text_vector)[0]
confidence = model.predict_proba(text_vector)[0].max()

print(f"Sentiment: {prediction} (confidence: {confidence:.2f})")
```

### Update Existing Classifier

Replace the classifier in `src/models/sentiment/classifier.py`:

```python
class SentimentClassifier:
    def __init__(self):
        model_dir = Path("data/model_artifacts/sentiment")
        self.classifier = joblib.load(model_dir / "sentiment_model.pkl")
        self.vectorizer = joblib.load(model_dir / "tfidf_vectorizer.pkl")

    def predict(self, texts):
        vectors = self.vectorizer.transform(texts)
        predictions = self.classifier.predict(vectors)
        return predictions
```

## Expected Results

### Typical Performance (GreenNode dataset)

| Metric | Score |
|--------|-------|
| **Accuracy** | 0.85 - 0.90 |
| **F1 (Macro)** | 0.82 - 0.88 |
| **F1 (Weighted)** | 0.84 - 0.89 |
| **Precision** | 0.83 - 0.88 |
| **Recall** | 0.84 - 0.89 |

### Training Time

- Data loading: ~30 seconds
- Preprocessing: ~2-3 minutes (depending on dataset size)
- Feature extraction: ~1 minute
- Model training: ~2-5 minutes (all models)
- Total: ~8-12 minutes

## Tips & Best Practices

### 1. **Increase Training Data**
Nếu accuracy thấp (<0.80), cần thêm data:
```python
# Load more data hoặc augment
dataset = load_dataset("GreenNode/tweet-sentiment-extraction-vn", split="train[:100%]")
```

### 2. **Adjust TF-IDF Parameters**
Cho dataset nhỏ (<1000 samples):
```python
tfidf_vectorizer = TfidfVectorizer(
    max_features=1000,  # Giảm features
    ngram_range=(1, 1),  # Chỉ unigrams
    min_df=1,  # Relax min_df
    max_df=0.95
)
```

### 3. **Handle Imbalanced Classes**
Nếu class imbalance > 3.0:
```python
smote = SMOTE(random_state=42, k_neighbors=min(5, min_class_count-1))
```

### 4. **Hyperparameter Tuning**
Expand grid search:
```python
param_grid = {
    'C': [0.01, 0.1, 1, 10, 100, 1000],
    'penalty': ['l1', 'l2', 'elasticnet'],
    'solver': ['liblinear', 'saga', 'lbfgs']
}
```

### 5. **Vietnamese Stopwords**
Add domain-specific stopwords:
```python
VIETNAMESE_STOPWORDS.update([
    'ngân_hàng', 'bank', 'atm', 'app'  # Bank-specific
])
```

## Troubleshooting

### Issue: "After pruning, no terms remain"

**Solution:** Giảm min_df và max_df
```python
tfidf_vectorizer = TfidfVectorizer(
    min_df=1,  # Was: 2
    max_df=1.0  # Was: 0.8
)
```

### Issue: Low accuracy (<0.70)

**Possible causes:**
1. Dataset quá nhỏ → Load more data
2. Class imbalance → Apply SMOTE
3. Text preprocessing không đủ tốt → Review clean_text()
4. Model không phù hợp → Try different models

### Issue: SMOTE error "k_neighbors > n_samples"

**Solution:**
```python
from collections import Counter
min_class_count = min(Counter(y_train).values())
k = min(5, min_class_count - 1)
smote = SMOTE(random_state=42, k_neighbors=k)
```

### Issue: Memory error với large dataset

**Solution:** Process in batches
```python
batch_size = 1000
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    # Process batch
```

## Customization

### Change Sentiment Labels

Nếu bạn muốn map sang 6 labels như app:
```python
label_mapping = {
    'positive': 'Positive',
    'very_positive': 'Very Positive',
    'negative': 'Negative',
    'very_negative': 'Very Negative',
    'neutral': 'Neutral',
    'mixed': 'Mixed'
}

train_df[label_col] = train_df[label_col].map(label_mapping)
```

### Add More Features

```python
# Character n-grams
char_vectorizer = TfidfVectorizer(
    analyzer='char',
    ngram_range=(2, 4),
    max_features=1000
)

# Combine with word TF-IDF
from scipy.sparse import hstack
X_combined = hstack([X_train_tfidf, char_features])
```

## Next Steps

1. ✅ Train model với notebook này
2. ✅ Export model artifacts
3. ✅ Load model trong `src/models/sentiment/classifier.py`
4. ✅ Test predictions trong Streamlit app
5. ✅ Monitor performance với ModelCardAgent
6. ✅ Retrain automatically khi degradation detected

## References

- [Underthesea - Vietnamese NLP](https://github.com/undertheseanlp/underthesea)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [SMOTE Paper](https://arxiv.org/abs/1106.1813)

---

**Author:** Bank Text Analysis Team
**Version:** 1.0
**Last Updated:** 2025-10-25
