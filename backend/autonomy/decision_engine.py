import math
from typing import Dict, Any, Optional
from collections import deque

class DecisionEngine:
    ACTION_CATALOG = {
        "throttle_process":  {"base_cost": 0.2, "base_score": 0.6, "safe": True},
        "kill_process":      {"base_cost": 0.9, "base_score": 0.8, "safe": False},
        "clear_cache":       {"base_cost": 0.1, "base_score": 0.4, "safe": True},
        "rate_limit":        {"base_cost": 0.3, "base_score": 0.5, "safe": True},
        "no_action":         {"base_cost": 0.0, "base_score": 0.3, "safe": True},
        "preemptive_throttle":{"base_cost": 0.2, "base_score": 0.55,"safe": True},
    }

    def __init__(self):
        self.weights = {action: 1.0 for action in self.ACTION_CATALOG}
        self._oscillation_window = deque(maxlen=5)

    def update_weights(self, new_weights: Dict[str, float]):
        self.weights.update(new_weights)

    def decide(
        self, 
        intelligence: Dict[str, Any], 
        matched_pattern: Optional[Dict[str, Any]] = None, 
        preemptive_signal: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        
        threat_score = intelligence.get("threat", {}).get("threat_score", 0)
        root_cause = intelligence.get("causal_graph", {}).get("root_cause")

        # Evaluate heuristics for each action
        heuristic_scores = self._evaluate_heuristics(threat_score, root_cause, preemptive_signal)

        scores = {}
        for action, heuristics in heuristic_scores.items():
            base_cost = self.ACTION_CATALOG[action]["base_cost"]
            learned_weight = self.weights.get(action, 1.0)
            
            memory_boost = 1.0
            if matched_pattern and matched_pattern.get("recommended_action") == action:
                memory_boost = 1 + matched_pattern.get("confidence", 0.2)

            threat_urgency = threat_score / 100.0

            raw = heuristics * learned_weight * memory_boost * (1.0 + threat_urgency)
            adj = raw * (1.0 - base_cost)
            scores[action] = max(0.0, adj)

        # Apply oscillation penalty
        self._apply_oscillation_penalty(scores)

        # Normalize confidence using softmax
        confidence_scores = self._softmax(scores)

        # Select best
        best_action = max(confidence_scores, key=confidence_scores.get)
        confidence = confidence_scores[best_action]

        if best_action != "no_action":
            self._oscillation_window.append(best_action)

        target = root_cause if best_action in ["throttle_process", "kill_process", "preemptive_throttle"] else None

        return {
            "action": best_action,
            "target": target,
            "confidence": round(confidence, 3),
            "reason": f"Heuristics evaluated. Learned weight for {best_action}: {self.weights.get(best_action, 1.0):.2f}",
            "scores": {k: round(v, 3) for k, v in confidence_scores.items()}
        }

    def _evaluate_heuristics(self, threat_score: int, root_cause: Optional[str], preemptive_signal: Optional[Dict[str, Any]]) -> Dict[str, float]:
        scores = {k: 0.0 for k in self.ACTION_CATALOG}
        
        # Base fallback
        scores["no_action"] = 1.0 if threat_score < 25 else 0.1

        if threat_score > 75 and root_cause:
            scores["kill_process"] = 1.0
            scores["throttle_process"] = 0.8
        elif threat_score > 50 and root_cause:
            scores["throttle_process"] = 1.0
            scores["rate_limit"] = 0.6
        elif threat_score > 50 and not root_cause:
            scores["clear_cache"] = 1.0
        elif 25 <= threat_score <= 50:
            scores["rate_limit"] = 0.8
            if root_cause:
                scores["throttle_process"] = 0.7

        if preemptive_signal:
            action = preemptive_signal.get("recommended_action")
            if action in scores:
                scores[action] = max(scores[action], preemptive_signal.get("urgency", 0.8))

        return scores

    def _apply_oscillation_penalty(self, scores: Dict[str, float]):
        if len(self._oscillation_window) < 4:
            return
            
        hist = list(self._oscillation_window)
        # Check if A-B-A-B pattern exists
        if hist[-1] == hist[-3] and hist[-2] == hist[-4] and hist[-1] != hist[-2]:
            aggressive = hist[-1] if self.ACTION_CATALOG[hist[-1]]["base_cost"] > self.ACTION_CATALOG[hist[-2]]["base_cost"] else hist[-2]
            if aggressive in scores:
                scores[aggressive] *= 0.4  # Penalize the more aggressive action to break loop

    def _softmax(self, scores: Dict[str, float]) -> Dict[str, float]:
        exp_scores = {k: math.exp(v) for k, v in scores.items()}
        total = sum(exp_scores.values())
        if total == 0:
            return {k: 0.0 for k in scores}
        return {k: v / total for k, v in exp_scores.items()}
