# JOC – The Sentinel Engine

JOC (Just‑On‑Command) is an **intelligent system optimization assistant** that doesn't just monitor - it understands, explains, and safely fixes performance issues. Think of it as a decision-making assistant for your computer.

> "This is the problem → here's the fix → do you want me to apply it?"

## 🚀 Overview

Most system tools either show charts or blindly clean files. JOC is different:

- **Detects** performance issues in real-time
- **Explains** root causes in human-readable language
- **Suggests** safe, targeted fixes
- **Executes** optimizations with user permission

## 🧠 Core Architecture

JOC operates as a 4-layer intelligent system:

### 1. Data Collection Layer (Observation)
Continuously monitors system metrics using:
- `psutil` for CPU, RAM, disk, and process monitoring
- `os` and `platform` for system information
- `subprocess` for command execution

### 2. Intelligence Layer (Thinking)
Analyzes patterns and identifies issues:
- Root cause detection
- Anomaly detection (spikes, abnormal patterns)
- "What Changed?" analysis
- Mode-specific logic (Gaming/Performance/Battery)

### 3. Explanation Layer (Communication)
Translates technical findings into clear explanations:
- Template-based human-readable messages
- Context-aware problem descriptions

### 4. Action Layer (Execution)
Safely executes fixes with user permission:
- Process management
- File cleanup operations
- System optimizations
- Comprehensive safety checks

## ✨ Key Features

### 🎮 Operation Modes
- **Gaming Mode**: Maximizes FPS and responsiveness
- **Performance Mode**: Balances speed and battery life
- **Battery Saver Mode**: Extends battery runtime

### 💾 Storage Intelligence
- Junk and cache cleaner
- Duplicate file detection (hashing-based)
- Cold file identification
- Storage breakdown analytics

### 🔍 Advanced Analysis
- **Root Cause Engine**: Identifies why systems slow down
- **What Changed Analyzer**: Tracks recent system behavior changes
- **Anomaly Detection**: Flags unusual resource usage patterns
- **Developer Mode**: Optimizes for coding environments

### ⚡ Quick Actions
- One-click RAM clearing
- Disk cleanup operations
- System restart management
- Process termination (with safety checks)

## 🛠 Technology Stack

### Backend (Core Engine)
- **Language**: Python 3.8+
- **Key Libraries**:
  - `psutil`: System monitoring and process management
  - `os`/`shutil`: File system operations
  - `platform`: OS detection and specifics
  - `subprocess`: Safe command execution
  - `hashlib`: File hashing for duplicate detection

### Frontend (User Interface)
- **React** with modern hooks and state management
- **Custom CSS** with design system tokens
- **Lucide React** for consistent icons
- **Vite** for fast development and building

### Safety Systems
- Process whitelist/blacklist protection
- User confirmation for all destructive actions
- Comprehensive action logging
- Dry-run capability for testing

## 📁 Project Structure

```
JOC/
├── frontend/                 # React-based user interface
│   ├── src/
│   │   ├── App.jsx           # Main application component
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Design system and styles
│   ├── package.json          # Frontend dependencies
│   ├── vite.config.js        # Build configuration
│   └── index.html            # HTML template
├── design-assets/            # UI mockups and design reference
│   ├── dashboard_insights_overview/
│   ├── system_actions_management/
│   └── operation_modes_configuration/
├── backend/                  # Python intelligence engine (planned)
│   ├── core/
│   │   ├── monitoring.py
│   │   ├── intelligence.py
│   │   └── actions.py
│   └── utils/
├── README.md                 # This file
└── .gitignore               # Version control exclusions
```

## 🎨 Design Philosophy

### Kinetic Command Interface
- **Color Palette**: Deep space (#0d0e12) with electric blue accents (#81ecff)
- **Typography**: Space Grotesk for headers, Inter for body text
- **Layout**: Intentional asymmetry with tactical "control pods"
- **Interaction**: Glassmorphic elements with gradient accents

### No-Line Design System
- Borders are a failure of hierarchy
- Sections defined through tonal shifts and physical layering
- Floating elements use glassmorphism with backdrop blur

## 🔧 Getting Started

### Prerequisites
- Node.js 16+ (for frontend development)
- Python 3.8+ (for backend intelligence engine)
- Modern web browser

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

The application will be available at `http://localhost:3000`

### Backend Development (Planned)
```bash
cd backend
pip install -r requirements.txt
python main.py
```

## 🚧 Current Status

### ✅ Implemented
- **Frontend UI**: Complete React application with design system
- **Dashboard**: System overview with CPU/RAM/Disk metrics
- **Process Management**: Top processes list with resource usage
- **Insights Panel**: Root cause analysis display
- **Action System**: Quick action buttons and mode toggles
- **Design Assets**: Complete UI reference mockups

### 📋 Planned Features
- Python backend intelligence engine
- Real system monitoring integration
- Safe action execution system
- Cross-platform support (Windows/Linux/macOS)
- Advanced storage analytics
- Battery optimization features

## 🛡️ Safety First

JOC is designed with safety as a core principle:

- **Never** kills system-critical processes
- **Always** requests user confirmation for impactful actions
- **Maintains** comprehensive logs of all operations
- **Includes** whitelist protection for essential system processes
- **Supports** safe mode (suggestions only, no execution)

## 🤝 Team Structure

This project is designed for a 6-person team:

1. **Core Dev 1**: Intelligence Engine & Root Cause Analysis
2. **Core Dev 2**: System Monitoring & Fix Engine
3. **Storage Specialist**: Storage Intelligence & Cleanup
4. **Frontend Dev 1**: Dashboard & Main Interface
5. **Frontend Dev 2**: UX & Interaction Design
6. **Research**: Advanced Features & Future Scope

## 📈 Future Roadmap

- Machine learning integration for predictive analysis
- Cross-platform support expansion
- Cloud sync for preferences and history
- Plugin system for custom optimizations
- Mobile companion app
- Advanced developer tools integration

## 🎯 Why JOC Matters

While many tools show system data, JOC:

1. **Understands** what the data means
2. **Explains** issues in clear language
3. **Suggests** targeted, safe solutions
4. **Executes** only with explicit permission

This combination of intelligence, clarity, and safety makes JOC feel like a true **Sentinel Engine** rather than just another monitoring tool.

## 📄 License

This project is developed for educational and demonstration purposes.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines (to be established) for more details on how to participate in development.

---

**JOC - Because your computer deserves an intelligent assistant.**