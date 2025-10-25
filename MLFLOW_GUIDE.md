# Hướng dẫn sử dụng MLflow

## MLflow là gì?

MLflow là công cụ quản lý vòng đời machine learning models, giúp tracking experiments, parameters, metrics và artifacts.

## Setup MLflow

MLflow đã được cài đặt sẵn trong `requirements.txt` và config sẵn trong `.env`:

```env
MLFLOW_TRACKING_URI=file:///./mlruns
```

## Sử dụng trong Streamlit App

### 1. Training với MLflow

Trong tab "Training" của app:

1. ✅ Check vào "Enable MLflow Tracking" (mặc định đã bật)
2. Upload CSV labeled data
3. Click "Train Sentiment Model" hoặc "Train Topic Model"
4. Sau khi train xong, bạn sẽ thấy metrics hiển thị

### 2. Xem MLflow UI

Mở terminal mới và chạy:

```bash
cd C:\Users\PC\bank-text-demo
mlflow ui
```

Sau đó mở browser tại: **http://localhost:5000**

### 3. Xem Experiments trong MLflow UI

MLflow UI cho phép bạn:

- **Experiments**: Xem tất cả experiments (sentiment_training, topic_training, topic_auto_training)
- **Runs**: Xem từng lần training với params và metrics
- **Compare**: So sánh nhiều runs với nhau
- **Artifacts**: Download models đã train
- **Charts**: Visualize metrics theo thời gian

## Ví dụ sử dụng

### Training Sentiment Model với MLflow

```python
from src.models.trainer import train_sentiment_model

texts = ["Rất tốt", "Tệ quá", "Bình thường"]
labels = ["Positive", "Negative", "Neutral"]

model, metrics = train_sentiment_model(texts, labels, log_mlflow=True)

print(f"Accuracy: {metrics['accuracy']:.3f}")
print(f"F1 Macro: {metrics['f1_macro']:.3f}")
```

Sau khi chạy, vào MLflow UI để xem:
- Params: n_samples, n_classes
- Metrics: accuracy, f1_macro, f1_weighted
- Artifacts: vectorizer.pkl, classifier.pkl, metadata.pkl

### Training từ command line

```bash
# Train sentiment với MLflow
python scripts/train_sentiment.py --data data/labeled/sentiment.csv --mlflow

# Train topic với MLflow
python scripts/train_topic.py --data data/labeled/topic.csv --mode supervised --mlflow
```

## So sánh Models trong MLflow

1. Mở MLflow UI: http://localhost:5000
2. Click vào experiment (ví dụ: "sentiment_training")
3. Chọn nhiều runs (checkbox bên trái)
4. Click "Compare"
5. Xem bảng so sánh metrics, params

## Export Model từ MLflow

Trong MLflow UI:
1. Click vào run
2. Scroll xuống "Artifacts"
3. Click "Download" để tải model artifacts

## Troubleshooting

### Lỗi: "No such experiment"
Solution: Run training ít nhất 1 lần để tạo experiment

### Lỗi: "Port 5000 already in use"
Solution:
```bash
mlflow ui --port 5001
```

### MLflow UI không hiển thị data
Solution: Kiểm tra folder `mlruns/` đã được tạo chưa

## Best Practices

1. **Luôn enable MLflow** khi train để track metrics
2. **Đặt tên run có ý nghĩa**: Thêm tag hoặc note trong MLflow UI
3. **So sánh models thường xuyên**: Để chọn model tốt nhất
4. **Backup mlruns/**: Folder này chứa toàn bộ history

## Tích hợp với CI/CD

Trong production, có thể setup MLflow Tracking Server:

```bash
mlflow server --host 0.0.0.0 --port 5000
```

Sau đó update `.env`:
```env
MLFLOW_TRACKING_URI=http://your-mlflow-server:5000
```
