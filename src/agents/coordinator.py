from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime
from src.agents.message_bus import MessageBus, Message, MessageType, MessagePriority
from src.agents.model_card_agent import ModelCardAgent
from src.agents.learning_agent import ContinuousLearningAgent
from src.agents.goal_manager import GoalManager
from src.agents.monitor import Monitor
from src.agents.planner import Planner
from src.agents.executor import Executor
from src.agents.memory import Memory
from src.utils.logger import default_logger as logger

class MultiAgentCoordinator:
    def __init__(self):
        self.message_bus = MessageBus()
        self.agent_id = "Coordinator"

        self.model_card_agent = ModelCardAgent()
        self.learning_agent = ContinuousLearningAgent()
        self.goal_manager = GoalManager()
        self.monitor = Monitor()
        self.planner = Planner()
        self.executor = Executor()
        self.memory = Memory()

        self.agents = {
            "ModelCardAgent": self.model_card_agent,
            "LearningAgent": self.learning_agent,
            "GoalManager": self.goal_manager,
            "Monitor": self.monitor,
            "Planner": self.planner,
            "Executor": self.executor,
            "Memory": self.memory
        }

        self.active = True
        self.coordination_history: List[Dict[str, Any]] = []

        self._subscribe_to_events()
        logger.info("MultiAgentCoordinator initialized with 7 agents")

    def _subscribe_to_events(self):
        self.message_bus.subscribe("coordinator.analyze", self.handle_analyze_request)
        self.message_bus.subscribe("coordinator.train", self.handle_train_request)
        self.message_bus.subscribe("coordinator.status", self.handle_status_request)
        self.message_bus.subscribe("model.degradation_detected", self.handle_degradation_coordination)
        self.message_bus.subscribe("learning.cycle_completed", self.handle_learning_cycle_completed)

    def handle_analyze_request(self, message: Message):
        logger.info("Coordinator received analyze request")

        self.coordination_history.append({
            "action": "analyze",
            "timestamp": datetime.now().isoformat(),
            "status": "started"
        })

    def handle_train_request(self, message: Message):
        logger.info("Coordinator received train request")
        payload = message.payload

        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="training.request",
            payload=payload,
            priority=MessagePriority.HIGH
        ))

    def handle_status_request(self, message: Message):
        status = self.get_system_status()
        self.message_bus.respond(message, {"status": status})

    def handle_degradation_coordination(self, message: Message):
        payload = message.payload
        model_id = payload.get('model_id')
        severity = payload.get('severity')

        logger.warning(f"Coordinating response to degradation: {model_id}, severity: {severity}")

        self.message_bus.publish(Message(
            type=MessageType.COMMAND,
            sender=self.agent_id,
            recipient="Planner",
            topic="plan.create",
            payload={"trigger": "degradation", "model_id": model_id, "severity": severity},
            priority=MessagePriority.HIGH
        ))

        self.coordination_history.append({
            "action": "handle_degradation",
            "model_id": model_id,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })

    def handle_learning_cycle_completed(self, message: Message):
        payload = message.payload
        logger.info("Learning cycle completed, updating coordination state")

        self.coordination_history.append({
            "action": "learning_cycle",
            "timestamp": datetime.now().isoformat(),
            "results": payload
        })

    def run_full_agentic_workflow(self, df: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Starting full agentic workflow")

        workflow_results = {
            "timestamp": datetime.now().isoformat(),
            "steps": []
        }

        try:
            baseline_metrics = {
                "total_comments": len(df),
                "timestamp": datetime.now().isoformat()
            }
            self.monitor.store_baseline(baseline_metrics)
            workflow_results['steps'].append({"step": "baseline_stored", "status": "success"})

            goals_set = self.goal_manager.get_all_goals()
            workflow_results['steps'].append({
                "step": "goals_checked",
                "status": "success",
                "goals_count": len(goals_set)
            })

            violations = self.goal_manager.check_violations(baseline_metrics)
            workflow_results['steps'].append({
                "step": "violations_checked",
                "status": "success",
                "violations_count": len(violations)
            })

            if violations:
                actions = self.planner.plan_from_violations(violations)
                workflow_results['steps'].append({
                    "step": "actions_planned",
                    "status": "success",
                    "actions_count": len(actions)
                })

                execution_summary = self.executor.execute_batch(actions, dry_run=False)
                workflow_results['steps'].append({
                    "step": "actions_executed",
                    "status": "success",
                    "summary": execution_summary
                })

            learning_status = self.learning_agent.get_learning_status()
            if learning_status.get('next_cycle_in') == 'due_now':
                learning_results = self.learning_agent.check_and_trigger_learning_cycle(df)
                workflow_results['steps'].append({
                    "step": "learning_cycle",
                    "status": "success",
                    "results": learning_results
                })

            model_cards = self.model_card_agent.get_performance_summary()
            workflow_results['steps'].append({
                "step": "model_cards_reviewed",
                "status": "success",
                "summary": model_cards
            })

            workflow_results['status'] = "completed"
            logger.info("Full agentic workflow completed successfully")

        except Exception as e:
            logger.error(f"Workflow error: {e}")
            workflow_results['status'] = "failed"
            workflow_results['error'] = str(e)

        self.coordination_history.append({
            "action": "full_workflow",
            "timestamp": datetime.now().isoformat(),
            "results": workflow_results
        })

        return workflow_results

    def trigger_continuous_improvement(self, df: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Triggering continuous improvement cycle")

        results = {
            "timestamp": datetime.now().isoformat(),
            "improvements": []
        }

        learning_cycle = self.learning_agent.force_learning_cycle(df)
        results['improvements'].append({
            "type": "learning_cycle",
            "results": learning_cycle
        })

        improvement_summary = self.learning_agent.get_improvement_summary()
        results['improvements'].append({
            "type": "improvement_summary",
            "data": improvement_summary
        })

        self.message_bus.publish(Message(
            type=MessageType.EVENT,
            sender=self.agent_id,
            topic="coordinator.improvement_triggered",
            payload=results
        ))

        return results

    def get_system_status(self) -> Dict[str, Any]:
        status = {
            "coordinator": {
                "active": self.active,
                "agents_count": len(self.agents),
                "coordination_history_size": len(self.coordination_history)
            },
            "agents": {}
        }

        status['agents']['model_cards'] = self.model_card_agent.get_performance_summary()
        status['agents']['learning'] = self.learning_agent.get_learning_status()
        status['agents']['goals'] = {
            "total_goals": len(self.goal_manager.get_all_goals())
        }
        status['agents']['memory'] = {
            "total_actions": len(self.memory.get_all_actions())
        }

        message_history = self.message_bus.get_history(limit=50)
        status['message_bus'] = {
            "recent_messages": len(message_history),
            "topics": list(set(msg.topic for msg in message_history))
        }

        return status

    def get_agent_communications(self, limit: int = 20) -> List[Dict[str, Any]]:
        messages = self.message_bus.get_history(limit=limit)

        return [
            {
                "id": msg.id,
                "type": msg.type.value,
                "sender": msg.sender,
                "recipient": msg.recipient,
                "topic": msg.topic,
                "timestamp": msg.timestamp.isoformat(),
                "priority": msg.priority.value
            }
            for msg in messages
        ]

    def get_coordination_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.coordination_history[-limit:]

    def shutdown(self):
        logger.info("Shutting down MultiAgentCoordinator")
        self.active = False
        self.message_bus.clear_history()
