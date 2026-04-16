from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioTraits:
    resource_type: str  # cpu, memory, disk, network, multi
    pattern: str  # spike, sustained, leak, burst
    process_concentration: str  # single, distributed
    severity_band: str  # moderate, high, critical
    has_root_cause_process: bool
    ramp_style: str = "gradual" # sudden, gradual, oscillating
    duration_class: str = "medium" # short, medium, long

    def similarity(self, other: ScenarioTraits) -> float:
        score = 0.0

        if self.resource_type == other.resource_type:
            score += 0.25
        if self.pattern == other.pattern:
            score += 0.15
        if self.process_concentration == other.process_concentration:
            score += 0.20
        if self.severity_band == other.severity_band:
            score += 0.10
        if self.has_root_cause_process == other.has_root_cause_process:
            score += 0.10
        if self.ramp_style == other.ramp_style:
            score += 0.10
        if self.duration_class == other.duration_class:
            score += 0.10

        return score