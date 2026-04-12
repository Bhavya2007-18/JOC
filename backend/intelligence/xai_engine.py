"""
Explainable AI (XAI) Engine — Phase 2, JOC Sentinel
---------------------------------------------------
Translates raw anomaly, causal, and predictive metrics into a structured,
human-readable narrative for dashboard display.

Usage:
    xai = XAIEngine()
    explanation = xai.generate(cpu, ram, baseline_data, threat_data, causal_data, pred_data)
"""

from typing import Dict, Any, Optional

class XAIEngine:
    
    def generate(
        self,
        cpu: float,
        ram: float,
        baseline_data: Dict[str, Any],
        threat_data: Dict[str, Any],
        causal_data: Dict[str, Any],
        pred_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Assembles a contextual narrative from the outputs of the other 4 engines.
        """
        # Determine the primary issue domain
        cpu_z = baseline_data.get("cpu_z_score", 0.0)
        ram_z = baseline_data.get("ram_z_score", 0.0)
        
        # Guard against None values during warm-up
        if cpu_z is None: cpu_z = 0.0
        if ram_z is None: ram_z = 0.0
        
        threat_level = threat_data.get("level", "SAFE")
        
        # 1. SUMMARY Generation
        summary = self._generate_summary(cpu, ram, cpu_z, ram_z, baseline_data, threat_level)
        
        # 2. CAUSE Generation
        cause = self._generate_cause(causal_data)
        
        # 3. IMPACT Generation
        impact = self._generate_impact(threat_level)
        
        # 4. PREDICTION Generation
        prediction = self._generate_prediction(pred_data, max(abs(cpu_z), abs(ram_z)))
        
        # 5. RECOMMENDED ACTION Generation
        action = self._generate_action(threat_level, causal_data)
        
        return {
            "summary": summary,
            "cause": cause,
            "impact": impact,
            "prediction": prediction,
            "recommended_action": action
        }

    def _generate_summary(
        self, 
        cpu: float, 
        ram: float, 
        cpu_z: float, 
        ram_z: float, 
        baseline: dict,
        level: str
    ) -> str:
        
        if level == "SAFE":
            return "System Operating within normal baseline parameters."
            
        primary = "CPU" if abs(cpu_z) >= abs(ram_z) else "RAM"
        val = cpu if primary == "CPU" else ram
        z = abs(cpu_z) if primary == "CPU" else abs(ram_z)
        base = baseline.get(f"{primary.lower()}_baseline", 0.0)
        
        if base is None:
            return f"System showing elevated {primary} usage."
            
        verb = "surged" if z > 3.0 else "elevated"
        return f"{primary} usage has {verb} to {val:.1f}% — {z:.1f}σ above the historical {base:.1f}% baseline."

    def _generate_cause(self, causal_data: dict) -> str:
        root = causal_data.get("root_cause")
        chain = causal_data.get("chain", [])
        
        if not root:
            return "No definitive root process identified. Issue may be diffuse or system-level."
            
        chain_str = " → ".join(chain)
        return (f"Root analysis identified '{root}' as the primary stressor. "
                f"Causal chain: {chain_str}.")

    def _generate_impact(self, threat_level: str) -> str:
        if threat_level == "CRITICAL":
            return "Severe system degradation occurring. Immediate instability risk."
        elif threat_level == "THREAT":
            return "System performance is visibly degraded. Processes may hang or fail to allocate resources."
        elif threat_level == "SUSPICIOUS":
            return "Minor resource contention. Background tasks may be slightly delayed."
        return "No adverse impact detected."

    def _generate_prediction(self, pred_data: dict, highest_z: float) -> str:
        risk = pred_data.get("risk", "LOW")
        
        # Find which metric is worse based on prediction trends
        c_trend = pred_data.get("predicted_cpu", {}).get("trend", "stable")
        r_trend = pred_data.get("predicted_ram", {}).get("trend", "stable")
        
        primary_pred = pred_data.get("predicted_cpu", {}) if "rising" in c_trend else pred_data.get("predicted_ram", {})
        if not primary_pred and "predicted_cpu" in pred_data:
            primary_pred = pred_data["predicted_cpu"] # fallback
            
        eta = primary_pred.get("time_to_critical_s", -1)
        trend = primary_pred.get("trend", "stable").replace("_", " ")
        
        if risk == "LOW":
            return "Trajectory is stable. Unlikely to breach thresholds."
            
        res = f"Trajectory is {trend}."
        if eta == 0:
            res += " Critical threshold is currently being breached."
        elif eta > 0:
            res += f" Projected to reach critical threshold in approx. {eta} seconds."
            
        return res

    def _generate_action(self, threat_level: str, causal_data: dict) -> str:
        root = causal_data.get("root_cause")
        
        if threat_level == "SAFE":
            return "Continue monitoring."
            
        action = []
        if threat_level in ["THREAT", "CRITICAL"]:
            if root:
                action.append(f"Immediate action required: Terminate process '{root}'.")
            else:
                action.append("Immediate action required: Clean up background processes.")
            action.append("Engage Battle Station protocols to restrict unapproved workloads.")
        else: # SUSPICIOUS
            action.append("Audit recent activity for irregular patterns.")
            if root:
                action.append(f"Consider throttling '{root}' if behavior persists.")
                
        return " ".join(action)
