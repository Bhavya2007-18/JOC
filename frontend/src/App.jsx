import React, { useState } from 'react'
import {
  Cpu, MemoryStick, HardDrive, Activity, Shield, Zap, Battery,
  Settings, Bell, Search, AlertTriangle, CheckCircle, Clock,
  TrendingUp, XCircle, RefreshCw, Gamepad2, Gauge, BatteryCharging
} from 'lucide-react'

function App() {
  const [activeNav, setActiveNav] = useState('dashboard')
  const [selectedMode, setSelectedMode] = useState('performance')

  const cpuUsage = 67
  const ramUsage = 82
  const diskUsage = 45

  const processes = [
    { name: 'Chrome', cpu: 24.5, ram: 2.1, icon: Cpu },
    { name: 'VS Code', cpu: 12.3, ram: 1.8, icon: Activity },
    { name: 'Spotify', cpu: 8.7, ram: 0.9, icon: Activity },
    { name: 'Discord', cpu: 5.2, ram: 0.7, icon: Activity },
    { name: 'System', cpu: 3.1, ram: 4.2, icon: Shield },
  ]

  const insights = {
    cause: "High CPU usage from multiple Chrome tabs consuming 24.5% resources",
    fix: "Close unused Chrome tabs or enable Performance mode"
  }

  const modes = [
    { id: 'gaming', name: 'Gaming', icon: Gamepad2 },
    { id: 'performance', name: 'Performance', icon: Gauge },
    { id: 'battery', name: 'Battery', icon: BatteryCharging },
  ]

  const actions = [
    { name: 'Clear RAM', icon: MemoryStick, primary: true },
    { name: 'Disk Cleanup', icon: HardDrive, primary: false },
    { name: 'Restart PC', icon: RefreshCw, primary: false },
  ]

  const navItems = [
    { id: 'dashboard', icon: Activity },
    { id: 'storage', icon: HardDrive },
    { id: 'alerts', icon: Bell },
    { id: 'history', icon: Clock },
    { id: 'modes', icon: Zap },
    { id: 'settings', icon: Settings },
  ]

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="sidebar-logo">J</div>
        {navItems.map(item => (
          <div
            key={item.id}
            className={`sidebar-item ${activeNav === item.id ? 'active' : ''}`}
            onClick={() => setActiveNav(item.id)}
          >
            <item.icon size={20} />
          </div>
        ))}
      </aside>

      <main className="main-content">
        <header className="header">
          <div>
            <h1 className="header-title">System Overview</h1>
            <p className="header-subtitle">Monitoring system health and performance</p>
          </div>
          <div className="header-actions">
            <div className="status-badge">
              <div className="status-dot"></div>
              <span>System Healthy</span>
            </div>
          </div>
        </header>

        <div className="content-area">
          <div className="dashboard-grid">
            <div className="alert-banner">
              <div className="alert-icon">
                <AlertTriangle size={20} />
              </div>
              <div className="alert-content">
                <div className="alert-title">High CPU Usage Detected</div>
                <div className="alert-text">Chrome is consuming 24.5% CPU. Consider closing unused tabs.</div>
              </div>
              <button className="alert-action">Fix Now</button>
            </div>

            <div className="metrics-row">
              <div className="metric-card">
                <div className="metric-header">
                  <div className="metric-icon"><Cpu size={20} /></div>
                  <span className="metric-label">CPU</span>
                </div>
                <div className="metric-value">{cpuUsage}<span className="metric-unit">%</span></div>
                <div className="metric-bar">
                  <div className="metric-bar-fill" style={{ width: `${cpuUsage}%` }}></div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <div className="metric-icon"><MemoryStick size={20} /></div>
                  <span className="metric-label">RAM</span>
                </div>
                <div className="metric-value">{ramUsage}<span className="metric-unit">%</span></div>
                <div className="metric-bar">
                  <div className="metric-bar-fill" style={{ width: `${ramUsage}%` }}></div>
                </div>
              </div>

              <div className="metric-card">
                <div className="metric-header">
                  <div className="metric-icon"><HardDrive size={20} /></div>
                  <span className="metric-label">Disk</span>
                </div>
                <div className="metric-value">{diskUsage}<span className="metric-unit">%</span></div>
                <div className="metric-bar">
                  <div className="metric-bar-fill" style={{ width: `${diskUsage}%` }}></div>
                </div>
              </div>
            </div>

            <div className="processes-section">
              <div className="section-header">
                <h2 className="section-title">Top Processes</h2>
                <span className="section-badge">5 Active</span>
              </div>
              <div className="process-list">
                {processes.map((proc, idx) => (
                  <div key={idx} className="process-item">
                    <div className="process-icon"><proc.icon size={16} /></div>
                    <div className="process-info">
                      <div className="process-name">{proc.name}</div>
                      <div className="process-meta">{proc.ram} GB RAM</div>
                    </div>
                    <div className="process-stats">
                      <div className="process-cpu">{proc.cpu}%</div>
                      <div className="process-ram">CPU</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="modes-section">
              <div className="section-header">
                <h2 className="section-title">Operation Modes</h2>
              </div>
              <div className="modes-grid">
                {modes.map(mode => (
                  <button
                    key={mode.id}
                    className={`mode-btn ${selectedMode === mode.id ? 'active' : ''}`}
                    onClick={() => setSelectedMode(mode.id)}
                  >
                    <div className="mode-icon"><mode.icon size={20} /></div>
                    <div className="mode-name">{mode.name}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="right-panel">
            <div className="insight-card">
              <div className="insight-header">
                <div className="insight-icon"><TrendingUp size={20} /></div>
                <div>
                  <div className="insight-title">Root Cause Analysis</div>
                  <div className="insight-subtitle">Why system is slow</div>
                </div>
              </div>
              <div className="insight-content">
                <div className="insight-cause">
                  <div className="insight-cause-label">Cause</div>
                  <p>{insights.cause}</p>
                </div>
                <div className="insight-fix">
                  <CheckCircle size={16} className="insight-fix-icon" />
                  <span className="insight-fix-text">{insights.fix}</span>
                </div>
              </div>
            </div>

            <div className="actions-section">
              <div className="section-header">
                <h2 className="section-title">Quick Actions</h2>
              </div>
              <div className="actions-grid">
                {actions.map((action, idx) => (
                  <button
                    key={idx}
                    className={`action-btn ${action.primary ? 'action-btn-primary' : ''}`}
                  >
                    <span>{action.name}</span>
                    <div className="action-btn-icon">
                      <action.icon size={16} />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="insight-card">
              <div className="section-header">
                <h2 className="section-title">System Health</h2>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <CheckCircle size={16} color="#6bff8a" />
                  <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>CPU temperature normal</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <CheckCircle size={16} color="#6bff8a" />
                  <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>No malware detected</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <AlertTriangle size={16} color="#ffd93d" />
                  <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>RAM usage elevated</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <CheckCircle size={16} color="#6bff8a" />
                  <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Disk space adequate</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App