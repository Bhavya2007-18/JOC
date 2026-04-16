# JOC — The Sentinel Engine

**JOC** (Just-On-Command) is an intelligent, real-time system optimization and security platform. It continuously monitors CPU, RAM, disk, thermal, and process activity, applies multi-factor threat scoring, predicts resource exhaustion, and executes safe, user-approved remediations — all orchestrated through a 7-stage intelligence pipeline and served via a modern React dashboard.

> "This is the problem → here's the root cause → here's what will happen next → do you want me to fix it?"

---

## Description

JOC goes beyond traditional system monitors by combining **statistical anomaly detection**, **causal root-cause analysis**, **predictive forecasting**, and **explainable AI narratives** into a single feedback loop. A dedicated security module scans running processes for suspicious or unknown activity, scores system-wide risk, and generates actionable recommendations.

The platform operates as a decoupled client-server application:
- **Backend** — A Python/FastAPI server that collects system snapshots every 5 seconds, runs them through a multi-engine intelligence pipeline, and exposes structured JSON endpoints plus a WebSocket for real-time state broadcast.
- **Frontend** — A React 19 SPA (Vite + TailwindCSS) with pages for Dashboard, System, Storage, Tweaks, and History, connected to the backend via REST and WebSocket.

---

## Features

### Intelligence Pipeline (7-Stage)
- **Baseline Engine** — Adaptive sliding-window statistics (mean, σ, z-score) over CPU and RAM to define "normal" behavior
- **Threat Engine** — Multi-factor composite scoring (z-score magnitude, rate-of-change, duration, cross-metric correlation) with EMA smoothing (SAFE → SUSPICIOUS → THREAT → CRITICAL)
- **Causal Engine** — Temporal directed-graph construction that links resource-heavy processes to system spikes, producing root-cause chains via BFS traversal
- **Predictive Engine** — Holt's Double Exponential Smoothing for 1-minute and 5-minute CPU/RAM forecasts with time-to-critical estimation
- **XAI Engine** — Translates raw metrics from all engines into structured, human-readable narratives (summary, cause, impact, prediction, recommended action)
- **Thermal Intelligence** — Temperature estimation with hysteresis-based state classification (COOL → WARM → HOT → CRITICAL), thermal velocity tracking, and predictive thermal risk scoring
- **Thermal Predictor** — Forecasts future temperature with time-to-critical alerts; integrates into the causal graph for cross-domain root-cause analysis

### Security Analysis
- **Process Scanner** — Classifies running processes as `known_safe`, `suspicious`, `unknown`, or `idle_resource_hog` based on behavior signals
- **Threat Detection** — Rule-based threat identification for suspicious processes, unknown binaries, idle resource hogs, and background suspicious activity
- **Risk Scoring** — Dynamic risk score (0–100) mapped to LOW / MODERATE / HIGH risk levels
- **Recommendation Engine** — Generates contextual, actionable security recommendations per detected threat
- **Continuous Monitor** — Background thread with adaptive scan intervals (faster when risk is high), deduplication via hash comparison, and alert persistence

### Autonomy Layer
- **Decision Engine** — Weighted decision-making informed by threat, causal, and predictive data
- **Action Engine** — Executes approved system actions (process kills, tweaks) with dry-run support
- **Feedback Engine** — Measures pre/post action effectiveness
- **Learning Engine** — Adjusts decision weights based on historical action outcomes
- **Memory Engine** — Pattern-matching lookup for recurring threat signatures
- **Preemptive Engine** — Early intervention when predictions indicate imminent resource exhaustion
- **Audit Logger** — Deterministic tick-level audit trail of all autonomous decisions

### System Optimization
- **Fix Engine** — Safe process termination (by name or PID) with critical-process protection and full action logging
- **Tweak System** — Registry of system tweaks (power modes, visual effects, disk cleanup, startup management) with dry-run preview, risk guards, and one-click revert
- **Power Modes** — Smart / Beast mode enforcement with thermal-aware safeguards
- **Storage Intelligence** — Filesystem scanning, junk cleaning, duplicate detection (hash-based), cold file identification, and storage breakdown analytics

### Simulation (Red/Blue Team)
- **Red Agent** — Multi-wave attack simulation (CPU probe → memory leak → CPU flood → multi-vector assault) with configurable seeds for reproducibility
- **Blue Agent** — Rule-based defensive responses (throttle, cache flush) to red agent attacks
- **Simulation Engine** — Async tick loop with start/pause/resume/reset and adjustable speed

### Frontend Dashboard
- Real-time system metrics (CPU, RAM, disk, per-core usage)
- Thermal monitoring panel with prediction display
- System health score visualization
- Live event stream via WebSocket
- Simulation control panel
- Storage analysis and cleanup interface
- Tweak management with dry-run preview
- Action history log

---

## Tech Stack

### Backend
| Component | Technology |
|---|---|
| Language | Python 3.8+ |
| Framework | FastAPI |
| ASGI Server | Uvicorn |
| Data Models | Pydantic |
| System Monitoring | psutil |
| Math / Stats | Pure Python (no ML dependencies) + NumPy (analytics) |
| Visualization | Matplotlib (backend charts) |
| Real-time | WebSocket (FastAPI native) |

### Frontend
| Component | Technology |
|---|---|
| Framework | React 19 |
| Build Tool | Vite 8 |
| Styling | TailwindCSS 4 |
| State Management | Zustand |
| HTTP Client | Axios |
| Routing | React Router DOM 7 |
| Charts | Recharts |
| Animations | Framer Motion |
| Icons | Lucide React |

### Stress Testing (Optional)
| Component | Technology |
|---|---|
| GPU Load | PyTorch (CUDA tensor operations) |

---

## Installation

### Prerequisites
- **Python** 3.8 or higher
- **Node.js** 16 or higher
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/Bhavya2007-18/JOC.git
cd JOC
```

### 2. Backend Setup
```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd frontend_new
npm install
cd ..
```

---

## Usage

### Start the Backend
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. API docs are auto-generated at `http://localhost:8000/docs`.

### Start the Frontend
```bash
cd frontend_new
npm run dev
```

The dashboard will be available at `http://localhost:5173`.

### Run Tweak Diagnostics
```bash
python diagnose_tweaks.py
```
Executes all registered tweaks in dry-run mode to verify they load and execute without errors.

### GPU Stress Test (Optional)
```bash
cd accelaration_script
python gpu_script.py
```
Runs continuous large matrix multiplications on CUDA (falls back to CPU if no GPU is available). Useful for testing thermal intelligence under sustained load.

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `JOC_DRY_RUN` | `"true"` | When `true`, all system-modifying actions are simulated. Set to `"false"` for live execution. |
| `JOC_CPU_CEILING` | `90.0` | CPU usage ceiling (%) for simulation validation |
| `JOC_MEMORY_CEILING` | `90.0` | Memory usage ceiling (%) for simulation validation |
| `JOC_SIM_TIMEOUT` | `60` | Simulation timeout in seconds |
| `JOC_OBSERVATION_WINDOW` | `10` | Observation window in seconds for simulation scoring |
| `JOC_MAX_CONCURRENT_SIMS` | `1` | Maximum concurrent simulation runs |
| `JOC_SCORE_WEIGHT_DETECTION` | `40` | Scoring weight for threat detection accuracy |
| `JOC_SCORE_WEIGHT_DECISION` | `40` | Scoring weight for decision quality |
| `JOC_SCORE_WEIGHT_TIME` | `20` | Scoring weight for response time |
| `JOC_RESPONSE_TARGET` | `8.0` | Target response time in seconds |
| `JOC_SIM_LOG_PATH` | `"logs/simulation_logs.json"` | Path for simulation log output |
| `JOC_VALIDATION_CONFIG_PATH` | `""` | Optional JSON config file path (overrides env vars) |

### Tunable Engine Parameters

Located in `backend/intelligence/config.py`:

```python
CPU_THRESHOLD = 80          # CPU usage % to trigger HIGH_CPU issue
MEMORY_THRESHOLD = 80       # Memory usage % to trigger HIGH_MEMORY issue
PROCESS_COUNT_THRESHOLD = 300  # Max background process count
SNAPSHOT_INTERVAL_SECONDS = 5  # Monitor loop frequency
MAX_HISTORY_LENGTH = 100    # Rolling snapshot history size
CPU_WEIGHT = 0.4            # Health score: CPU weight
MEMORY_WEIGHT = 0.4         # Health score: Memory weight
PROCESS_WEIGHT = 0.2        # Health score: Process count weight
```

---

## Project Structure

```
JOC/
├── backend/
│   ├── main.py                        # FastAPI app entry point, router registration, startup events
│   ├── api/                           # REST API route handlers
│   │   ├── analyze.py                 # /analyze endpoint (system diagnostics)
│   │   ├── fix.py                     # /fix endpoint (process kill, tweak execution)
│   │   ├── intelligence_routes.py     # Intelligence pipeline data endpoints
│   │   ├── security_routes.py         # Security analysis endpoints
│   │   ├── security_alerts_routes.py  # Security alert retrieval
│   │   ├── security_monitor_routes.py # Security monitor control (start/stop/status)
│   │   ├── sentinel_routes.py         # WebSocket real-time broadcast
│   │   ├── simulation_routes.py       # Simulation control (start/pause/reset)
│   │   ├── storage_routes.py          # Storage intelligence endpoints
│   │   ├── system_routes.py           # System info and thermal state
│   │   ├── optimizer_routes.py        # Power mode and cleanup controls
│   │   ├── autonomy_routes.py         # Autonomy layer status and control
│   │   └── tweak.py                   # Tweak listing and execution
│   ├── intelligence/                  # Core intelligence engines
│   │   ├── engine.py                  # Primary diagnostic analysis engine (issues, anomalies, changes)
│   │   ├── baseline_engine.py         # Adaptive sliding-window baseline (mean, σ, z-score)
│   │   ├── threat_engine.py           # Multi-factor threat scoring with EMA smoothing
│   │   ├── causal_engine.py           # Temporal causal graph for root-cause analysis
│   │   ├── predictive_engine.py       # Holt's Double Exponential Smoothing forecasts
│   │   ├── xai_engine.py             # Explainable AI narrative generation
│   │   ├── thermal_engine.py          # Thermal state classification with hysteresis
│   │   ├── thermal_predictor.py       # Thermal forecasting and risk prediction
│   │   ├── thermal_adapters.py        # Platform-specific temperature sensor adapters
│   │   ├── monitor_loop.py            # Central 5-second monitor loop (orchestrates all engines)
│   │   ├── snapshot_provider.py       # System data collector (CPU, RAM, disk, processes, services)
│   │   ├── fixer.py                   # Safe process termination and tweak execution
│   │   ├── action_store.py            # Action history persistence
│   │   ├── models.py                  # Data models (SystemSnapshot, Issue, DiagnosticReport)
│   │   ├── config.py                  # Engine thresholds and weights
│   │   ├── constants.py               # Critical process whitelist
│   │   └── tweaks/                    # System tweak registry, executor, guards, and definitions
│   ├── security/                      # Security analysis module
│   │   ├── security_engine.py         # Orchestrator: process scan → threats → risk → recommendations
│   │   ├── security_monitor.py        # Background continuous monitoring thread
│   │   ├── threat_engine.py           # Rule-based threat classification
│   │   ├── process_engine.py          # Process enumeration and classification
│   │   ├── risk_engine.py             # Risk score calculation
│   │   ├── recommendation_engine.py   # Actionable recommendation generation
│   │   ├── alert_engine.py            # Alert threshold detection and persistence
│   │   ├── network_engine.py          # Network connection analysis
│   │   └── sec_config.py             # Security configuration and process whitelists
│   ├── autonomy/                      # Self-healing autonomy layer
│   │   ├── orchestrator.py            # Main autonomy tick loop (7-step cycle)
│   │   ├── decision_engine.py         # Weighted decision logic
│   │   ├── action_engine.py           # Action execution with dry-run
│   │   ├── feedback_engine.py         # Post-action effectiveness measurement
│   │   ├── learning_engine.py         # Adaptive weight adjustment
│   │   ├── memory_engine.py           # Pattern-matching memory lookup
│   │   ├── preemptive_engine.py       # Early intervention signals
│   │   └── audit_log.py              # Tick-level audit trail
│   ├── simulation/                    # Red/Blue team simulation
│   │   └── engine.py                  # Async simulation loop with agent orchestration
│   ├── agents/                        # Simulation agents
│   │   ├── red_agent.py               # Multi-wave attack agent
│   │   └── blue_agent.py             # Defensive response agent
│   ├── storage/                       # Storage intelligence module
│   │   ├── scanner.py                 # Filesystem scanner
│   │   ├── breakdown.py               # Storage usage breakdown
│   │   ├── junk_cleaner.py            # Junk file detection and cleanup
│   │   ├── duplicate_finder.py        # Hash-based duplicate file detection
│   │   ├── cold_files.py             # Cold (unused) file identification
│   │   ├── suggestions.py            # Storage optimization suggestions
│   │   ├── cleanup.py                 # Cleanup operations
│   │   └── db.py                      # SQLite storage for snapshots
│   ├── services/                      # System service integrations
│   │   ├── optimizer/                 # Power mode, cleanup, process management
│   │   ├── intelligence/              # Intelligence service layer
│   │   ├── system_monitor/            # System monitoring services
│   │   ├── thermal/                   # Thermal service layer
│   │   ├── red_team/ & blue_team/     # Simulation service layer
│   │   └── rollback.py               # Action rollback support
│   ├── core/                          # Core configuration
│   │   └── config.py                  # Validation config with env var / JSON file support
│   ├── models/                        # Pydantic data models
│   ├── state/                         # Shared system state (WebSocket broadcast source)
│   ├── events/                        # Event management system
│   ├── training/                      # Training data and model artifacts
│   └── utils/                         # Logging and system utilities
├── frontend_new/                      # React 19 + Vite frontend
│   └── src/
│       ├── pages/                     # Dashboard, System, Storage, Tweaks, History
│       ├── components/                # UI components (thermal panels, simulation, modes, etc.)
│       ├── api/                       # API client (Axios)
│       ├── store/                     # Zustand global state
│       ├── hooks/                     # Custom React hooks
│       ├── lib/                       # WebSocket client
│       └── context/                   # React context providers
├── accelaration_script/               # CPU/GPU stress-testing scripts
│   ├── gpu_script.py                  # PyTorch CUDA matrix multiplication loop
│   ├── cpu_script.py                  # CPU stress (placeholder)
│   └── both_script.py                # Combined stress (placeholder)
├── docs/                              # Technical documentation
├── requirements.txt                   # Python dependencies
├── diagnose_tweaks.py                 # Tweak diagnostic runner
└── .gitignore
```

---

## How It Works

### Monitor Loop (Core Cycle)

The `MonitorLoop` runs in a background thread on a **5-second interval**. Each tick executes the full intelligence pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│                    MONITOR LOOP (every 5s)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Stage 0: Snapshot Collection                               │
│     └─ psutil → CPU, RAM, disk, processes, services, I/O   │
│                                                             │
│  Stage 1: Baseline Analysis                                 │
│     └─ Rolling mean/σ/z-score for CPU and RAM               │
│                                                             │
│  Stage 2: Threat Scoring                                    │
│     └─ 4-factor weighted composite → 0-100 threat score     │
│                                                             │
│  Stage 3: Causal Analysis                                   │
│     └─ Temporal graph linking processes → resource spikes    │
│                                                             │
│  Stage 4: Predictive Forecast                               │
│     └─ Holt's DES → 1m/5m CPU/RAM predictions + ETA        │
│                                                             │
│  Stage 5: XAI Narrative                                     │
│     └─ Human-readable summary, cause, impact, prediction    │
│                                                             │
│  Stage 6: Thermal Intelligence                              │
│     └─ Temperature estimation, state classification,        │
│        velocity tracking, thermal risk scoring              │
│                                                             │
│  Stage 7: Thermal Prediction                                │
│     └─ Future temp forecast, time-to-critical,              │
│        preemptive mitigation (auto-degrade power mode)      │
│                                                             │
│  Autonomy Tick                                              │
│     └─ Decision → Action → Feedback → Learning → Memory     │
│                                                             │
│  Broadcast                                                  │
│     └─ WebSocket push to all connected frontend clients     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Security Pipeline

The security module operates **independently** in its own background thread:

1. **Enumerate** all running processes via `psutil`
2. **Classify** each process against known-safe lists and behavioral heuristics
3. **Detect threats** — suspicious processes, unknown binaries, idle resource hogs, background anomalies
4. **Score risk** — aggregate threat count → 0-100 score → LOW / MODERATE / HIGH
5. **Generate recommendations** — contextual remediation advice per threat
6. **Deduplicate** — hash-compare results against previous scan to avoid redundant alerts
7. **Adapt interval** — increase scan frequency when risk score exceeds 70

### Thermal Intelligence

JOC estimates temperature from CPU usage via a synthetic fallback model and applies:
- **EMA Smoothing** (α = 0.35) for signal stability
- **Hysteresis State Machine** with separate enter/exit thresholds to prevent mode oscillation
- **Thermal Velocity** classification (stable / rising / spiking)
- **Preemptive Power Mode Guard** — automatically downgrades BEAST → SMART mode when thermal prediction indicates HIGH or CRITICAL risk

---

## Performance Notes / Limitations

- **Platform**: Primary target is **Windows**. Service enumeration uses `psutil.win_service_iter()` which is Windows-only; other platforms gracefully degrade.
- **Temperature**: Hardware temperature reading depends on platform-specific sensor adapters. The fallback synthetic model (`40 + cpu_usage * 0.5`) provides an approximation but is not a substitute for real sensor data.
- **Snapshot Overhead**: Each 5-second cycle calls `psutil.process_iter()` with `cpu_percent()`, which requires a brief blocking interval (~0.5s). This is by design for accuracy.
- **Process Enumeration**: Some system processes may return `AccessDenied` — these are silently skipped.
- **Causal Graph Decay**: The causal graph applies a 0.98 decay factor per cycle. Long-running root causes will naturally lose weight over time, which is intentional to keep the graph current.
- **Predictive Warm-up**: The predictive engine requires ≥ 5 observations (~25 seconds) before trend labels become meaningful. The baseline engine requires ≥ 10 samples (~50 seconds) for reliable z-scores.
- **Frontend Polling**: The frontend relies on WebSocket for real-time data. If the WebSocket disconnects, data will stale until reconnection.

---

## Safety Notes

> [!CAUTION]
> **JOC interacts directly with system processes and can terminate running applications.**

- **Dry-Run Mode is ON by default.** The `JOC_DRY_RUN` environment variable defaults to `"true"`. In this mode, all process kills and system tweaks are simulated — no actual system changes occur.
- **Critical Process Protection.** A hardcoded whitelist prevents JOC from terminating essential system processes (e.g., `explorer`, `svchost`, `csrss`, `lsass`, `winlogon`). This protection cannot be bypassed through the API.
- **User Confirmation Required.** The autonomy layer is **disabled by default** and must be explicitly enabled via the API. Even when enabled, high-risk tweaks require explicit `confirm_high_risk` authorization.
- **Action Logging.** Every executed action (including dry-runs) is recorded with a unique ID, timestamp, target, result, and reversibility status. Tweak actions support one-click revert.
- **System Load from Stress Scripts.** The scripts in `accelaration_script/` are designed to **deliberately saturate** CPU and/or GPU. Running `gpu_script.py` will push GPU utilization to near 100% and may cause thermal throttling or instability on inadequately cooled systems. Use with caution and monitor temperatures.
- **Security Monitor Resource Usage.** The background security monitor runs continuous `psutil` scans. On systems with thousands of processes, this may introduce measurable CPU overhead. Adjust the scan interval via the API if needed.

---

## License

This project is developed for educational and demonstration purposes.

---

**JOC — Because your computer deserves an intelligent sentinel.**