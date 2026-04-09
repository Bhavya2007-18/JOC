from __future__ import annotations

import math
from typing import List


def compute_z_score(current_value: float, history: List[float]) -> float:
    if len(history) < 2:
        return 0.0

    mean = sum(history) / len(history)
    variance = sum((value - mean) ** 2 for value in history) / len(history)
    std = math.sqrt(variance)

    if std == 0.0:
        return 0.0

    return (current_value - mean) / std


def is_anomaly(z_score: float, threshold: float = 2.0) -> bool:
    return abs(z_score) > threshold
