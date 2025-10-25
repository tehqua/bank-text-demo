from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

@dataclass
class ActionCost:
    computational_cost: float = 0.0
    time_cost: float = 0.0
    resource_cost: float = 0.0
    risk_score: float = 0.0

    def total_cost(self, weights: Dict[str, float] = None) -> float:
        if weights is None:
            weights = {
                "computational": 0.25,
                "time": 0.35,
                "resource": 0.25,
                "risk": 0.15
            }

        return (
            self.computational_cost * weights.get("computational", 0.25) +
            self.time_cost * weights.get("time", 0.35) +
            self.resource_cost * weights.get("resource", 0.25) +
            self.risk_score * weights.get("risk", 0.15)
        )

@dataclass
class ActionBenefit:
    accuracy_improvement: float = 0.0
    user_satisfaction: float = 0.0
    business_value: float = 0.0
    strategic_alignment: float = 0.0

    def total_benefit(self, weights: Dict[str, float] = None) -> float:
        if weights is None:
            weights = {
                "accuracy": 0.4,
                "satisfaction": 0.3,
                "value": 0.2,
                "strategic": 0.1
            }

        return (
            self.accuracy_improvement * weights.get("accuracy", 0.4) +
            self.user_satisfaction * weights.get("satisfaction", 0.3) +
            self.business_value * weights.get("value", 0.2) +
            self.strategic_alignment * weights.get("strategic", 0.1)
        )

@dataclass
class AgentCapability:
    agent_id: str
    task_type: str
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    resource_availability: float = 1.0
    expertise_score: float = 0.5
    current_load: int = 0
    max_load: int = 10

    def can_accept_task(self) -> bool:
        return self.current_load < self.max_load and self.resource_availability > 0.2

    def utility_for_task(self, task_requirements: Dict[str, float]) -> float:
        quality_match = self.expertise_score
        load_penalty = self.current_load / self.max_load
        reliability = self.success_rate
        availability = self.resource_availability

        utility = (
            quality_match * 0.4 +
            reliability * 0.3 +
            availability * 0.2 -
            load_penalty * 0.1
        )

        return max(0.0, min(1.0, utility))

class UtilityFunction:
    def __init__(self, global_goals: Dict[str, float] = None):
        self.global_goals = global_goals or {
            "minimize_cost": 0.3,
            "maximize_accuracy": 0.4,
            "minimize_time": 0.2,
            "maximize_reliability": 0.1
        }

    def evaluate_action(self, action: Dict[str, Any], cost: ActionCost,
                       benefit: ActionBenefit) -> float:
        total_cost = cost.total_cost()
        total_benefit = benefit.total_benefit()

        utility = total_benefit - total_cost

        goal_alignment = 0.0
        if "accuracy_impact" in action:
            goal_alignment += action["accuracy_impact"] * self.global_goals.get("maximize_accuracy", 0)

        if "time_required" in action:
            time_penalty = action["time_required"] / 3600.0
            goal_alignment -= time_penalty * self.global_goals.get("minimize_time", 0)

        return utility + goal_alignment

    def rank_actions(self, actions: List[Dict[str, Any]],
                    costs: List[ActionCost],
                    benefits: List[ActionBenefit]) -> List[tuple]:
        utilities = []

        for action, cost, benefit in zip(actions, costs, benefits):
            utility = self.evaluate_action(action, cost, benefit)
            utilities.append((action, utility))

        return sorted(utilities, key=lambda x: x[1], reverse=True)

class TaskAllocator:
    def __init__(self):
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.utility_function = UtilityFunction()

    def register_agent(self, agent_id: str, task_types: List[str],
                      success_rate: float = 0.8, expertise: float = 0.5):
        for task_type in task_types:
            self.agent_capabilities[f"{agent_id}:{task_type}"] = AgentCapability(
                agent_id=agent_id,
                task_type=task_type,
                success_rate=success_rate,
                expertise_score=expertise
            )

    def allocate_task(self, task: Dict[str, Any]) -> Optional[str]:
        task_type = task.get("type", "unknown")
        requirements = task.get("requirements", {})

        candidates = []

        for key, capability in self.agent_capabilities.items():
            if capability.task_type == task_type and capability.can_accept_task():
                utility = capability.utility_for_task(requirements)
                candidates.append((capability.agent_id, utility, capability))

        if not candidates:
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)

        selected_agent = candidates[0][0]
        selected_capability = candidates[0][2]

        selected_capability.current_load += 1

        return selected_agent

    def release_task(self, agent_id: str, task_type: str):
        key = f"{agent_id}:{task_type}"
        if key in self.agent_capabilities:
            self.agent_capabilities[key].current_load = max(
                0, self.agent_capabilities[key].current_load - 1
            )

    def update_agent_stats(self, agent_id: str, task_type: str,
                          success: bool, execution_time: float):
        key = f"{agent_id}:{task_type}"
        if key not in self.agent_capabilities:
            return

        capability = self.agent_capabilities[key]

        alpha = 0.1
        capability.success_rate = (
            alpha * (1.0 if success else 0.0) +
            (1 - alpha) * capability.success_rate
        )

        capability.avg_execution_time = (
            alpha * execution_time +
            (1 - alpha) * capability.avg_execution_time
        )

    def get_load_balance_report(self) -> Dict[str, Any]:
        agent_loads = {}
        for key, capability in self.agent_capabilities.items():
            agent_id = capability.agent_id
            if agent_id not in agent_loads:
                agent_loads[agent_id] = {
                    "total_load": 0,
                    "tasks": []
                }

            agent_loads[agent_id]["total_load"] += capability.current_load
            agent_loads[agent_id]["tasks"].append({
                "task_type": capability.task_type,
                "load": capability.current_load,
                "success_rate": capability.success_rate
            })

        return agent_loads

class ConflictResolver:
    def __init__(self):
        self.conflict_history: List[Dict[str, Any]] = []

    def detect_conflict(self, actions: List[Dict[str, Any]]) -> List[tuple]:
        conflicts = []

        for i, action1 in enumerate(actions):
            for j, action2 in enumerate(actions[i+1:], start=i+1):
                if self._actions_conflict(action1, action2):
                    conflicts.append((action1, action2))

        return conflicts

    def _actions_conflict(self, action1: Dict[str, Any], action2: Dict[str, Any]) -> bool:
        if action1.get("resource") and action2.get("resource"):
            if action1["resource"] == action2["resource"]:
                return True

        if action1.get("target_model") and action2.get("target_model"):
            if action1["target_model"] == action2["target_model"]:
                if action1["type"] == "retrain" and action2["type"] == "retrain":
                    return True

        return False

    def resolve_conflict(self, action1: Dict[str, Any], action2: Dict[str, Any],
                        costs: tuple, benefits: tuple) -> Dict[str, Any]:
        utility_func = UtilityFunction()

        utility1 = utility_func.evaluate_action(action1, costs[0], benefits[0])
        utility2 = utility_func.evaluate_action(action2, costs[1], benefits[1])

        conflict_record = {
            "timestamp": datetime.now().isoformat(),
            "action1": action1,
            "action2": action2,
            "utility1": utility1,
            "utility2": utility2,
            "selected": "action1" if utility1 >= utility2 else "action2"
        }

        self.conflict_history.append(conflict_record)

        return action1 if utility1 >= utility2 else action2

    def resolve_multiple_conflicts(self, actions: List[Dict[str, Any]],
                                   costs: List[ActionCost],
                                   benefits: List[ActionBenefit]) -> List[Dict[str, Any]]:
        utility_func = UtilityFunction()
        ranked = utility_func.rank_actions(actions, costs, benefits)

        resolved_actions = []
        used_resources = set()

        for action, utility in ranked:
            resource = action.get("resource")
            target = action.get("target_model")

            conflict = False
            if resource and resource in used_resources:
                conflict = True

            if target and target in used_resources:
                conflict = True

            if not conflict:
                resolved_actions.append(action)
                if resource:
                    used_resources.add(resource)
                if target:
                    used_resources.add(target)

        return resolved_actions

    def get_conflict_statistics(self) -> Dict[str, Any]:
        if not self.conflict_history:
            return {
                "total_conflicts": 0,
                "resolution_rate": 0.0
            }

        return {
            "total_conflicts": len(self.conflict_history),
            "recent_conflicts": self.conflict_history[-10:],
            "resolution_rate": 1.0
        }
