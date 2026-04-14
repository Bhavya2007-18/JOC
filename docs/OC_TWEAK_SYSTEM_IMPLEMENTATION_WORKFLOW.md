# OC Tweak System Implementation Workflow

## 1. Goal

Build a safe, accurate, and performant OC tweak system for all four protocols (Combat, Stealth, Neural Sync, Memory Flush), while adding the core infrastructure needed for reversibility, observability, and future intelligence automation.

This document defines:
- Execution guardrails before any OS action
- Standardized execution context and action result schema
- System state snapshot strategy for true revert
- Phase-by-phase implementation and validation flow

---

## 2. Ground Truth Baseline

Current flow:
1. `Tweaks.jsx` sends `POST /tweak/execute` with `{ tweak_name, dry_run }`
2. `api/tweak.py` calls `FixEngine.execute_tweak(...)`
3. `intelligence/tweaks/executor.py` mutates global `config.DRY_RUN` (thread-unsafe)
4. `intelligence/tweaks/basic_tweaks.py` executes OS calls (`psutil`, `ctypes`, `subprocess`)
5. `FixEngine` wraps result with `action_id`
6. Frontend maps payload to preview modal or execute banner

Key risks in baseline:
- No pre-execution guard layer
- Thread-unsafe global dry-run mutation
- Incomplete revert semantics
- Silent permission failures in some paths
- Response shape inconsistencies and misleading wording

---

## 3. Mandatory New Foundation Layers

## 3.1 Execution Guard Layer (Required Before Any Tweak Action)

Create a dedicated guard component called `ExecutionGuard` and run it before every tweak apply/revert action.

Target API:
- `check_admin(tweak_name, context)`
- `check_safe_processes(tweak_name, planned_targets)`
- `check_system_load(tweak_name, telemetry)`
- `confirm_if_high_risk(guard_report)`

Behavior requirements:
- If guard result is blocking, execution must not proceed.
- If guard result is warning-level, execution requires explicit confirmation path.
- Guard outcomes must be returned in API response and logs.

Examples:
- Combat execute: if CPU is already critical (example: > 90%), block by default.
- Memory Flush execute: if admin required path is unavailable, return explicit warning and degrade behavior truthfully.

---

## 3.2 System State Snapshot Engine (Required For Revert and Debugging)

Create a formal snapshot model captured before impactful execution.

Target model:

```python
class SystemSnapshot:
    processes: list
    priorities: dict
    memory_state: dict
    power_plan: str
    timestamp: datetime
```

Usage requirements:
- Capture snapshot before execute when action is reversible or partially reversible.
- Persist snapshot metadata with `action_id`.
- Use snapshot in revert handlers to restore tracked state.
- Keep snapshot retention policy bounded (avoid unbounded growth).

Outcomes:
- True priority revert for Combat and future Stealth suspend/resume.
- Better incident debugging and telemetry explainability.
- Foundation for adaptive/ML decisions.

---

## 3.3 Action Result Standardization (Move Earlier, Not Phase-Late)

Introduce a single normalized action response contract now (Step 1), not only in later phase cleanup.

Canonical response shape:

```json
{
  "mode": "preview | execute | revert",
  "tweak": "combat | stealth | neural_sync | clean_ram",
  "status": "success | partial | failed | blocked",
  "simulated": true,
  "effects": {
    "targets": [],
    "power_plan": null,
    "memory_freed": null
  },
  "meta": {
    "duration_ms": 120,
    "admin_required": true,
    "admin_used": false,
    "guard": {
      "blocked": false,
      "warnings": []
    }
  }
}
```

Requirements:
- Every tweak returns this envelope shape.
- Existing frontend fields remain supported through compatibility mapping until migration completes.
- Partial and blocked execution must be first-class statuses, never hidden behind success text.

---

## 4. Smart Execution Order (Implementation Plan)

## Step 1 (Foundation and Stabilization)

Scope:
- Remove global `DRY_RUN` mutation.
- Introduce per-request `ExecutionContext`.
- Implement `ExecutionGuard`.
- Add structured logging on every action boundary.
- Start standardized action response envelope.

Acceptance:
- No global dry-run mutation in runtime path.
- Guard runs for preview/execute/revert paths.
- API returns normalized envelope with guard metadata.
- Concurrent requests remain isolated.

---

## Step 2 (Performance and Reality)

Scope:
- Fix Neural Sync sampling to remove serial blocking loop.
- Implement real Memory Flush standby purge API path.
- Add Memory Flush preview estimate (non-destructive).

Acceptance:
- Neural Sync avoids N x 100ms sampling delay pattern.
- Memory Flush admin path performs real purge attempt and reports result.
- Preview provides informative estimated reclaimable memory.

---

## Step 3 (Control and Reversibility)

Scope:
- Implement formal `SystemSnapshot` capture + persistence.
- Combat foreground process detection (real target selection).
- Combat priority snapshot restore on revert.

Acceptance:
- Revert restores tracked priorities + power plan.
- Irreversible effects are clearly labeled as irreversible.
- Foreground-based boost target is deterministic and logged.

---

## Step 4 (Truth Alignment End-to-End)

Scope:
- Complete API schema normalization across all tweaks.
- Update frontend mapping in `Tweaks.jsx`.
- Fix wording mismatches (example: avoid "suspended" when priority is only lowered).

Acceptance:
- UI copy matches backend reality in all modes.
- No misleading labels remain in preview or execute outputs.

---

## Step 5 (Intelligence Layer Evolution)

Scope:
- Add simple decision engine for mode suggestion using live telemetry rules.
- Add bounded auto-trigger support behind feature flag.
- Add adaptive threshold configuration for future learning loop.

Example bootstrap logic:

```python
if cpu > 80:
    suggest("combat")
elif battery < 25:
    suggest("stealth")
```

Acceptance:
- Decision engine suggestions are explainable and logged.
- Auto-trigger remains opt-in and safety-gated by `ExecutionGuard`.

---

## 5. Execution Guard Policy Matrix

Minimum policy examples:
- Combat execute:
  - block if CPU critical and sustained
  - block if planned targets include protected processes
- Memory Flush execute:
  - warn/partial if admin-only operations unavailable
- Neural Sync execute:
  - skip or throttle if guard detects recent execution overload window
- Stealth execute:
  - require clear admin status for service operations

Policy requirements:
- Config-driven thresholds (not hardcoded constants across logic).
- Policy decision and reason codes must be returned in `meta.guard`.

---

## 6. Testing and Verification Matrix

For each mode (Combat, Stealth, Neural Sync, Memory Flush):
1. Preview as non-admin
2. Execute as non-admin
3. Execute as admin
4. Revert after execute
5. Guard-blocked execution path
6. Concurrent preview + execute overlap

Validate:
- Guard decision correctness
- Action status correctness (`success`/`partial`/`failed`/`blocked`)
- OS effect truthfulness
- Revert fidelity (where applicable)
- Latency and resource impact

---

## 7. Observability and Reliability Requirements

All ctypes/subprocess/process-control paths must:
- wrap exceptions and return explicit errors
- include structured logs with reason codes
- avoid silent no-op outcomes

Minimum telemetry fields:
- `tweak_name`
- `mode`
- `dry_run`
- `action_id`
- `duration_ms`
- `status`
- `admin_required`
- `admin_used`
- `guard_blocked`
- `targets_total`
- `targets_succeeded`
- `targets_failed`
- `targets_skipped`

---

## 8. Risk Watchlist (Must Be Actively Managed)

1. Windows API instability:
   - `ctypes` calls can fail per build/policy, always log and classify failures.
2. Permission inconsistency:
   - admin and non-admin branches must produce explicit status differences.
3. Process edge-case safety:
   - strict protected-process deny list and validation before kill/reprioritize.
4. Performance spikes:
   - bound Neural Sync cadence and add cooldown/lock to avoid overload.

---

## 9. Definition of Done

The OC tweak system is considered ready when:
1. ExecutionGuard is active for all tweak actions.
2. Global dry-run mutation is removed and concurrency-safe context is in place.
3. Standard action response envelope is used consistently.
4. SystemSnapshot is captured and used for meaningful revert.
5. Neural Sync sampling no longer introduces serial blocking stalls.
6. Memory Flush standby purge is real and truthfully reported.
7. Frontend language and backend actions are fully aligned.

---

## 10. Immediate Build Start

Start implementation in this exact order:
1. Step 1 Foundation (`ExecutionContext`, `ExecutionGuard`, response envelope, structured logging)
2. Step 2 Performance/Reality fixes (Neural Sync + Memory Flush)
3. Step 3 Reversibility and targeting (`SystemSnapshot` + Combat restore path)

This sequence gives maximum risk reduction first, then performance, then trust and intelligence infrastructure.
