# Agentic AI Architecture Guide

## Overview

This document describes the **True Agentic AI** architecture implemented in the Bank Text Analysis system. Unlike traditional workflow-based systems, this architecture features autonomous agents that communicate through protocols, make independent decisions, and continuously improve models.

## Architecture Principles

### 1. Agent Autonomy
- Each agent has specific responsibilities and can act independently
- Agents make decisions based on their observations and goals
- No centralized control - agents coordinate through message passing

### 2. Inter-Agent Communication
- Agents communicate via a **Message Bus** (publish-subscribe pattern)
- Supports Request/Response, Event, and Command message types
- Priority-based message queue for critical actions

### 3. Continuous Learning
- Models automatically detect performance degradation
- Active learning identifies uncertain predictions for labeling
- Auto-training triggers when sufficient labeled data is available

### 4. Model Cards & Metadata
- Each model has a dedicated Model Card with full lineage
- Performance history tracking
- Automatic degradation detection

## System Components

### Core Infrastructure

#### Message Bus (`src/agents/message_bus.py`)

**Purpose:** Event-driven communication backbone for all agents

**Features:**
- Pub/Sub pattern for loose coupling
- Priority queue (LOW, MEDIUM, HIGH, CRITICAL)
- Request/Response pattern with timeout
- Message history and auditing

**Message Types:**
- `REQUEST`: Synchronous request expecting response
- `RESPONSE`: Reply to a request
- `EVENT`: Asynchronous notification
- `COMMAND`: Direct instruction to specific agent

**Example Usage:**
```python
from agents.message_bus import MessageBus, Message, MessageType, MessagePriority

bus = MessageBus()

# Subscribe to events
bus.subscribe("model.trained", my_callback)

# Publish event
bus.publish(Message(
    type=MessageType.EVENT,
    sender="TrainerAgent",
    topic="model.trained",
    payload={"model_id": "sentiment_20250101", "accuracy": 0.92},
    priority=MessagePriority.HIGH
))

# Request/Response
response = bus.request(
    sender="CoordinatorAgent",
    recipient="ModelCardAgent",
    topic="model.get_card",
    payload={"model_id": "sentiment_20250101"}
)
```

### Agents

#### 1. Model Card Agent (`src/agents/model_card_agent.py`)

**Responsibility:** Manage model metadata and performance tracking

**Key Features:**
- Creates model cards on training completion
- Tracks performance history over time
- Detects performance degradation (>10% drop)
- Publishes degradation events automatically

**Model Card Structure:**
```python
{
    "model_id": "sentiment_model_20250101_123456",
    "model_name": "sentiment_model",
    "model_type": "sentiment",
    "version": "1.0.0",
    "created_at": "2025-01-01T12:34:56",
    "metrics": {
        "accuracy": 0.92,
        "precision": 0.90,
        "recall": 0.88,
        "f1_score": 0.89
    },
    "training_data_size": 1000,
    "hyperparameters": {...},
    "performance_history": [...],
    "drift_score": 0.0,
    "retraining_count": 0
}
```

**Events Published:**
- `model.card_created`: New model card created
- `model.degradation_detected`: Performance drop detected

**Events Subscribed:**
- `model.trained`: Create new card
- `model.evaluated`: Update metrics
- `model.get_card`: Respond with card data

#### 2. Continuous Learning Agent (`src/agents/learning_agent.py`)

**Responsibility:** Orchestrate continuous model improvement

**Key Features:**
- Periodic learning cycles (default: 24 hours)
- Integrates Active Learning and Auto Training
- Tracks improvement over time
- Triggers retraining when needed

**Learning Cycle Process:**
1. Check if learning cycle is due
2. Process training queue (if any)
3. Identify uncertain predictions for labeling
4. Update performance baselines
5. Publish learning cycle results

**Events Published:**
- `learning.cycle_started`: Learning cycle initiated
- `learning.cycle_completed`: Cycle finished with results
- `learning.improvement_detected`: Model improved
- `learning.uncertain_samples_found`: Samples need labeling

**Events Subscribed:**
- `data.analyzed`: Check for learning opportunities
- `model.degradation_detected`: Trigger immediate cycle
- `learning.trigger_cycle`: Manual trigger

#### 3. Auto Trainer (`src/models/auto_trainer.py`)

**Responsibility:** Autonomous model retraining

**Key Features:**
- Training queue with prioritization
- Automatic retraining on degradation
- Minimum sample validation
- MLflow integration (optional)

**Training Triggers:**
1. Performance degradation detected
2. New labeled data available (>= min_samples)
3. Manual training request

**Events Published:**
- `training.queued`: Training task added to queue
- `model.trained`: Training completed successfully
- `training.failed`: Training error occurred

**Events Subscribed:**
- `model.degradation_detected`: Add to training queue
- `data.new_labeled`: Check if enough data to train
- `training.request`: Manual training

#### 4. Goal Manager (`src/agents/goal_manager.py`)

**Responsibility:** Define and monitor KPI goals

**Default Goals:**
```python
{
    "sentiment_accuracy": {
        "metric": "sentiment_accuracy",
        "threshold": 0.7,
        "operator": ">=",
        "priority": "high",
        "action": "retrain_sentiment"
    },
    "negative_spike": {
        "metric": "negative_ratio_delta",
        "threshold": 0.1,
        "operator": ">",
        "priority": "critical",
        "action": "alert_ops"
    },
    "topic_drift": {
        "metric": "topic_drift_score",
        "threshold": 0.3,
        "operator": ">",
        "priority": "medium",
        "action": "retrain_topic"
    }
}
```

**Events Published:**
- `goals.violations_detected`: KPI violations found

**Events Subscribed:**
- `goals.check`: Evaluate goals against metrics
- `goals.update`: Update goal definitions

#### 5. Monitor Agent (`src/agents/monitor.py`)

**Responsibility:** Anomaly detection and drift monitoring

**Detection Methods:**
- Sentiment distribution drift (KL divergence)
- Topic distribution drift
- Negative sentiment spike detection

**Events Published:**
- `monitor.anomalies_detected`: Anomalies found
- `monitor.baseline_updated`: Baseline metrics saved

**Events Subscribed:**
- `monitor.check_anomalies`: Run anomaly detection
- `monitor.save_baseline`: Update baseline

#### 6. Planner Agent (`src/agents/planner.py`)

**Responsibility:** Create action plans from violations/anomalies

**Plan Structure:**
```python
{
    "plan_id": "plan_20250101_123456",
    "timestamp": "2025-01-01T12:34:56",
    "actions": [
        {
            "type": "retrain_sentiment",
            "priority": "high",
            "description": "Retrain sentiment model",
            "params": {...}
        }
    ]
}
```

#### 7. Executor Agent (`src/agents/executor.py`)

**Responsibility:** Execute planned actions

**Action Types:**
- `retrain_sentiment`: Trigger sentiment model retraining
- `retrain_topic`: Trigger topic model retraining
- `alert_ops`: Send alerts (email/slack/jira)
- `collect_feedback`: Initiate data labeling

#### 8. Multi-Agent Coordinator (`src/agents/coordinator.py`)

**Responsibility:** High-level orchestration of all agents

**Key Methods:**

**`run_full_agentic_workflow(df)`**
- Store baseline metrics
- Check goals and violations
- Detect anomalies
- Plan and execute actions
- Run learning cycle if due
- Review model cards

**`trigger_continuous_improvement(df)`**
- Force immediate learning cycle
- Get improvement summary
- Publish improvement events

**`get_system_status()`**
- Agent health checks
- Model card summary
- Learning status
- Message bus statistics

## Active Learning Module

### Purpose
Identify uncertain predictions that need human labeling

### Strategies

**1. Confidence-based Sampling**
```python
uncertainty_score = 1.0 - max_probability
# Select samples with high uncertainty (low confidence)
```

**2. Margin Sampling**
```python
margin = prob_top1 - prob_top2
# Select samples with small margin between top 2 classes
```

**3. Entropy Sampling**
```python
entropy = -sum(p * log(p) for p in probabilities)
# Select samples with high prediction entropy
```

### Usage Example
```python
from models.active_learner import ActiveLearner

learner = ActiveLearner(uncertainty_threshold=0.3)

# Identify uncertain samples
uncertain = learner.identify_uncertain_samples(
    texts=comments,
    predictions=pred_labels,
    probabilities=pred_probs,
    top_k=20
)

# Get samples for labeling
samples = learner.get_samples_for_labeling()

# After labeling, update
learner.update_with_labels([(idx, "Positive"), (idx2, "Negative")])
```

## Communication Flow Examples

### Example 1: Performance Degradation Triggered Retraining

```
1. ModelCardAgent detects accuracy drop from 0.92 to 0.80
   → Publishes: model.degradation_detected

2. AutoTrainer receives event
   → Adds task to training queue
   → Publishes: training.queued

3. LearningAgent receives degradation event
   → Triggers immediate learning cycle
   → Publishes: learning.cycle_started

4. Coordinator receives cycle_started
   → Coordinates AutoTrainer to process queue

5. AutoTrainer completes retraining
   → Publishes: model.trained

6. ModelCardAgent receives model.trained
   → Creates new model card
   → Publishes: model.card_created

7. LearningAgent updates baselines
   → Publishes: learning.improvement_detected
```

### Example 2: Scheduled Learning Cycle

```
1. User triggers "Run Full Agentic Workflow"

2. Coordinator.run_full_agentic_workflow(df)

3. Monitor stores baseline
   → Publishes: monitor.baseline_updated

4. GoalManager checks violations
   → Publishes: goals.violations_detected (if any)

5. Planner creates action plan
   → Coordinator executes plan

6. LearningAgent checks if cycle is due
   → Runs learning cycle
   → Processes training queue
   → Identifies uncertain samples
   → Publishes: learning.cycle_completed
```

## Configuration

### Learning Cycle Interval
```python
# Default: 24 hours
coordinator.learning_agent.configure_learning_interval(hours=12)
```

### Active Learning Threshold
```python
# Default: 0.3 (samples with confidence < 0.7 are uncertain)
active_learner = ActiveLearner(uncertainty_threshold=0.2)
```

### Auto Trainer Settings
```python
auto_trainer = AutoTrainer()
auto_trainer.min_samples_for_training = 20
auto_trainer.retrain_threshold_accuracy = 0.75
```

## Usage in Streamlit App

### Initialize Coordinator
```python
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = MultiAgentCoordinator()
```

### Run Autonomous Workflow
```python
coordinator = st.session_state.coordinator
results = coordinator.run_full_agentic_workflow(df)
```

### Trigger Continuous Improvement
```python
results = coordinator.trigger_continuous_improvement(df)
```

### View System Status
```python
status = coordinator.get_system_status()
st.json(status)
```

### View Agent Communications
```python
messages = coordinator.get_agent_communications(limit=20)
for msg in messages:
    st.write(f"{msg['sender']} → {msg['topic']}")
```

## Key Differences from Workflow-Based Systems

| Aspect | Traditional Workflow | True Agentic AI |
|--------|---------------------|-----------------|
| **Control** | Centralized, sequential | Decentralized, autonomous |
| **Communication** | Direct function calls | Message bus (async) |
| **Decision Making** | Pre-defined steps | Agent-based reasoning |
| **Adaptability** | Static workflow | Dynamic agent coordination |
| **Learning** | Manual retraining | Continuous auto-improvement |
| **Monitoring** | External monitoring | Self-monitoring agents |

## Benefits

1. **Scalability**: Add new agents without modifying existing ones
2. **Resilience**: Agents continue working if others fail
3. **Observability**: Message history provides full audit trail
4. **Flexibility**: Easy to change agent behavior independently
5. **Continuous Improvement**: Models improve automatically without human intervention

## Future Enhancements

1. **Multi-Model Ensembles**: Agents coordinate multiple models
2. **Reinforcement Learning**: Agents learn optimal actions from outcomes
3. **Human-in-the-Loop**: Interactive approval for critical actions
4. **Distributed Deployment**: Agents run on separate services
5. **Advanced Active Learning**: Query-by-committee, expected model change

## Troubleshooting

### Issue: Agents not communicating

**Solution:** Check MessageBus initialization
```python
from agents.message_bus import MessageBus
bus = MessageBus()
bus.get_history()  # Check if messages are being published
```

### Issue: Learning cycle not triggering

**Solution:** Check time interval
```python
learning_agent = coordinator.learning_agent
status = learning_agent.get_learning_status()
print(status['next_cycle_in'])
```

### Issue: Training queue not processing

**Solution:** Check queue status
```python
auto_trainer = coordinator.learning_agent.auto_trainer
stats = auto_trainer.get_training_statistics()
print(f"Queue size: {stats['queue_size']}")
```

## References

- Multi-Agent Systems: https://en.wikipedia.org/wiki/Multi-agent_system
- Active Learning: https://en.wikipedia.org/wiki/Active_learning_(machine_learning)
- Model Cards: https://modelcards.withgoogle.com/about

---

**Version:** 2.0
**Last Updated:** 2025-10-25
**Maintainer:** Bank Text Analysis Team
