# 🚀 Bank Text Analysis v2.0 - Agentic AI Upgrade

### Version 2.0 (Hiện tại) ✨
```
✅ 7 Agents tự chủ (autonomous)
✅ Message Bus giao tiếp (event-driven)
✅ Auto-retrain khi phát hiện degradation
✅ Continuous learning cycles (24h)
✅ Active learning tự động
✅ Model Cards với full lineage
```

## 📦 Các thành phần mới

### 1. Message Bus (`src/agents/message_bus.py`)
**Backbone giao tiếp cho tất cả agents**

Tính năng:
- Pub/Sub pattern
- Priority queue (LOW → CRITICAL)
- Request/Response với timeout
- Message history cho audit

### 2. Model Card Agent (`src/agents/model_card_agent.py`)
**Quản lý metadata và tracking performance của models**

Tính năng:
- Tự động tạo model card khi train
- Track performance history
- Phát hiện degradation (>10% drop)
- Lưu trữ tại `models/cards/*.json`

### 3. Learning Agent (`src/agents/learning_agent.py`)
**Điều phối continuous improvement**

Tính năng:
- Learning cycles định kỳ (24h)
- Tích hợp Active Learning
- Tích hợp Auto Trainer
- Track improvements theo thời gian

### 4. Auto Trainer (`src/models/auto_trainer.py`)
**Autonomous model retraining**

Tính năng:
- Training queue với priority
- Tự động retrain khi degradation
- Validation trước khi train
- MLflow integration (optional)

### 5. Active Learner (`src/models/active_learner.py`)
**Chọn samples cần human labeling**

Chiến lược:
- Confidence-based sampling
- Margin sampling
- Entropy sampling

### 6. Multi-Agent Coordinator (`src/agents/coordinator.py`)
**Điều phối 7 agents**

Methods:
- `run_full_agentic_workflow(df)`: Chạy toàn bộ workflow
- `trigger_continuous_improvement(df)`: Force learning cycle
- `get_system_status()`: Xem status của hệ thống

### 7. Agents hiện có được nâng cấp
**GoalManager, Monitor, Planner, Executor**
- Tích hợp với Message Bus
- Subscribe/Publish events
- Agent-to-agent communication

## 🔄 Luồng hoạt động mới

### Luồng 1: Auto-detect và retrain

```
1. User upload data mới
2. Analysis chạy với model hiện tại
3. ModelCardAgent evaluates performance
4. Accuracy giảm từ 0.92 → 0.78
   ↓
   ModelCardAgent.publish(model.degradation_detected)
   ↓
5. AutoTrainer nhận event → add vào queue
6. LearningAgent nhận event → trigger immediate cycle
   ↓
7. AutoTrainer process queue → retrain model
   ↓
   AutoTrainer.publish(model.trained)
   ↓
8. ModelCardAgent nhận event → create new card
9. LearningAgent update baseline
   ↓
   LearningAgent.publish(learning.improvement_detected)
```

### Luồng 2: Continuous Learning Cycle (24h)

```
Mỗi 24 giờ (hoặc manual trigger):

1. LearningAgent kiểm tra: đến lúc learning cycle?
2. Check training queue → process nếu có
3. Active Learning identifies uncertain samples
4. Update performance baselines
5. Publish learning.cycle_completed event
```

### Luồng 3: Active Learning

```
1. Model predicts 1000 samples
2. ActiveLearner analyzes probabilities
3. Identifies 50 samples với confidence < 70%
4. Publish learning.uncertain_samples_found
5. User có thể label trong tab "Edit & Export"
6. Upload labeled data → trigger retraining
```

## 🆕 UI Changes (Tab 5)

### Trước đây:
```
Tab 5: Agentic AI - Monitoring & Planning
- Run Monitoring button
- View anomalies/violations
- Manual plan execution
```

### Bây giờ:
```
Tab 5: 🤖 True Agentic AI - Multi-Agent System
┌─────────────────────────────────────────┐
│ 🚀 Autonomous Actions                   │
│ - Run Full Agentic Workflow             │
│ - Trigger Continuous Improvement        │
│                                         │
│ 📊 System Status                        │
│ - Active Agents: 7                      │
│ - Model Cards: X                        │
│ - Learning Status                       │
│                                         │
│ 📡 Agent Communications                 │
│ - View Agent Messages                   │
│ - View Coordination History             │
│                                         │
│ 🎯 Model Cards & Performance            │
│ - View All Model Cards                  │
│ - Performance history                   │
└─────────────────────────────────────────┘
```

## 📚 Tài liệu mới

| File | Mô tả |
|------|-------|
| **AGENTIC_AI_GUIDE.md** | Tài liệu kiến trúc chi tiết (English) |
| **AGENTIC_QUICKSTART.md** | Hướng dẫn sử dụng nhanh (Vietnamese) |
| **UPGRADE_V2.0.md** | File này - Hướng dẫn upgrade |

## 🎓 Hướng dẫn sử dụng

### Bước 1: Làm quen với UI mới

1. Vào tab **"🤖 True Agentic AI - Multi-Agent System"**
2. Upload và analyze data (nếu chưa có)
3. System sẽ tự động initialize 7 agents

### Bước 2: Chạy first workflow

1. Click **"Run Full Agentic Workflow"**
2. Quan sát các bước được thực hiện:
   - ✓ baseline_stored
   - ✓ goals_checked
   - ✓ violations_checked
   - ✓ model_cards_reviewed

### Bước 3: Xem System Status

1. Click **"Get System Status"**
2. Xem:
   - Active Agents: 7
   - Model Cards: số lượng models
   - Learning Status: last cycle, next cycle

### Bước 4: Monitor communications

1. Click **"View Agent Messages"**
2. Xem messages giữa các agents
3. Click **"View Coordination History"**
4. Xem lịch sử coordination actions

### Bước 5: Trigger improvement

1. Click **"Trigger Continuous Improvement"**
2. System sẽ:
   - Force learning cycle ngay
   - Process training queue
   - Identify uncertain samples
   - Update baselines

## 🔧 Configuration mới

### Learning Cycle Interval

```python
# Default: 24 hours
# Thay đổi trong code (future: sẽ có UI config)
coordinator.learning_agent.configure_learning_interval(hours=12)
```

### Active Learning Threshold

```python
# Default: 0.3 (confidence < 70% → uncertain)
coordinator.learning_agent.active_learner.uncertainty_threshold = 0.2
```

### Auto Trainer Settings

```python
# Minimum samples để train
coordinator.learning_agent.auto_trainer.min_samples_for_training = 20

# Accuracy threshold để trigger retrain
coordinator.learning_agent.auto_trainer.retrain_threshold_accuracy = 0.75
```

## 🆚 So sánh v1.0 vs v2.0

| Tính năng | v1.0 | v2.0 |
|-----------|------|------|
| **Architecture** | Workflow sequential | Multi-Agent autonomous |
| **Communication** | Direct function calls | Message Bus (event-driven) |
| **Retraining** | Manual upload + train | Auto-detect + retrain |
| **Learning** | One-time training | Continuous learning cycles |
| **Model Tracking** | File-based only | Model Cards + lineage |
| **Active Learning** | ❌ Không có | ✅ 3 strategies |
| **Degradation Detection** | ❌ Manual check | ✅ Auto-detect >10% drop |
| **Agent Communication** | ❌ N/A | ✅ Pub/Sub, Request/Response |
| **Observability** | Logs only | Message history + cards |

## ⚠️ Breaking Changes

**Không có breaking changes!**

- Tất cả code cũ vẫn hoạt động
- Tabs 1-4, 6 không thay đổi
- Chỉ Tab 5 được nâng cấp UI
- Backward compatible 100%

## 🐛 Known Issues

1. **Message history in-memory**: Mất khi restart app
   - Future: Sẽ persist vào database

2. **Learning cycle config**: Chưa có UI config
   - Future: Sẽ có settings UI

3. **Model Card visualization**: Chưa có charts
   - Future: Sẽ có performance trend charts

## 🎯 Next Steps (v2.1 roadmap)

- [ ] Persist message history to database
- [ ] Learning cycle config UI
- [ ] Model Card performance charts
- [ ] Multi-model ensemble agents
- [ ] Reinforcement learning for action selection
- [ ] Human-in-the-loop approval workflow
- [ ] Distributed agent deployment

## 💡 Tips & Best Practices

### 1. Chạy workflow định kỳ
```
Mỗi ngày: Run Full Agentic Workflow
→ Kiểm tra violations
→ Review model cards
```

### 2. Monitor learning cycles
```
Weekly: Check learning status
→ Xem recent improvements
→ Identify models cần attention
```

### 3. Active learning workflow
```
1. Run analysis → identify uncertain samples
2. Export samples → manual labeling
3. Upload labeled data → auto-retrain
4. Review new model card
```

### 4. Customize goals/thresholds
```
Quarterly: Review và adjust KPI thresholds
→ Phù hợp với business requirements
```

## ❓ FAQs

**Q: Có cần retrain lại models không?**
A: Không cần. Models cũ vẫn dùng được. System sẽ tự tạo model cards cho lần train tiếp theo.

**Q: Message Bus có tốn performance không?**
A: Không đáng kể. Message Bus in-memory, rất nhanh.

**Q: Learning cycle 24h có thể thay đổi không?**
A: Có, xem phần Configuration ở trên.

**Q: Model Cards lưu ở đâu?**
A: `models/cards/*.json`

**Q: Có thể tắt auto-retraining không?**
A: Có. Đừng click "Trigger Continuous Improvement". System chỉ detect và suggest, không tự động train.

**Q: Agents có cần internet không?**
A: Không. Toàn bộ chạy local.

## 🙏 Feedback

Nếu bạn gặp issues hoặc có suggestions:
1. Tạo issue trên GitHub
2. Hoặc liên hệ team

---

**Version:** 2.0.0
**Release Date:** 2025-10-25
**Upgrade Path:** Seamless (no migration needed)

**Enjoy the new Agentic AI capabilities! 🚀**