# Agentic AI Quick Start Guide

## Giới thiệu nhanh

Hệ thống Agentic AI của chúng tôi bao gồm **7 agents tự chủ** làm việc cùng nhau để cải tiến liên tục các models machine learning.

### 7 Agents chính:

1. **ModelCardAgent** - Quản lý metadata và performance của models
2. **LearningAgent** - Điều phối continuous learning
3. **AutoTrainer** - Tự động retrain models
4. **GoalManager** - Theo dõi KPIs và goals
5. **Monitor** - Phát hiện anomalies và drift
6. **Planner** - Tạo action plans
7. **Executor** - Thực thi actions

## Cách sử dụng trong Streamlit App

### Bước 1: Upload và phân tích dữ liệu

1. Vào tab **"Upload & Analyze"**
2. Upload file CSV (phải có cột `comment`)
3. Click **"Run Analysis"**

### Bước 2: Khởi động Agentic AI System

1. Vào tab **"🤖 True Agentic AI - Multi-Agent System"**
2. Hệ thống sẽ tự động initialize 7 agents
3. Bạn sẽ thấy: ✅ Multi-Agent System initialized with 7 agents

### Bước 3: Chạy Autonomous Workflow

Click **"Run Full Agentic Workflow"** để:
- Lưu baseline metrics
- Kiểm tra goal violations
- Phát hiện anomalies
- Tạo và thực thi action plans
- Chạy learning cycle (nếu đến lúc)
- Review tất cả model cards

### Bước 4: Trigger Continuous Improvement

Click **"Trigger Continuous Improvement"** để:
- Chạy learning cycle ngay lập tức
- Process training queue
- Identify uncertain samples cần label
- Update performance baselines

### Bước 5: Xem System Status

Click **"Get System Status"** để xem:
- Số lượng active agents
- Tổng số model cards
- Learning status (last cycle, next cycle)
- Recent improvements

### Bước 6: Monitor Agent Communications

- **View Agent Messages**: Xem messages giữa các agents
- **View Coordination History**: Xem lịch sử coordination actions

### Bước 7: Xem Model Cards

Click **"View All Model Cards"** để xem:
- Tất cả models đã được train
- Performance metrics (accuracy, F1, etc.)
- Status và deployment info

## Tính năng tự động

### 1. Auto-Detection Performance Degradation

Khi model accuracy giảm > 10%:
```
ModelCardAgent phát hiện → publish event
  ↓
AutoTrainer nhận event → thêm vào training queue
  ↓
LearningAgent trigger immediate cycle
  ↓
Model được retrain tự động
```

### 2. Continuous Learning Cycle (24h)

Mỗi 24 giờ, hệ thống tự động:
- Kiểm tra training queue
- Process pending training tasks
- Identify uncertain predictions
- Update baselines

### 3. Active Learning

Hệ thống tự động tìm predictions không chắc chắn:
- Confidence < 70% → mark as uncertain
- Sắp xếp theo uncertainty score
- Gợi ý top samples cần human labeling

## Workflow điển hình

### Workflow 1: First Time Setup

```
1. Upload data → Run Analysis
2. Vào tab Agentic AI
3. Run Full Agentic Workflow
4. System creates baseline và model cards
```

### Workflow 2: Daily Monitoring

```
1. Upload new data → Run Analysis
2. Run Full Agentic Workflow
3. System detects violations/anomalies
4. Auto-creates và executes action plans
```

### Workflow 3: Manual Improvement

```
1. Trigger Continuous Improvement
2. Xem uncertain samples
3. Label uncertain samples (trong tab Edit & Export)
4. Upload labeled data → Train model
5. System auto-creates new model card
```

### Workflow 4: Model Performance Tracking

```
1. View All Model Cards
2. Xem performance history
3. So sánh models qua các versions
4. Identify models cần retrain
```

## Ví dụ cụ thể

### Ví dụ 1: Phát hiện và xử lý Negative Spike

```
Scenario: Đột ngột có nhiều comments tiêu cực

1. Upload data → Run Analysis
2. Run Full Agentic Workflow

Hệ thống tự động:
✓ Monitor detects negative spike (+15%)
✓ GoalManager identifies violation (threshold: 10%)
✓ Planner creates action: "alert_ops"
✓ Executor sends alert (email/slack)
✓ Learning cycle triggered để retrain model
```

### Ví dụ 2: Model Accuracy giảm

```
Scenario: Sentiment model accuracy từ 0.92 → 0.78

Hệ thống tự động:
✓ ModelCardAgent detects degradation
✓ Publishes: model.degradation_detected
✓ AutoTrainer adds to queue
✓ LearningAgent triggers immediate cycle
✓ Model được retrain với data mới
✓ New model card được tạo
✓ Performance comparison available
```

### Ví dụ 3: Continuous Improvement với Active Learning

```
1. Run Analysis → 1000 comments
2. System predicts sentiment
3. Active Learning identifies 50 uncertain samples
4. Trong tab "Edit & Export":
   - Filter by sentiment_score < 0.7
   - Review và edit labels
   - Export labeled data
5. Trong tab "Training":
   - Upload labeled CSV
   - Train Sentiment Model
6. System auto-creates model card
7. LearningAgent updates baseline
```

## Message Bus Events

### Events bạn có thể monitor:

- `model.trained` - Model vừa được train xong
- `model.degradation_detected` - Performance giảm
- `learning.cycle_completed` - Learning cycle hoàn thành
- `goals.violations_detected` - KPI violations
- `monitor.anomalies_detected` - Anomalies phát hiện
- `training.queued` - Training task added

### Xem message history:

```python
# Trong code
coordinator = st.session_state.coordinator
messages = coordinator.get_agent_communications(limit=20)
```

## Tuning và Configuration

### Thay đổi Learning Cycle Interval

```python
# Default: 24 hours
# Thay đổi thành 12 hours:
coordinator.learning_agent.configure_learning_interval(hours=12)
```

### Thay đổi Active Learning Threshold

```python
# Default: 0.3 (samples với confidence < 0.7)
# Thay đổi thành 0.2 (confidence < 0.8):
coordinator.learning_agent.active_learner.uncertainty_threshold = 0.2
```

### Thay đổi Minimum Training Samples

```python
# Default: 10 samples
# Thay đổi thành 20:
coordinator.learning_agent.auto_trainer.min_samples_for_training = 20
```

### Thay đổi Goals/KPIs

```python
# Trong GoalManager
new_goals = {
    "sentiment_accuracy": {
        "metric": "sentiment_accuracy",
        "threshold": 0.85,  # Thay từ 0.7 → 0.85
        "operator": ">=",
        "priority": "high",
        "action": "retrain_sentiment"
    }
}

coordinator.goal_manager.goals.update(new_goals)
coordinator.goal_manager.save_goals()
```

## Troubleshooting

### ❌ Agents không communicate

**Kiểm tra:**
```python
coordinator = st.session_state.coordinator
messages = coordinator.get_agent_communications(limit=10)
print(f"Messages: {len(messages)}")
```

**Giải pháp:** Re-initialize coordinator
```python
st.session_state.coordinator = None
# Refresh page
```

### ❌ Learning cycle không trigger

**Kiểm tra:**
```python
status = coordinator.learning_agent.get_learning_status()
print(status['next_cycle_in'])
```

**Giải pháp:** Force trigger
```python
coordinator.trigger_continuous_improvement(df)
```

### ❌ Training queue không process

**Kiểm tra:**
```python
stats = coordinator.learning_agent.auto_trainer.get_training_statistics()
print(f"Queue: {stats['queue_size']}")
```

**Giải pháp:** Manual process
```python
results = coordinator.learning_agent.auto_trainer.process_training_queue(df)
```

## Best Practices

### 1. Định kỳ chạy Full Workflow

- Mỗi ngày: Run Full Agentic Workflow
- Xem violations và anomalies
- Review action plans trước khi execute

### 2. Monitor Model Cards

- Weekly: Xem all model cards
- Compare performance trends
- Identify models cần attention

### 3. Active Learning Strategy

- Export uncertain samples
- Batch labeling (20-50 samples/lần)
- Retrain khi đủ labeled data

### 4. Baseline Updates

- Update baseline sau major changes
- Monthly baseline refresh
- Keep history for comparison

### 5. Goal Tuning

- Review goals quarterly
- Adjust thresholds dựa trên business needs
- Add new goals khi cần

## FAQs

**Q: Bao lâu learning cycle chạy 1 lần?**
A: Default là 24 giờ, có thể configure.

**Q: Agents có cần internet không?**
A: Không, toàn bộ chạy local.

**Q: Model Cards lưu ở đâu?**
A: `models/cards/*.json`

**Q: Có thể tắt auto-training không?**
A: Có, đừng click "Trigger Continuous Improvement". System sẽ chỉ suggest actions.

**Q: Message history lưu bao lâu?**
A: Message history in-memory, mất khi restart app. Có thể extend để persist.

**Q: Có thể add thêm agents không?**
A: Có, tạo class mới extend từ base agent, subscribe vào message bus.

---

**Tip:** Bắt đầu đơn giản với Run Full Agentic Workflow, sau đó explore từng feature!
