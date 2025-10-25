# 🏦 Bank Text Analysis - AI-Powered Comment Analytics

<div align="center">

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-orange.svg)
![MLflow](https://img.shields.io/badge/MLflow-2.9.2-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Hệ thống phân tích feedback/comment ngân hàng tự động với AI Agent**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Agentic AI System](#-agentic-ai-system)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [AI Chatbot](#-ai-chatbot)
- [MLflow Tracking](#-mlflow-tracking)
- [API Reference](#-api-reference)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Bank Text Analysis** là hệ thống phân tích comment/feedback ngân hàng tự động, kết hợp:

- 🤖 **AI-Powered Analysis**: Topic modeling & sentiment analysis tự động
- 🧠 **Agentic AI**: Chatbot tương tác với tool calling capabilities
- 📊 **Real-time Monitoring**: Anomaly detection & drift analysis
- 🎨 **Interactive Visualization**: Word clouds, bubble charts, dashboards
- 🔄 **MLOps Ready**: MLflow tracking, model versioning, retraining pipeline

### Use Cases

- ✅ Phân tích feedback khách hàng ngân hàng
- ✅ Tự động phát hiện vấn đề tiêu cực (negative spikes)
- ✅ Monitoring sentiment trends theo thời gian
- ✅ Tạo alerts/reports tự động
- ✅ Training & deploying ML models

---

## ✨ Features

### Core Features

- 📤 **CSV Upload & Validation**: Upload và validate comment data
- 🏷️ **Topic Modeling**:
  - Auto clustering (TF-IDF + KMeans)
  - Supervised classification (Logistic Regression)
- 😊 **Sentiment Analysis**:
  - 6-level classification (Very Negative → Very Positive + Mixed)
  - Trainable models với fallback rule-based
- 📈 **Interactive Visualizations**:
  - Word clouds per topic
  - Bubble charts (topic size vs sentiment)
  - Summary tables & filters
- ✏️ **Edit Mode**: Inline editing labels
- 💾 **Export**: CSV, JSON, Markdown reports

### Advanced Features

- 🤖 **AI Chatbot Assistant**:
  - Natural language interface (Vietnamese)
  - 10+ tools: query data, train models, export reports, create alerts
  - Powered by Ollama (100% free & local)
- 🚀 **True Agentic AI System** (NEW v2.0!):
  - **7 Autonomous Agents** working together:
    - ModelCardAgent: Manages model metadata & performance tracking
    - LearningAgent: Orchestrates continuous improvement
    - AutoTrainer: Autonomous model retraining
    - GoalManager: KPI monitoring & violation detection
    - Monitor: Anomaly & drift detection
    - Planner: Action planning from violations
    - Executor: Executes planned actions
  - **Message Bus**: Event-driven inter-agent communication
  - **Continuous Learning**: Auto-detects degradation & triggers retraining
  - **Active Learning**: Identifies uncertain predictions for labeling
  - **Model Cards**: Full model lineage & performance history
- 📊 **MLflow Integration**:
  - Experiment tracking
  - Model versioning & registry
  - Metrics visualization
- 🔄 **Auto-Retraining Pipeline**: Models improve continuously without manual intervention

---

## 🛠️ Tech Stack

### Core Technologies

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Data Processing** | Pandas | ETL pipeline |
| **ML Framework** | scikit-learn | Topic & sentiment models |
| **UI Framework** | Streamlit | Interactive web app |
| **Visualization** | Plotly, Matplotlib, WordCloud | Charts & graphs |
| **MLOps** | MLflow | Experiment tracking |
| **LLM** | Ollama (Llama 3.2) | AI Chatbot (local) |

### Models & Algorithms

- **Topic Modeling**: TF-IDF + KMeans / Logistic Regression
- **Sentiment Analysis**: TF-IDF + Logistic Regression (6-class)
- **Vietnamese NLP**: underthesea tokenization
- **Anomaly Detection**: Distribution drift detection (KL divergence)

---

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip
- (Optional) Ollama for AI Chatbot

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/bank-text-demo.git
cd bank-text-demo
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment

```bash
cp .env.example .env
# Edit .env with your configurations
```

### Step 5: Create Data Folders

```bash
# Windows
mkdir data\raw data\processed data\labeled data\model_artifacts\topic data\model_artifacts\sentiment

# Linux/Mac
mkdir -p data/{raw,processed,labeled,model_artifacts/{topic,sentiment}}
```

---

## 🚀 Quick Start

### 1. Run the App

```bash
streamlit run app.py
```

App will open at `http://localhost:8501`

### 2. Upload Sample Data

Create `data/raw/sample.csv`:

```csv
id,timestamp,comment,source
1,2025-10-20T08:12:00Z,Ứng dụng báo lỗi khi chuyển tiền,app
2,2025-10-20T09:30:00Z,Giao dịch nhanh chóng tiện lợi,app
3,2025-10-20T10:15:00Z,Không thể đăng nhập vào ứng dụng,app
```

### 3. Analyze Data

1. Go to **Tab 1: Upload & Analyze**
2. Upload `sample.csv`
3. Click **Run Analysis**
4. View results in **Tab 2: Visualizations**

### 4. (Optional) Setup AI Chatbot

```bash
# Install Ollama
# Download from: https://ollama.com/download

# Pull model
ollama pull llama3.2:3b

# Chatbot ready in Tab 6!
```

---

## 📖 Usage Guide

### Tab 1: Upload & Analyze

**Input CSV Format:**

| Column | Required | Description |
|--------|----------|-------------|
| `comment` | ✅ Yes | Comment text |
| `id` | ❌ No | Unique identifier |
| `timestamp` | ❌ No | ISO 8601 format |
| `source` | ❌ No | Source (app/web/call) |

**Process:**
1. Upload CSV
2. Click "Run Analysis"
3. Auto topic clustering (8 clusters)
4. Sentiment classification (6 levels)

### Tab 2: Visualizations

- **Sentiment Distribution**: Bar chart
- **Topic Summary**: Table with counts
- **Bubble Chart**: Topic size vs avg sentiment
- **Word Cloud**: Top words per topic (filterable)

### Tab 3: Edit & Export

- **Filters**: Topic, sentiment, source, date range
- **View**: Interactive data table
- **Export**: Download filtered CSV

### Tab 4: Training

**Train Sentiment Model:**

Create `data/labeled/sentiment_train.csv`:
```csv
comment,sentiment_label
Rất tuyệt vời xuất sắc,Very Positive
Dịch vụ tốt hài lòng,Positive
Bình thường không có gì đặc biệt,Neutral
Chậm lắm thất vọng,Negative
Rất tệ lừa đảo,Very Negative
Tốt nhưng còn lag,Mixed
```

Upload → Train → View metrics (Accuracy, F1)

**Train Topic Model:**

Create `data/labeled/topic_train.csv`:
```csv
comment,topic_label
Chuyển tiền bị lỗi,Transfer Issues
Không đăng nhập được,Login Issues
Nhân viên tư vấn tốt,Customer Service
```

Upload → Train

### Tab 5: 🤖 True Agentic AI - Multi-Agent System

**Autonomous Workflows:**

1. **Run Full Agentic Workflow**
   - Initializes 7 autonomous agents
   - Stores baseline metrics
   - Checks goal violations
   - Detects anomalies
   - Creates and executes action plans
   - Runs learning cycle if due
   - Reviews all model cards

2. **Trigger Continuous Improvement**
   - Forces immediate learning cycle
   - Processes training queue
   - Identifies uncertain samples for labeling
   - Updates performance baselines

3. **Get System Status**
   - View active agents (7 total)
   - Monitor model cards
   - Check learning status
   - View recent improvements

4. **Agent Communications**
   - View inter-agent messages
   - Monitor coordination history
   - Audit message bus events

5. **Model Cards & Performance**
   - View all trained models
   - Track performance history
   - Compare model versions
   - Monitor degradation

**Key Features:**
- ✨ Event-driven agent communication via Message Bus
- 🔄 Continuous learning with auto-retraining
- 🎯 Active learning for uncertain predictions
- 📊 Model cards with full lineage tracking
- 🚨 Auto-detection of performance degradation

### Tab 6: 💬 AI Chatbot

**Example Commands:**

```
👤 Cho tôi thống kê tổng quan
👤 Top 5 vấn đề tiêu cực là gì?
👤 Kiểm tra anomalies
👤 Train sentiment model từ data/labeled/sentiment_sample.csv
👤 Export báo cáo CSV
👤 Phân tích file data/raw/new_comments.csv
```

**Available Tools (10+):**
- Query & filter data
- Get summary stats
- Find top issues
- Check anomalies
- Train models
- Export reports
- Create alerts
- Full analysis pipeline

See [CHATBOT_GUIDE.md](CHATBOT_GUIDE.md) for details.

---

## 🤖 Agentic AI System

### Architecture Overview

The system implements **True Agentic AI** with 7 autonomous agents communicating via a Message Bus:

```
┌─────────────────────────────────────────────────────────┐
│                    Message Bus                           │
│         (Event-Driven Communication Layer)               │
└─────────────────────────────────────────────────────────┘
        ▲           ▲           ▲           ▲
        │           │           │           │
┌───────┴─────┐ ┌───┴───────┐ ┌─┴─────────┐ ┌─────┴──────┐
│ModelCard    │ │Learning   │ │Auto       │ │Goal        │
│Agent        │ │Agent      │ │Trainer    │ │Manager     │
└─────────────┘ └───────────┘ └───────────┘ └────────────┘
        ▲           ▲           ▲
        │           │           │
┌───────┴─────┐ ┌───┴───────┐ ┌─┴─────────┐
│Monitor      │ │Planner    │ │Executor   │
│Agent        │ │Agent      │ │Agent      │
└─────────────┘ └───────────┘ └───────────┘
```

### The 7 Agents

| Agent | Responsibility | Key Events |
|-------|---------------|------------|
| **ModelCardAgent** | Manages model metadata & performance tracking | `model.trained`, `model.degradation_detected` |
| **LearningAgent** | Orchestrates continuous improvement cycles | `learning.cycle_completed`, `learning.improvement_detected` |
| **AutoTrainer** | Autonomous model retraining | `training.queued`, `model.trained` |
| **GoalManager** | Monitors KPIs and detects violations | `goals.violations_detected` |
| **Monitor** | Anomaly & drift detection | `monitor.anomalies_detected` |
| **Planner** | Creates action plans from violations | `plan.created` |
| **Executor** | Executes planned actions | `action.executed` |

### Key Features

**1. Message Bus Communication**
- Pub/Sub pattern for loose coupling
- Priority-based message queue (LOW, MEDIUM, HIGH, CRITICAL)
- Request/Response pattern with timeout
- Full message history for auditing

**2. Continuous Learning**
- Automatic performance degradation detection (>10% drop)
- Scheduled learning cycles (default: 24 hours)
- Auto-retraining when degradation detected
- Performance baseline tracking

**3. Active Learning**
- Identifies uncertain predictions (confidence < 70%)
- Three sampling strategies:
  - Confidence-based sampling
  - Margin sampling (top1 - top2 probabilities)
  - Entropy sampling (prediction uncertainty)
- Suggests samples for human labeling

**4. Model Cards**
- Full model lineage and metadata
- Performance history tracking
- Hyperparameter logging
- Deployment status tracking
- Retraining trigger history

### Communication Flow Example

```
User uploads new data → Analysis complete
  ↓
ModelCardAgent evaluates performance
  ↓
Performance drops 15% → Publishes: model.degradation_detected
  ↓
AutoTrainer receives event → Adds to training queue
  ↓
LearningAgent receives event → Triggers immediate cycle
  ↓
AutoTrainer retrains model → Publishes: model.trained
  ↓
ModelCardAgent creates new card → Publishes: model.card_created
  ↓
LearningAgent updates baseline → Publishes: learning.improvement_detected
```

### Documentation

- **[AGENTIC_AI_GUIDE.md](AGENTIC_AI_GUIDE.md)** - Complete architecture documentation
- **[AGENTIC_QUICKSTART.md](AGENTIC_QUICKSTART.md)** - Quick start guide (Vietnamese)

---

## 📁 Project Structure

```
bank-text-demo/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── app.py                             # Main Streamlit app
│
├── config/
│   ├── settings.py                    # App configuration
│   └── model_config.py                # Model hyperparameters
│
├── src/
│   ├── etl/
│   │   ├── loader.py                  # CSV loading & validation
│   │   ├── preprocessor.py            # Text preprocessing
│   │   └── pii_mask.py                # PII masking utilities
│   │
│   ├── models/
│   │   ├── topic/
│   │   │   ├── auto_topic.py          # KMeans clustering
│   │   │   └── supervised_topic.py    # Topic classifier
│   │   ├── sentiment/
│   │   │   ├── classifier.py          # Sentiment classifier
│   │   │   └── fallback.py            # Rule-based fallback
│   │   └── trainer.py                 # Training pipeline
│   │
│   ├── viz/
│   │   ├── wordcloud.py               # Word cloud generator
│   │   ├── bubble_chart.py            # Bubble charts
│   │   └── table_view.py              # Data tables
│   │
│   ├── agents/                        # Agentic AI System (NEW v2.0!)
│   │   ├── message_bus.py             # Event-driven communication
│   │   ├── model_card_agent.py        # Model metadata management
│   │   ├── learning_agent.py          # Continuous learning orchestration
│   │   ├── coordinator.py             # Multi-agent coordinator
│   │   ├── goal_manager.py            # KPI goals & tracking
│   │   ├── monitor.py                 # Anomaly detection
│   │   ├── planner.py                 # Action planning
│   │   ├── executor.py                # Action execution
│   │   └── memory.py                  # Agent memory
│   │
│   ├── models/
│   │   ├── active_learner.py          # Active learning module (NEW!)
│   │   ├── auto_trainer.py            # Autonomous retraining (NEW!)
│   │   └── ...
│   │
│   ├── alerts/
│   │   ├── email_sender.py            # Email alerts
│   │   ├── slack_sender.py            # Slack webhooks
│   │   └── ticket_creator.py          # Jira integration
│   │
│   ├── chatbot/                       # AI Chatbot
│   │   ├── ollama_client.py           # Ollama API client
│   │   ├── tools.py                   # Tool definitions
│   │   └── agent.py                   # ChatbotAgent
│   │
│   └── utils/
│       ├── logger.py                  # Logging utilities
│       ├── metrics.py                 # Evaluation metrics
│       └── export.py                  # Export utilities
│
├── data/
│   ├── raw/                           # Uploaded CSVs
│   ├── processed/                     # Cleaned data
│   ├── labeled/                       # Training data
│   └── model_artifacts/               # Saved models
│       ├── topic/
│       └── sentiment/
│
├── scripts/
│   ├── train_sentiment.py             # Standalone training
│   ├── train_topic.py
│   ├── run_monitoring.py              # Monitoring job
│   └── clean_models.py                # Model cleanup
│
└── docs/
    ├── AGENTIC_AI_GUIDE.md            # Agentic AI architecture (NEW!)
    ├── AGENTIC_QUICKSTART.md          # Agentic AI quick start (NEW!)
    ├── OLLAMA_SETUP.md                # Ollama installation
    ├── CHATBOT_GUIDE.md               # Chatbot usage guide
    └── MLFLOW_GUIDE.md                # MLflow guide
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```env
# Paths
DATA_DIR=data
MODEL_DIR=data/model_artifacts
MLFLOW_TRACKING_URI=file:///./mlruns

# Email Alerts (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ALERT_EMAIL=ops@yourbank.com

# Slack Alerts (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Jira Integration (optional)
JIRA_URL=https://your-company.atlassian.net
JIRA_USER=your-email@example.com
JIRA_TOKEN=your-api-token
JIRA_PROJECT=OPS

# KPI Thresholds
KPI_SENTIMENT_ACCURACY_MIN=0.88
KPI_NEGATIVE_SPIKE_THRESHOLD=0.2
KPI_DRIFT_THRESHOLD=0.15
```

### Model Configurations

Edit `config/model_config.py`:

```python
TFIDF_CONFIG = {
    "max_features": 5000,
    "ngram_range": (1, 2),
    "min_df": 1,
    "max_df": 0.95
}

KMEANS_CONFIG = {
    "n_clusters": 8,  # Number of topics
    "random_state": 42
}
```

---

## 🤖 AI Chatbot

### Setup

```bash
# 1. Install Ollama
# Download: https://ollama.com/download

# 2. Pull model (choose one)
ollama pull llama3.2:3b    # Recommended (3GB)
ollama pull llama3.2:1b    # Lightweight (1GB)
ollama pull gemma2:2b      # Alternative (2GB)

# 3. Verify
ollama list
```

### Usage Examples

```bash
# Query data
👤 Cho tôi thống kê tổng quan
👤 Có bao nhiêu comment về chuyển tiền?

# Find issues
👤 Top 5 vấn đề tiêu cực là gì?
👤 Tìm các comment về app performance

# Train models
👤 Train sentiment model từ data/labeled/sentiment_sample.csv
👤 Train topic model từ data/labeled/topic_sample.csv

# Export & alerts
👤 Export báo cáo CSV với tên report_final
👤 Gửi email alert về negative spike
👤 Tạo log alert: "Phát hiện vấn đề nghiêm trọng"

# Full workflow
👤 Phân tích file data/raw/new_comments.csv
👤 Kiểm tra anomalies
```

See [CHATBOT_GUIDE.md](CHATBOT_GUIDE.md) for full documentation.

---

## 📊 MLflow Tracking

### Start MLflow UI

```bash
mlflow ui
```

Open: `http://localhost:5000`

### Features

- **Experiments**: sentiment_training, topic_training
- **Metrics**: accuracy, f1_macro, f1_weighted
- **Parameters**: n_samples, n_classes, hyperparameters
- **Artifacts**: Model files (.pkl)
- **Compare**: Multiple runs side-by-side

See [MLFLOW_GUIDE.md](MLFLOW_GUIDE.md) for details.

---

## 📚 API Reference

### Command Line Scripts

**Train Sentiment Model:**
```bash
python scripts/train_sentiment.py \
  --data data/labeled/sentiment.csv \
  --mlflow
```

**Train Topic Model:**
```bash
python scripts/train_topic.py \
  --data data/labeled/topic.csv \
  --mode supervised \
  --mlflow
```

**Run Monitoring:**
```bash
python scripts/run_monitoring.py \
  --data data/raw/comments.csv \
  --execute \
  --save-baseline
```

**Clean Models:**
```bash
python scripts/clean_models.py --type all
```

### Python API

```python
from src.models.trainer import train_sentiment_model

# Train sentiment model
texts = ["Rất tốt", "Tệ quá", "Bình thường"]
labels = ["Positive", "Negative", "Neutral"]

model, metrics = train_sentiment_model(texts, labels, log_mlflow=True)
print(f"Accuracy: {metrics['accuracy']:.3f}")
```

---

## 🗺️ Roadmap

### Current Version (v1.0)

- ✅ Pandas-based ETL
- ✅ scikit-learn models
- ✅ Streamlit UI
- ✅ MLflow tracking
- ✅ Agentic AI monitoring
- ✅ AI Chatbot (Ollama)

### Planned Features

#### v1.1 - Enhanced NLP
- [ ] HuggingFace Transformers (PhoBERT)
- [ ] Fine-tuned Vietnamese models
- [ ] Advanced tokenization

#### v1.2 - Scalability
- [ ] PySpark distributed processing
- [ ] Vector DB (Milvus/Pinecone)
- [ ] Redis caching

#### v1.3 - MLOps
- [ ] Airflow orchestration
- [ ] CI/CD pipeline
- [ ] Model A/B testing

#### v1.4 - Deployment
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Production monitoring

#### v2.0 - Enterprise
- [ ] Multi-tenant support
- [ ] Role-based access control
- [ ] Audit logging
- [ ] Data encryption

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Code formatting
black src/
isort src/

# Type checking
mypy src/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Ollama** - Free local LLM inference
- **scikit-learn** - Machine learning library
- **Streamlit** - Web app framework
- **MLflow** - MLOps platform
- **underthesea** - Vietnamese NLP toolkit

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/bank-text-demo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/bank-text-demo/discussions)
- **Email**: lamminhquang0411@gmail.com 

---

<div align="center">

**Made with ❤️ for Vietnamese Banking Industry**

⭐ Star this repo if you find it helpful!

</div>
