import React from 'react';

const backgrounds = {
  boost: BoostBg,
  flush: FlushBg,
  battle: BattleBg,
  anomaly: AnomalyBg,
};

export function ProtocolBg({ type, color = 'text-accent-blue' }) {
  const Bg = backgrounds[type];
  if (!Bg) return null;
  return (
    <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none z-0">
      <Bg color={color} />
    </div>
  );
}

function BoostBg() {
  return (
    <div className="absolute inset-0">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 rounded-full bg-amber-500/10 blur-[50px] animate-pulse" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 100" preserveAspectRatio="none">
        {[...Array(6)].map((_, i) => (
          <line
            key={i}
            x1="-20" y1={15 + i * 15} x2="10" y2={15 + i * 15}
            stroke="#f59e0b"
            strokeWidth="2"
            opacity="0.2"
          >
            <animate attributeName="x1" from="-50" to="250" dur={`${0.4 + i * 0.1}s`} repeatCount="indefinite" />
            <animate attributeName="x2" from="0" to="300" dur={`${0.4 + i * 0.1}s`} repeatCount="indefinite" />
          </line>
        ))}
        {[...Array(12)].map((_, i) => (
          <circle key={i} r="1" fill="#fbbf24" opacity="0.6">
            <animate attributeName="cx" values={`${Math.random() * 200};${Math.random() * 200}`} dur="0.1s" repeatCount="indefinite" />
            <animate attributeName="cy" values={`${Math.random() * 100};${Math.random() * 100}`} dur="0.1s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0;0.8;0" dur="0.2s" repeatCount="indefinite" />
          </circle>
        ))}
      </svg>
    </div>
  );
}

function FlushBg() {
  return (
    <div className="absolute inset-0">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 rounded-full bg-emerald-500/10 blur-[50px] animate-pulse" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 100" preserveAspectRatio="none">
        <path d="M0 50 Q 50 20, 100 50 T 200 50 L 200 100 L 0 100 Z" fill="#10b981" opacity="0.1">
          <animate attributeName="d" 
            values="M0 50 Q 50 20, 100 50 T 200 50 L 200 100 L 0 100 Z; 
                    M0 50 Q 50 80, 100 50 T 200 50 L 200 100 L 0 100 Z; 
                    M0 50 Q 50 20, 100 50 T 200 50 L 200 100 L 0 100 Z" 
            dur="4s" repeatCount="indefinite" />
        </path>
        {[...Array(10)].map((_, i) => (
          <circle key={i} cx={20 + i * 18} cy={80} r="1.5" fill="#34d399" opacity="0.3">
            <animate attributeName="cy" from="110" to="-10" dur={`${2 + Math.random() * 2}s`} repeatCount="indefinite" />
            <animate attributeName="opacity" values="0;0.4;0" dur={`${2 + Math.random() * 2}s`} repeatCount="indefinite" />
          </circle>
        ))}
        <line x1="0" y1="0" x2="200" y2="0" stroke="#10b981" strokeWidth="1" opacity="0.2">
          <animate attributeName="y1" from="0" to="100" dur="2.5s" repeatCount="indefinite" />
          <animate attributeName="y2" from="0" to="100" dur="2.5s" repeatCount="indefinite" />
        </line>
      </svg>
    </div>
  );
}

function BattleBg() {
  return (
    <div className="absolute inset-0">
      <div className="absolute inset-0 bg-red-900/5 animate-pulse" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 100" preserveAspectRatio="none">
        {[...Array(8)].map((_, i) => (
          <line
            key={i}
            x1="0" y1={i * 12.5} x2="200" y2={i * 12.5}
            stroke="#ef4444"
            strokeWidth="0.5"
            opacity="0.1"
          >
            <animate attributeName="opacity" values="0.05;0.2;0.05" dur={`${0.1 + i * 0.05}s`} repeatCount="indefinite" />
          </line>
        ))}
        <rect x="0" y="0" width="10" height="100" fill="#ef4444" opacity="0.08">
          <animate attributeName="x" from="-10" to="200" dur="1s" repeatCount="indefinite" />
        </rect>
        {[...Array(15)].map((_, i) => (
          <circle key={i} cx={Math.random() * 200} cy={Math.random() * 100} r="1" fill="#f87171" opacity="0.4">
            <animate attributeName="opacity" values="0.1;0.8;0.1" dur={`${0.2 + Math.random() * 0.4}s`} repeatCount="indefinite" />
          </circle>
        ))}
      </svg>
    </div>
  );
}

function AnomalyBg({ color }) {
  const isRed = color.includes('red');
  const isAmber = color.includes('amber');
  const strokeColor = isRed ? '#ef4444' : isAmber ? '#f59e0b' : '#10b981';

  return (
    <div className="absolute inset-0">
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 100" preserveAspectRatio="none">
        {/* Sonar Scan Beam - Pure horizontal sweep */}
        <rect x="0" y="0" width="2" height="100" fill={strokeColor} opacity="0.15">
          <animate attributeName="x" from="-5" to="205" dur="3s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.05;0.2;0.05" dur="3s" repeatCount="indefinite" />
        </rect>
        
        {/* Rhythmic Pulse from Focal Point */}
        <circle cx="20" cy="50" r="10" fill="none" stroke={strokeColor} strokeWidth="1" opacity="0.1">
          <animate attributeName="r" from="10" to="100" dur="4s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.2;0;0" dur="4s" repeatCount="indefinite" />
        </circle>
        <circle cx="20" cy="50" r="10" fill="none" stroke={strokeColor} strokeWidth="1" opacity="0.1">
          <animate attributeName="r" from="10" to="100" dur="4s" begin="2s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0.2;0;0" dur="4s" begin="2s" repeatCount="indefinite" />
        </circle>

        {/* Faint Horizontal Analysis Lines */}
        {[...Array(10)].map((_, i) => (
          <line
            key={i}
            x1="0" y1={i * 10} x2="200" y2={i * 10}
            stroke={strokeColor}
            strokeWidth="0.5"
            opacity="0.05"
          />
        ))}
      </svg>
    </div>
  );
}
