import numpy as np
from typing import List, Dict
from .models import SystemSnapshot

class PredictiveEngine:
    """
    Forecasting engine to predict resource exhaustion.
    In production, this is the wrapper for an ONNX-optimized LSTM.
    Currently uses an extrapolation heuristic over the sliding window.
    """
    def __init__(self, window_size: int = 30):
        self.window_size = window_size
        self.history = []

    def observe(self, snapshot: SystemSnapshot):
        self.history.append({
            "timestamp": snapshot.timestamp,
            "cpu": snapshot.cpu_percent,
            "memory": snapshot.memory_percent,
            "disk": snapshot.disk_percent
        })
        if len(self.history) > self.window_size:
            self.history.pop(0)

    def forecast(self, minutes_ahead: int = 5) -> Dict[str, dict]:
        if len(self.history) < 10:
            return {"status": "insufficient_data"}
        
        # Linear regression extrapolation for proxy forecasting
        x = np.arange(len(self.history))
        predictions = {}
        for metric in ["cpu", "memory", "disk"]:
            y = np.array([h[metric] for h in self.history])
            
            # Avoid polyfit crashing on zero variance
            if np.all(y == y[0]):
                slope, intercept = 0.0, y[0]
            else:
                slope, intercept = np.polyfit(x, y, 1)
            
            # Predict 'lines' points ahead
            # Assuming ~5 sec interval for snapshots -> 12 per minute
            points_ahead = minutes_ahead * 12 
            projected = slope * (len(self.history) + points_ahead) + intercept
            projected = max(0.0, min(100.0, float(projected)))
            
            variance = np.var(y)
            confidence = max(0.1, 1.0 - (variance / 1000) - (minutes_ahead * 0.05))
            
            predictions[metric] = {
                f"{minutes_ahead}m": projected,
                "confidence": confidence,
                "trend": "up" if slope > 0.5 else "down" if slope < -0.5 else "stable"
            }
            
        return predictions
