import React from 'react';

const backgrounds = {
  'CPU Usage': CpuBackground,
  'Memory': MemoryBackground,
  'Disk Usage': DiskBackground,
  'Network': NetworkBackground,
};

export function StatCardBg({ type }) {
  const Bg = backgrounds[type];
  if (!Bg) return null;
  return (
    <div className="absolute inset-0 overflow-hidden rounded-3xl pointer-events-none z-0">
      <Bg />
    </div>
  );
}

function CpuBackground() {
  return (
    <div className="absolute inset-0">
      {/* Ambient glow centered near top icon */}
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full bg-blue-500/10 blur-3xl animate-pulse" />
      
      {/* Circuit board SVG - upshifted to y=50 */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 200" preserveAspectRatio="none">
        <defs>
          <linearGradient id="cpuGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="1" />
            <stop offset="100%" stopColor="#60a5fa" stopOpacity="0.5" />
          </linearGradient>
        </defs>
        {/* Grid lines */}
        <line x1="50" y1="0" x2="50" y2="200" stroke="#3b82f6" strokeWidth="0.5" opacity="0.12" />
        <line x1="100" y1="0" x2="100" y2="200" stroke="#3b82f6" strokeWidth="0.5" opacity="0.08" />
        <line x1="150" y1="0" x2="150" y2="200" stroke="#3b82f6" strokeWidth="0.5" opacity="0.12" />
        
        <line x1="0" y1="20" x2="200" y2="20" stroke="#3b82f6" strokeWidth="0.5" opacity="0.08" />
        <line x1="0" y1="90" x2="200" y2="90" stroke="#3b82f6" strokeWidth="0.5" opacity="0.08" />
        
        {/* Pulsing circuit nodes */}
        <circle cx="50" cy="20" r="4" fill="#3b82f6" opacity="0.5">
          <animate attributeName="opacity" values="0.2;0.7;0.2" dur="2s" repeatCount="indefinite" />
          <animate attributeName="r" values="3;5;3" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx="150" cy="20" r="3.5" fill="#60a5fa" opacity="0.4">
          <animate attributeName="opacity" values="0.15;0.6;0.15" dur="2.5s" repeatCount="indefinite" />
          <animate attributeName="r" values="2.5;4.5;2.5" dur="2.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="50" cy="90" r="3" fill="#60a5fa" opacity="0.35">
          <animate attributeName="opacity" values="0.2;0.55;0.2" dur="1.8s" repeatCount="indefinite" />
          <animate attributeName="r" values="2;4;2" dur="1.8s" repeatCount="indefinite" />
        </circle>
        <circle cx="150" cy="90" r="3" fill="#3b82f6" opacity="0.3">
          <animate attributeName="opacity" values="0.15;0.5;0.15" dur="3s" repeatCount="indefinite" />
          <animate attributeName="r" values="2;4;2" dur="3s" repeatCount="indefinite" />
        </circle>
        
        {/* Central chip outline - Centered cleanly around y=55 */}
        <rect x="70" y="25" width="60" height="60" rx="8" fill="none" stroke="#3b82f6" strokeWidth="1.5" opacity="0.2">
          <animate attributeName="opacity" values="0.08;0.3;0.08" dur="2s" repeatCount="indefinite" />
        </rect>
        <rect x="80" y="35" width="40" height="40" rx="4" fill="#3b82f6" opacity="0.1">
          <animate attributeName="opacity" values="0.04;0.18;0.04" dur="1.5s" repeatCount="indefinite" />
        </rect>
        
        {/* Flowing trace paths */}
        <path d="M50 20 L70 20 L70 35" fill="none" stroke="#3b82f6" strokeWidth="1.5" opacity="0.25" strokeDasharray="6 4">
          <animate attributeName="stroke-dashoffset" from="40" to="0" dur="2s" repeatCount="indefinite" />
        </path>
        <path d="M150 20 L130 20 L130 35" fill="none" stroke="#60a5fa" strokeWidth="1.5" opacity="0.2" strokeDasharray="6 4">
          <animate attributeName="stroke-dashoffset" from="40" to="0" dur="2.5s" repeatCount="indefinite" />
        </path>
        <path d="M100 85 L100 90 L50 90" fill="none" stroke="#3b82f6" strokeWidth="1" opacity="0.2" strokeDasharray="4 4">
          <animate attributeName="stroke-dashoffset" from="50" to="0" dur="3s" repeatCount="indefinite" />
        </path>
        <path d="M100 85 L100 90 L150 90" fill="none" stroke="#60a5fa" strokeWidth="1" opacity="0.15" strokeDasharray="4 4">
          <animate attributeName="stroke-dashoffset" from="50" to="0" dur="3.5s" repeatCount="indefinite" />
        </path>
      </svg>
    </div>
  );
}

function MemoryBackground() {
  return (
    <div className="absolute inset-0">
      {/* Ambient glow centered near top icon */}
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full bg-purple-500/10 blur-3xl animate-pulse" />
      
      {/* RAM equalizer bars - Shifted up */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 200" preserveAspectRatio="none">
        <defs>
          <linearGradient id="memGrad" x1="0%" y1="100%" x2="0%" y2="0%">
            <stop offset="0%" stopColor="#a855f7" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#c084fc" stopOpacity="0.1" />
          </linearGradient>
        </defs>
        
        {/* Animated equalizer bars (behind/around icon) */}
        {[20, 38, 56, 74, 92, 110, 128, 146, 164, 182].map((x, i) => (
          <rect key={i} x={x - 6} y={15} width="10" rx="3" fill="url(#memGrad)" opacity="0.25">
            <animate
              attributeName="height"
              values={`${30 + i * 4};${70 + i * 3};${30 + i * 4}`}
              dur={`${1.2 + i * 0.15}s`}
              repeatCount="indefinite"
            />
            {/* Keeping y fixed so they grow downwards, looking like descending scanlines, or fix y so they are centered? Let's grow them upwards */}
            <animate
              attributeName="y"
              values={`${90 - (30 + i * 4)};${90 - (70 + i * 3)};${90 - (30 + i * 4)}`}
              dur={`${1.2 + i * 0.15}s`}
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.15;0.35;0.15"
              dur={`${1.2 + i * 0.15}s`}
              repeatCount="indefinite"
            />
          </rect>
        ))}
        {/* Data bus lines flowing horizontally behind the icon */}
        <line x1="0" y1="20" x2="200" y2="20" stroke="#a855f7" strokeWidth="1" opacity="0.15" strokeDasharray="10 5">
          <animate attributeName="stroke-dashoffset" from="0" to="-30" dur="1.5s" repeatCount="indefinite" />
        </line>
        <line x1="0" y1="40" x2="200" y2="40" stroke="#c084fc" strokeWidth="0.8" opacity="0.1" strokeDasharray="6 8">
          <animate attributeName="stroke-dashoffset" from="0" to="28" dur="2s" repeatCount="indefinite" />
        </line>
      </svg>
    </div>
  );
}

function DiskBackground() {
  return (
    <div className="absolute inset-0">
      {/* Ambient glow centered near top icon */}
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full bg-emerald-500/10 blur-3xl animate-pulse" />
      
      {/* Spinning disk rings - centered at y=55 */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 200" preserveAspectRatio="none">
        <defs>
          <linearGradient id="diskGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#34d399" stopOpacity="0.3" />
          </linearGradient>
        </defs>
        {/* Outer ring */}
        <circle cx="100" cy="55" r="55" fill="none" stroke="url(#diskGrad)" strokeWidth="1" opacity="0.2" strokeDasharray="12 8">
          <animateTransform attributeName="transform" type="rotate" from="0 100 55" to="360 100 55" dur="15s" repeatCount="indefinite" />
        </circle>
        {/* Middle ring - counter-rotate */}
        <circle cx="100" cy="55" r="40" fill="none" stroke="#10b981" strokeWidth="0.8" opacity="0.2" strokeDasharray="8 12">
          <animateTransform attributeName="transform" type="rotate" from="360 100 55" to="0 100 55" dur="12s" repeatCount="indefinite" />
        </circle>
        {/* Inner ring */}
        <circle cx="100" cy="55" r="25" fill="none" stroke="#34d399" strokeWidth="0.8" opacity="0.18" strokeDasharray="5 10">
          <animateTransform attributeName="transform" type="rotate" from="0 100 55" to="360 100 55" dur="8s" repeatCount="indefinite" />
        </circle>
        {/* Center hub */}
        <circle cx="100" cy="55" r="8" fill="none" stroke="#10b981" strokeWidth="1.5" opacity="0.25">
          <animate attributeName="opacity" values="0.15;0.35;0.15" dur="2s" repeatCount="indefinite" />
        </circle>
        
        {/* Read/write sweeping arm */}
        <line x1="100" y1="55" x2="100" y2="0" stroke="#34d399" strokeWidth="1.5" opacity="0.18">
          <animateTransform attributeName="transform" type="rotate" from="0 100 55" to="360 100 55" dur="3s" repeatCount="indefinite" />
        </line>
      </svg>
    </div>
  );
}

function NetworkBackground() {
  return (
    <div className="absolute inset-0">
      {/* Ambient glow centered near top icon */}
      <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-40 h-40 rounded-full bg-cyan-500/10 blur-3xl animate-pulse" />
      
      {/* Network topology - centered around y=55 */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 200" preserveAspectRatio="none">
        <defs>
          <linearGradient id="netGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.3" />
          </linearGradient>
        </defs>
        
        {/* Connection lines pulsing */}
        <line x1="40" y1="20" x2="100" y2="55" stroke="#06b6d4" strokeWidth="1" opacity="0.2">
          <animate attributeName="opacity" values="0.08;0.3;0.08" dur="2s" repeatCount="indefinite" />
        </line>
        <line x1="160" y1="20" x2="100" y2="55" stroke="#22d3ee" strokeWidth="1" opacity="0.2">
          <animate attributeName="opacity" values="0.1;0.35;0.1" dur="2.5s" repeatCount="indefinite" />
        </line>
        <line x1="40" y1="90" x2="100" y2="55" stroke="#06b6d4" strokeWidth="0.8" opacity="0.15">
          <animate attributeName="opacity" values="0.08;0.25;0.08" dur="3s" repeatCount="indefinite" />
        </line>
        <line x1="160" y1="90" x2="100" y2="55" stroke="#22d3ee" strokeWidth="0.8" opacity="0.15">
          <animate attributeName="opacity" values="0.1;0.28;0.1" dur="1.8s" repeatCount="indefinite" />
        </line>
        
        {/* Cross connections */}
        <line x1="40" y1="20" x2="160" y2="20" stroke="#06b6d4" strokeWidth="0.5" opacity="0.1" strokeDasharray="4 6">
          <animate attributeName="stroke-dashoffset" from="0" to="-20" dur="3s" repeatCount="indefinite" />
        </line>
        <line x1="40" y1="90" x2="160" y2="90" stroke="#22d3ee" strokeWidth="0.5" opacity="0.08" strokeDasharray="4 6">
          <animate attributeName="stroke-dashoffset" from="0" to="20" dur="3.5s" repeatCount="indefinite" />
        </line>
        
        {/* Data packets traveling */}
        <circle r="3" fill="#06b6d4" opacity="0.6">
          <animateMotion dur="2s" repeatCount="indefinite" path="M40,20 L100,55" />
          <animate attributeName="opacity" values="0;0.6;0" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle r="3" fill="#22d3ee" opacity="0.5">
          <animateMotion dur="2.5s" repeatCount="indefinite" path="M100,55 L160,20" />
          <animate attributeName="opacity" values="0;0.5;0" dur="2.5s" repeatCount="indefinite" />
        </circle>
        <circle r="2.5" fill="#06b6d4" opacity="0.5">
          <animateMotion dur="3s" repeatCount="indefinite" path="M40,90 L100,55" />
          <animate attributeName="opacity" values="0;0.5;0" dur="3s" repeatCount="indefinite" />
        </circle>
        
        {/* Pulsing nodes */}
        <circle cx="40" cy="20" r="6" fill="none" stroke="#06b6d4" strokeWidth="1.5" opacity="0.3">
          <animate attributeName="r" values="5;8;5" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx="160" cy="20" r="5" fill="none" stroke="#22d3ee" strokeWidth="1.5" opacity="0.25">
          <animate attributeName="r" values="4;7;4" dur="2.5s" repeatCount="indefinite" />
        </circle>
        <circle cx="40" cy="90" r="5" fill="none" stroke="#06b6d4" strokeWidth="1" opacity="0.2">
          <animate attributeName="r" values="4;7;4" dur="3s" repeatCount="indefinite" />
        </circle>
        <circle cx="160" cy="90" r="5" fill="none" stroke="#22d3ee" strokeWidth="1" opacity="0.2">
          <animate attributeName="r" values="4;7;4" dur="1.8s" repeatCount="indefinite" />
        </circle>
        
        {/* Central hub */}
        <circle cx="100" cy="55" r="12" fill="none" stroke="#06b6d4" strokeWidth="2" opacity="0.2">
          <animate attributeName="opacity" values="0.1;0.4;0.1" dur="1.5s" repeatCount="indefinite" />
          <animate attributeName="r" values="10;14;10" dur="1.5s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  );
}
