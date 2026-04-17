import math
from typing import Dict, Any, Optional
from collections import deque

class DecisionEngine:
    ACTION_CATALOG = {
        "throttle_process":  {"base_cost": 0.2, "base_score": 0.6, "safe": True},
        "kill_process":      {"base_cost": 0.9, "base_score": 0.8, "safe": False},
        "clear_cache":       {"base_cost": 0.1, "base_score": 0.4, "safe": True},
        "rate_limit":        {"base_cost": 0.3, "base_score": 0.5, "safe": True},
        "reduce_io":         {"base_cost": 0.2, "base_score": 0.5, "safe": True},
        "suspend_process":   {"base_cost": 0.5, "base_score": 0.7, "safe": False},
        "no_action":         {"base_cost": 0.0, "base_score": 0.3, "safe": True},
        "preemptive_throttle":{"base_cost": 0.2, "base_score": 0.55,"safe": True},
    }

    def __init__(self):
        self.weights = {action: 1.0 for action in self.ACTION_CATALOG}
        self._oscillation_window = deque(maxlen=5)
        
        # Priority order for issue categories
        self.CATEGORY_PRIORITY = {
            "thermal": 100,
            "security": 90,
            "threat": 80,
            "cpu": 70,
            "memory": 60,
            "disk": 50,
            "system": 40,
        }

    def update_weights(self, new_weights: Dict[str, float]):
        self.weights.update(new_weights)

    def decide(
        self, 
        intelligence: Dict[str, Any], 
        matched_pattern: Optional[Dict[str, Any]] = None, 
        preemptive_signal: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        New prioritization-aware decision logic.
        """
        # Extract issues from intelligence payload
        # Note: MonitorLoop will now be updated to pass these
        issues = intelligence.get("issues", [])
        threat_score = intelligence.get("threat", {}).get("threat_score", 0)
        
        # Rank issues if multiple exist
        ranked_issues = self._rank_issues(issues, intelligence)
        top_issue = ranked_issues[0] if ranked_issues else None
        
        # Use top issue category/root_cause for heuristics
        category = "system"
        root_cause = intelligence.get("causal_graph", {}).get("root_cause")
        pid = None
        
        if top_issue:
            if isinstance(top_issue, dict):
                category = top_issue.get("category", "system")
                evidence = top_issue.get("evidence", {})
            else:
                category = getattr(top_issue, "category", "system")
                evidence = getattr(top_issue, "evidence", {})
                
            fix_action = evidence.get("fix_action", {}) if isinstance(evidence, dict) else {}
            if fix_action.get("target"):
                root_cause = fix_action.get("target")
            pid = fix_action.get("pid")

        # Evaluate heuristics for each action
        heuristic_scores = self._evaluate_heuristics(threat_score, category, root_cause, preemptive_signal)

        scores = {}
        for action, heuristics in heuristic_scores.items():
            base_cost = self.ACTION_CATALOG[action]["base_cost"]
            learned_weight = self.weights.get(action, 1.0)
            
            memory_boost = 1.0
            if matched_pattern and matched_pattern.get("recommended_action") == action:
                # Stronger boost for high-confidence learning patterns
                conf = matched_pattern.get("confidence", 0.2)
                memory_boost = 1.0 + (conf * 1.5)  # Max boost of 2.5x

            threat_urgency = threat_score / 100.0

            # Prioritization boost: if the best heuristic action matches the top_issue category needs
            prio_boost = 1.0
            if top_issue:
                sev = top_issue.get("severity") if isinstance(top_issue, dict) else getattr(top_issue, "severity", "medium")
                sev_val = str(getattr(sev, "value", sev)).lower()
                if sev_val in ["high", "critical"]:
                    prio_boost = 1.5

            raw = heuristics * learned_weight * memory_boost * (1.0 + threat_urgency) * prio_boost
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
            "pid": pid,
            "confidence": round(confidence, 3),
            "top_issue": (top_issue.get("id") if isinstance(top_issue, dict) else getattr(top_issue, "id", "none")) if top_issue else "none",
            "reason": f"Heuristics evaluated for {category}. Ranked {len(ranked_issues)} issues.",
            "scores": {k: round(v, 3) for k, v in confidence_scores.items()}
        }

    def _rank_issues(self, issues: List[Any], intelligence: Dict[str, Any]) -> List[Any]:
        """Ranks issues by category priority and severity."""
        if not issues:
            return []
            
        def get_score(issue):
            if isinstance(issue, dict):
                cat = str(issue.get("category", "system")).lower()
                sev = str(issue.get("severity", "moderate")).lower()
            else:
                cat = str(getattr(issue, "category", "system")).lower()
                sev_obj = getattr(issue, "severity", "moderate")
                sev = str(getattr(sev_obj, "value", sev_obj)).lower()
                
            cat_score = self.CATEGORY_PRIORITY.get(cat, 0)
            
            sev_score = 0
            if sev == "critical": sev_score = 1000
            elif sev == "high": sev_score = 500
            elif sev == "medium": sev_score = 100
            
            return cat_score + sev_score

        return sorted(issues, key=get_score, reverse=True)

    def _evaluate_heuristics(
        self, 
        threat_score: int, 
        category: str, 
        root_cause: Optional[str], 
        preemptive_signal: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        scores = {k: 0.0 for k in self.ACTION_CATALOG}
        
        # Base fallback
        scores["no_action"] = 1.0 if threat_score < 25 else 0.1

        # Category-specific heuristics
        if category == "thermal":
            scores["throttle_process"] = 1.0
            scores["clear_cache"] = 0.5
        elif category == "cpu":
            if threat_score > 75: scores["kill_process"] = 1.0
            else: scores["throttle_process"] = 1.0
        elif category == "memory":
            scores["clear_cache"] = 1.0
            if threat_score > 70: scores["kill_process"] = 0.7
        elif category == "disk":
            scores["clear_cache"] = 1.0
            scores["reduce_io"] = 0.8
        
        # Preemptive overrides
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
