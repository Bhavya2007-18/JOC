from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List
import ctypes

import psutil

from intelligence.constants import CRITICAL_PROCESSES
from utils.execution_context import ExecutionContext


@dataclass
class GuardReport:
    blocked: bool = False
    warnings: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
    admin_required: bool = False
    admin_used: bool = False

    def to_dict(self) -> Dict[str, object]:
        return {
            "blocked": self.blocked,
            "warnings": self.warnings,
            "reasons": self.reasons,
            "admin_required": self.admin_required,
            "admin_used": self.admin_used,
        }


def _is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


class ExecutionGuard:
    CPU_BLOCK_THRESHOLD = 90.0
    CPU_WARN_THRESHOLD = 80.0
    PLANNED_TARGETS = {
        "gaming_boost": [
            "searchindexer.exe",
            "searchhost.exe",
            "onedrive.exe",
            "msedge.exe",
            "teams.exe",
            "skype.exe",
            "spotify.exe",
            "discord.exe",
            "slack.exe",
            "cortana.exe",
            "gamebarpresencewriter.exe",
            "yourphone.exe",
            "microsoftedgeupdate.exe",
            "googlechromeupdate.exe",
        ]
    }

    def check_admin(self, tweak_name: str, context: ExecutionContext) -> GuardReport:
        report = GuardReport()
        admin_required_for_full_effect = {"clean_ram", "battery_saver"}
        admin_used = _is_admin()

        report.admin_used = admin_used
        report.admin_required = tweak_name in admin_required_for_full_effect

        # We only hard-block if admin is mandatory for the operation's safety,
        # which is not the case yet; we warn and enforce truthful partial status.
        if report.admin_required and not admin_used and context.mode != "preview":
            report.warnings.append("Admin privileges are unavailable; execution may be partial.")
            report.reasons.append("admin_missing")
        return report

    def check_safe_processes(self, planned_targets: List[str]) -> GuardReport:
        report = GuardReport()
        protected = {p.lower().replace(".exe", "") for p in CRITICAL_PROCESSES}
        matched = []
        for target in planned_targets:
            norm = (target or "").lower().replace(".exe", "")
            if norm in protected:
                matched.append(target)

        if matched:
            report.blocked = True
            report.reasons.append("protected_process_target")
            report.warnings.append(f"Refusing to target protected processes: {', '.join(matched)}")
        return report

    def check_system_load(self, tweak_name: str, context: ExecutionContext) -> GuardReport:
        report = GuardReport()
        if context.mode == "preview":
            return report

        try:
            cpu = psutil.cpu_percent(interval=None)
        except Exception:
            cpu = 0.0

        if tweak_name == "gaming_boost" and cpu >= self.CPU_BLOCK_THRESHOLD:
            report.blocked = True
            report.reasons.append("cpu_overload_block")
            report.warnings.append(
                f"CPU is already at {cpu:.1f}%. Blocking Combat Mode to avoid instability."
            )
        elif cpu >= self.CPU_WARN_THRESHOLD:
            report.warnings.append(
                f"High CPU load detected ({cpu:.1f}%). Proceeding may have reduced impact."
            )
            report.reasons.append("cpu_high_warn")
        return report

    def confirm_if_high_risk(self, tweak_name: str, context: ExecutionContext) -> GuardReport:
        report = GuardReport()
        high_risk_tweaks = {"gaming_boost"}
        if tweak_name in high_risk_tweaks and context.mode == "execute" and not context.confirmed_high_risk:
            report.blocked = True
            report.warnings.append(
                "High-risk tweak requested without explicit high-risk confirmation flag."
            )
            report.reasons.append("high_risk_unconfirmed")
        return report

    def evaluate(self, tweak_name: str, context: ExecutionContext) -> GuardReport:
        combined = GuardReport()
        for part in [
            self.check_admin(tweak_name, context),
            self.check_safe_processes(self.PLANNED_TARGETS.get(tweak_name, [])),
            self.check_system_load(tweak_name, context),
            self.confirm_if_high_risk(tweak_name, context),
        ]:
            combined.blocked = combined.blocked or part.blocked
            combined.admin_required = combined.admin_required or part.admin_required
            combined.admin_used = combined.admin_used or part.admin_used
            combined.warnings.extend(part.warnings)
            combined.reasons.extend(part.reasons)
        return combined
