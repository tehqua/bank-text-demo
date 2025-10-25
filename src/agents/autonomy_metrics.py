from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from src.utils.logger import default_logger as logger

@dataclass
class AutonomyScore:
    overall_score: float
    decision_autonomy: float
    action_autonomy: float
    learning_autonomy: float
    coordination_autonomy: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_score": self.overall_score,
            "decision_autonomy": self.decision_autonomy,
            "action_autonomy": self.action_autonomy,
            "learning_autonomy": self.learning_autonomy,
            "coordination_autonomy": self.coordination_autonomy,
            "timestamp": self.timestamp
        }

class AutonomyMetrics:
    def __init__(self):
        self.decision_log: List[Dict[str, Any]] = []
        self.action_log: List[Dict[str, Any]] = []
        self.intervention_log: List[Dict[str, Any]] = []
        self.learning_events: List[Dict[str, Any]] = []
        self.coordination_events: List[Dict[str, Any]] = []

    def record_decision(self, agent_id: str, decision_type: str,
                       autonomous: bool, context: Dict[str, Any]):
        self.decision_log.append({
            "agent_id": agent_id,
            "decision_type": decision_type,
            "autonomous": autonomous,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def record_action(self, agent_id: str, action_type: str,
                     initiated_by: str, success: bool):
        self.action_log.append({
            "agent_id": agent_id,
            "action_type": action_type,
            "initiated_by": initiated_by,
            "autonomous": initiated_by == agent_id,
            "success": success,
            "timestamp": datetime.now().isoformat()
        })

    def record_intervention(self, agent_id: str, intervention_type: str,
                           reason: str, by_whom: str = "human"):
        self.intervention_log.append({
            "agent_id": agent_id,
            "intervention_type": intervention_type,
            "reason": reason,
            "by_whom": by_whom,
            "timestamp": datetime.now().isoformat()
        })

    def record_learning_event(self, agent_id: str, event_type: str,
                              trigger: str, outcome: Dict[str, Any]):
        self.learning_events.append({
            "agent_id": agent_id,
            "event_type": event_type,
            "trigger": trigger,
            "autonomous": trigger in ["auto_degradation", "auto_cycle", "self_initiated"],
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        })

    def record_coordination(self, initiator: str, participants: List[str],
                           coordination_type: str, outcome: str):
        self.coordination_events.append({
            "initiator": initiator,
            "participants": participants,
            "coordination_type": coordination_type,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_decision_autonomy(self, window_hours: int = 24) -> float:
        cutoff = (datetime.now() - timedelta(hours=window_hours)).isoformat()

        recent_decisions = [
            d for d in self.decision_log
            if d['timestamp'] >= cutoff
        ]

        if not recent_decisions:
            return 0.5

        autonomous_count = sum(1 for d in recent_decisions if d['autonomous'])

        return autonomous_count / len(recent_decisions)

    def calculate_action_autonomy(self, window_hours: int = 24) -> float:
        cutoff = (datetime.now() - timedelta(hours=window_hours)).isoformat()

        recent_actions = [
            a for a in self.action_log
            if a['timestamp'] >= cutoff
        ]

        if not recent_actions:
            return 0.5

        autonomous_count = sum(1 for a in recent_actions if a['autonomous'])

        return autonomous_count / len(recent_actions)

    def calculate_learning_autonomy(self, window_hours: int = 24) -> float:
        cutoff = (datetime.now() - timedelta(hours=window_hours)).isoformat()

        recent_learning = [
            e for e in self.learning_events
            if e['timestamp'] >= cutoff
        ]

        if not recent_learning:
            return 0.5

        autonomous_count = sum(1 for e in recent_learning if e['autonomous'])

        return autonomous_count / len(recent_learning)

    def calculate_coordination_autonomy(self, window_hours: int = 24) -> float:
        cutoff = (datetime.now() - timedelta(hours=window_hours)).isoformat()

        recent_coordination = [
            c for c in self.coordination_events
            if c['timestamp'] >= cutoff
        ]

        if not recent_coordination:
            return 0.5

        successful_coordination = sum(
            1 for c in recent_coordination
            if c['outcome'] in ["success", "completed", "agreement_reached"]
        )

        return successful_coordination / len(recent_coordination)

    def calculate_intervention_rate(self, window_hours: int = 24) -> float:
        cutoff = (datetime.now() - timedelta(hours=window_hours)).isoformat()

        recent_interventions = [
            i for i in self.intervention_log
            if i['timestamp'] >= cutoff
        ]

        total_actions = len([
            a for a in self.action_log
            if a['timestamp'] >= cutoff
        ])

        if total_actions == 0:
            return 0.0

        return len(recent_interventions) / total_actions

    def calculate_autonomy_score(self, weights: Dict[str, float] = None) -> AutonomyScore:
        if weights is None:
            weights = {
                "decision": 0.3,
                "action": 0.3,
                "learning": 0.2,
                "coordination": 0.2
            }

        decision_autonomy = self.calculate_decision_autonomy()
        action_autonomy = self.calculate_action_autonomy()
        learning_autonomy = self.calculate_learning_autonomy()
        coordination_autonomy = self.calculate_coordination_autonomy()

        intervention_penalty = self.calculate_intervention_rate() * 0.2

        overall_score = (
            decision_autonomy * weights["decision"] +
            action_autonomy * weights["action"] +
            learning_autonomy * weights["learning"] +
            coordination_autonomy * weights["coordination"] -
            intervention_penalty
        )

        overall_score = max(0.0, min(1.0, overall_score))

        return AutonomyScore(
            overall_score=overall_score,
            decision_autonomy=decision_autonomy,
            action_autonomy=action_autonomy,
            learning_autonomy=learning_autonomy,
            coordination_autonomy=coordination_autonomy
        )

    def get_agent_autonomy_breakdown(self, agent_id: str) -> Dict[str, Any]:
        agent_decisions = [d for d in self.decision_log if d['agent_id'] == agent_id]
        agent_actions = [a for a in self.action_log if a['agent_id'] == agent_id]
        agent_interventions = [i for i in self.intervention_log if i['agent_id'] == agent_id]

        autonomous_decisions = sum(1 for d in agent_decisions if d['autonomous'])
        autonomous_actions = sum(1 for a in agent_actions if a['autonomous'])

        return {
            "agent_id": agent_id,
            "total_decisions": len(agent_decisions),
            "autonomous_decisions": autonomous_decisions,
            "decision_autonomy_rate": autonomous_decisions / len(agent_decisions) if agent_decisions else 0,
            "total_actions": len(agent_actions),
            "autonomous_actions": autonomous_actions,
            "action_autonomy_rate": autonomous_actions / len(agent_actions) if agent_actions else 0,
            "interventions": len(agent_interventions)
        }

    def get_autonomy_trend(self, window_hours: int = 168, interval_hours: int = 24) -> List[Dict[str, Any]]:
        now = datetime.now()
        trend = []

        for hours_back in range(window_hours, 0, -interval_hours):
            end_time = now - timedelta(hours=hours_back)
            start_time = end_time - timedelta(hours=interval_hours)

            period_decisions = [
                d for d in self.decision_log
                if start_time.isoformat() <= d['timestamp'] < end_time.isoformat()
            ]

            period_actions = [
                a for a in self.action_log
                if start_time.isoformat() <= a['timestamp'] < end_time.isoformat()
            ]

            if period_decisions or period_actions:
                autonomous_decisions = sum(1 for d in period_decisions if d['autonomous'])
                autonomous_actions = sum(1 for a in period_actions if a['autonomous'])

                decision_rate = autonomous_decisions / len(period_decisions) if period_decisions else 0
                action_rate = autonomous_actions / len(period_actions) if period_actions else 0

                trend.append({
                    "timestamp": end_time.isoformat(),
                    "decision_autonomy": decision_rate,
                    "action_autonomy": action_rate,
                    "average_autonomy": (decision_rate + action_rate) / 2
                })

        return trend

class RobustnessMetrics:
    def __init__(self):
        self.failure_events: List[Dict[str, Any]] = []
        self.recovery_events: List[Dict[str, Any]] = []

    def record_failure(self, component: str, failure_type: str, severity: str):
        self.failure_events.append({
            "component": component,
            "failure_type": failure_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })

    def record_recovery(self, component: str, recovery_time: float, successful: bool):
        self.recovery_events.append({
            "component": component,
            "recovery_time": recovery_time,
            "successful": successful,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_mtbf(self) -> float:
        if len(self.failure_events) < 2:
            return float('inf')

        failure_times = [
            datetime.fromisoformat(f['timestamp'])
            for f in self.failure_events
        ]

        intervals = [
            (failure_times[i+1] - failure_times[i]).total_seconds() / 3600
            for i in range(len(failure_times) - 1)
        ]

        return np.mean(intervals) if intervals else float('inf')

    def calculate_mttr(self) -> float:
        if not self.recovery_events:
            return 0.0

        recovery_times = [r['recovery_time'] for r in self.recovery_events]

        return np.mean(recovery_times)

    def calculate_availability(self, total_time_hours: float = 720) -> float:
        total_downtime = sum(r['recovery_time'] for r in self.recovery_events if not r['successful'])

        uptime = total_time_hours - total_downtime

        return uptime / total_time_hours if total_time_hours > 0 else 1.0

    def get_robustness_report(self) -> Dict[str, Any]:
        return {
            "mtbf_hours": self.calculate_mtbf(),
            "mttr_hours": self.calculate_mttr(),
            "availability": self.calculate_availability(),
            "total_failures": len(self.failure_events),
            "total_recoveries": len(self.recovery_events),
            "recovery_success_rate": sum(1 for r in self.recovery_events if r['successful']) / len(self.recovery_events) if self.recovery_events else 0
        }

class AlignmentMetrics:
    def __init__(self, global_goals: Dict[str, float]):
        self.global_goals = global_goals
        self.goal_achievements: List[Dict[str, Any]] = []
        self.deviations: List[Dict[str, Any]] = []

    def record_goal_achievement(self, goal_name: str, target: float, actual: float):
        achievement_rate = actual / target if target > 0 else 0

        self.goal_achievements.append({
            "goal_name": goal_name,
            "target": target,
            "actual": actual,
            "achievement_rate": achievement_rate,
            "timestamp": datetime.now().isoformat()
        })

    def record_deviation(self, action_type: str, expected_outcome: Any,
                        actual_outcome: Any, severity: str):
        self.deviations.append({
            "action_type": action_type,
            "expected": expected_outcome,
            "actual": actual_outcome,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })

    def calculate_goal_alignment(self) -> float:
        if not self.goal_achievements:
            return 0.5

        recent_achievements = self.goal_achievements[-20:]

        avg_achievement = np.mean([
            a['achievement_rate']
            for a in recent_achievements
        ])

        return min(1.0, avg_achievement)

    def calculate_deviation_rate(self) -> float:
        total_actions = len(self.goal_achievements) + len(self.deviations)

        if total_actions == 0:
            return 0.0

        return len(self.deviations) / total_actions

    def get_alignment_report(self) -> Dict[str, Any]:
        return {
            "goal_alignment_score": self.calculate_goal_alignment(),
            "deviation_rate": self.calculate_deviation_rate(),
            "total_goal_achievements": len(self.goal_achievements),
            "total_deviations": len(self.deviations),
            "recent_goals": self.goal_achievements[-5:]
        }
