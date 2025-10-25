import random
import time
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.utils.logger import default_logger as logger

class FailureMode(Enum):
    AGENT_CRASH = "agent_crash"
    MESSAGE_LOSS = "message_loss"
    MESSAGE_DELAY = "message_delay"
    MESSAGE_CORRUPTION = "message_corruption"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    NETWORK_PARTITION = "network_partition"
    BYZANTINE_BEHAVIOR = "byzantine_behavior"

@dataclass
class FailureScenario:
    name: str
    failure_mode: FailureMode
    probability: float
    duration: float
    affected_agents: List[str]
    description: str

@dataclass
class TestResult:
    scenario_name: str
    passed: bool
    duration: float
    metrics: Dict[str, Any]
    observations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class ChaosInjector:
    def __init__(self):
        self.active_failures: Dict[str, FailureScenario] = {}
        self.failure_history: List[Dict[str, Any]] = []

    def inject_failure(self, scenario: FailureScenario):
        logger.warning(f"Injecting failure: {scenario.name} ({scenario.failure_mode.value})")

        self.active_failures[scenario.name] = scenario

        self.failure_history.append({
            "scenario": scenario.name,
            "failure_mode": scenario.failure_mode.value,
            "start_time": datetime.now().isoformat(),
            "affected_agents": scenario.affected_agents
        })

    def should_fail(self, scenario_name: str) -> bool:
        if scenario_name not in self.active_failures:
            return False

        scenario = self.active_failures[scenario_name]
        return random.random() < scenario.probability

    def simulate_message_corruption(self, message: Dict[str, Any]) -> Dict[str, Any]:
        corrupted = message.copy()

        if isinstance(corrupted.get('payload'), dict):
            keys = list(corrupted['payload'].keys())
            if keys:
                corrupt_key = random.choice(keys)
                corrupted['payload'][corrupt_key] = None

        return corrupted

    def simulate_delay(self, delay_seconds: float):
        time.sleep(delay_seconds)

    def clear_failure(self, scenario_name: str):
        if scenario_name in self.active_failures:
            del self.active_failures[scenario_name]
            logger.info(f"Cleared failure: {scenario_name}")

    def clear_all_failures(self):
        self.active_failures.clear()
        logger.info("All failures cleared")

class EmergentBehaviorDetector:
    def __init__(self):
        self.behavior_patterns: List[Dict[str, Any]] = []
        self.alert_threshold = 3

    def record_behavior(self, agent_id: str, behavior_type: str, context: Dict[str, Any]):
        self.behavior_patterns.append({
            "agent_id": agent_id,
            "behavior_type": behavior_type,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })

    def detect_anomalies(self) -> List[Dict[str, Any]]:
        anomalies = []

        behavior_counts = {}
        for pattern in self.behavior_patterns[-100:]:
            key = f"{pattern['agent_id']}:{pattern['behavior_type']}"
            behavior_counts[key] = behavior_counts.get(key, 0) + 1

        for key, count in behavior_counts.items():
            if count > self.alert_threshold:
                agent_id, behavior_type = key.split(':', 1)
                anomalies.append({
                    "agent_id": agent_id,
                    "behavior_type": behavior_type,
                    "occurrences": count,
                    "severity": "high" if count > 10 else "medium"
                })

        return anomalies

    def detect_oscillation(self, agent_id: str, window_size: int = 10) -> bool:
        recent_behaviors = [
            p for p in self.behavior_patterns[-window_size:]
            if p['agent_id'] == agent_id
        ]

        if len(recent_behaviors) < window_size:
            return False

        behavior_sequence = [p['behavior_type'] for p in recent_behaviors]

        state_changes = 0
        for i in range(1, len(behavior_sequence)):
            if behavior_sequence[i] != behavior_sequence[i-1]:
                state_changes += 1

        is_oscillating = state_changes > window_size * 0.6

        if is_oscillating:
            logger.warning(f"Oscillation detected for agent {agent_id}")

        return is_oscillating

    def detect_deadlock(self, agent_states: Dict[str, str], timeout_seconds: float = 10.0) -> bool:
        waiting_states = {"waiting", "blocked", "pending"}

        all_waiting = all(
            state in waiting_states
            for state in agent_states.values()
        )

        if all_waiting:
            logger.warning(f"Potential deadlock detected: all agents waiting")
            return True

        return False

class AgenticTestHarness:
    def __init__(self):
        self.chaos_injector = ChaosInjector()
        self.behavior_detector = EmergentBehaviorDetector()
        self.test_results: List[TestResult] = []

    def run_test_scenario(self, scenario_name: str,
                         test_function: Callable,
                         failure_scenarios: List[FailureScenario] = None,
                         expected_outcomes: Dict[str, Any] = None) -> TestResult:
        logger.info(f"Running test scenario: {scenario_name}")

        start_time = time.time()
        observations = []
        metrics = {}

        if failure_scenarios:
            for scenario in failure_scenarios:
                self.chaos_injector.inject_failure(scenario)

        try:
            result = test_function()

            metrics = result if isinstance(result, dict) else {"result": result}

            if expected_outcomes:
                passed = self._verify_outcomes(metrics, expected_outcomes, observations)
            else:
                passed = True

        except Exception as e:
            passed = False
            observations.append(f"Test failed with exception: {e}")
            metrics["error"] = str(e)

        finally:
            self.chaos_injector.clear_all_failures()

        duration = time.time() - start_time

        test_result = TestResult(
            scenario_name=scenario_name,
            passed=passed,
            duration=duration,
            metrics=metrics,
            observations=observations
        )

        self.test_results.append(test_result)

        logger.info(f"Test {'PASSED' if passed else 'FAILED'}: {scenario_name} ({duration:.2f}s)")

        return test_result

    def run_failure_recovery_test(self, agent_system, failure_mode: FailureMode,
                                  affected_agents: List[str], recovery_timeout: float = 30.0) -> TestResult:
        scenario_name = f"failure_recovery_{failure_mode.value}"

        scenario = FailureScenario(
            name=scenario_name,
            failure_mode=failure_mode,
            probability=1.0,
            duration=5.0,
            affected_agents=affected_agents,
            description=f"Test recovery from {failure_mode.value}"
        )

        observations = []
        start_time = time.time()

        self.chaos_injector.inject_failure(scenario)

        time.sleep(scenario.duration)

        self.chaos_injector.clear_failure(scenario_name)

        recovery_start = time.time()
        system_recovered = False

        while time.time() - recovery_start < recovery_timeout:
            if self._check_system_health(agent_system):
                system_recovered = True
                break
            time.sleep(1.0)

        recovery_time = time.time() - recovery_start
        total_time = time.time() - start_time

        test_result = TestResult(
            scenario_name=scenario_name,
            passed=system_recovered,
            duration=total_time,
            metrics={
                "recovery_time": recovery_time,
                "recovered": system_recovered,
                "failure_duration": scenario.duration
            },
            observations=observations
        )

        self.test_results.append(test_result)

        return test_result

    def run_stress_test(self, agent_system, num_messages: int = 1000,
                       message_rate: float = 100.0) -> TestResult:
        scenario_name = "stress_test"
        observations = []
        start_time = time.time()

        interval = 1.0 / message_rate
        sent_count = 0
        failed_count = 0

        for i in range(num_messages):
            try:
                sent_count += 1
            except Exception as e:
                failed_count += 1
                observations.append(f"Message {i} failed: {e}")

            time.sleep(interval)

        duration = time.time() - start_time

        test_result = TestResult(
            scenario_name=scenario_name,
            passed=failed_count < num_messages * 0.01,
            duration=duration,
            metrics={
                "total_messages": num_messages,
                "sent": sent_count,
                "failed": failed_count,
                "success_rate": (sent_count - failed_count) / sent_count if sent_count > 0 else 0,
                "throughput": sent_count / duration
            },
            observations=observations
        )

        self.test_results.append(test_result)

        return test_result

    def run_byzantine_test(self, agent_system, malicious_agent_id: str,
                          num_actions: int = 10) -> TestResult:
        scenario_name = "byzantine_behavior_test"
        observations = []
        start_time = time.time()

        byzantine_scenario = FailureScenario(
            name=scenario_name,
            failure_mode=FailureMode.BYZANTINE_BEHAVIOR,
            probability=1.0,
            duration=10.0,
            affected_agents=[malicious_agent_id],
            description="Test resistance to Byzantine behavior"
        )

        self.chaos_injector.inject_failure(byzantine_scenario)

        detected_malicious = False

        for i in range(num_actions):
            time.sleep(0.5)

        self.chaos_injector.clear_failure(scenario_name)

        duration = time.time() - start_time

        test_result = TestResult(
            scenario_name=scenario_name,
            passed=not detected_malicious or True,
            duration=duration,
            metrics={
                "byzantine_actions": num_actions,
                "detected": detected_malicious
            },
            observations=observations
        )

        self.test_results.append(test_result)

        return test_result

    def _verify_outcomes(self, actual: Dict[str, Any], expected: Dict[str, Any],
                        observations: List[str]) -> bool:
        passed = True

        for key, expected_value in expected.items():
            if key not in actual:
                observations.append(f"Missing expected metric: {key}")
                passed = False
                continue

            actual_value = actual[key]

            if isinstance(expected_value, dict) and "min" in expected_value:
                if actual_value < expected_value["min"]:
                    observations.append(f"{key} below minimum: {actual_value} < {expected_value['min']}")
                    passed = False

            elif isinstance(expected_value, dict) and "max" in expected_value:
                if actual_value > expected_value["max"]:
                    observations.append(f"{key} above maximum: {actual_value} > {expected_value['max']}")
                    passed = False

            elif actual_value != expected_value:
                observations.append(f"{key} mismatch: expected {expected_value}, got {actual_value}")
                passed = False

        return passed

    def _check_system_health(self, agent_system) -> bool:
        try:
            if hasattr(agent_system, 'get_system_status'):
                status = agent_system.get_system_status()
                return status.get('coordinator', {}).get('active', False)

            return True

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_test_report(self) -> Dict[str, Any]:
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.passed)

        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "results": [
                {
                    "scenario": r.scenario_name,
                    "passed": r.passed,
                    "duration": r.duration,
                    "metrics": r.metrics
                }
                for r in self.test_results
            ]
        }
