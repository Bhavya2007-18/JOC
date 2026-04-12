import React from 'react';

const backgrounds = {
  chill: ChillBg,
  smart: SmartBg,
  beast: BeastBg,
};

export function ModeCardBg({ type }) {
  const Bg = backgrounds[type];
  if (!Bg) return null;
  return (
    <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none z-0">
      <Bg />
    </div>
  );
}

function ChillBg() {
  return (
    <div className="absolute inset-0">
      <div className="absolute top-1/2 left-1/4 w-32 h-32 rounded-full bg-blue-500/10 blur-[40px] animate-pulse" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
        {/* Soft floating particles */}
        {[...Array(5)].map((_, i) => (
          <circle key={i} cx={20 + i * 80} cy={50} r={10 + i * 2} fill="#3b82f6" opacity="0.1">
            <animate attributeName="cy" values="40;60;40" dur={`${3 + i}s`} repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.05;0.15;0.05" dur={`${4 + i}s`} repeatCount="indefinite" />
          </circle>
        ))}
        {/* Gentle drifting waves */}
        <path d="M0 50 Q 100 30, 200 50 T 400 50" fill="none" stroke="#3b82f6" strokeWidth="1" opacity="0.15">
          <animate attributeName="d" values="M0 50 Q 100 30, 200 50 T 400 50; M0 50 Q 100 70, 200 50 T 400 50; M0 50 Q 100 30, 200 50 T 400 50" dur="8s" repeatCount="indefinite" />
        </path>
      </svg>
    </div>
  );
}

function SmartBg() {
  return (
    <div className="absolute inset-0">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-40 h-40 rounded-full bg-purple-500/10 blur-[50px] animate-pulse" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
        {/* Neural paths */}
        <path d="M50 20 L100 50 L50 80 M350 20 L300 50 L350 80" fill="none" stroke="#a855f7" strokeWidth="1" opacity="0.2" />
        <circle cx="100" cy="50" r="3" fill="#a855f7" opacity="0.4">
          <animate attributeName="opacity" values="0.2;0.6;0.2" dur="2s" repeatCount="indefinite" />
        </circle>
        <circle cx="300" cy="50" r="3" fill="#a855f7" opacity="0.4">
          <animate attributeName="opacity" values="0.2;0.6;0.2" dur="2.5s" repeatCount="indefinite" />
        </circle>
        {/* Data pulse line */}
        <line x1="100" y1="50" x2="300" y2="50" stroke="#a855f7" strokeWidth="0.5" opacity="0.1" strokeDasharray="5,10">
          <animate attributeName="stroke-dashoffset" from="0" to="-30" dur="3s" repeatCount="indefinite" />
        </line>
        {/* Connection webs */}
        <path d="M100 50 L150 20 M100 50 L150 80 M300 50 L250 20 M300 50 L250 80" fill="none" stroke="#a855f7" strokeWidth="0.5" opacity="0.1" />
      </svg>
    </div>
  );
}

function BeastBg() {
  return (
    <div className="absolute inset-0">
      <div className="absolute bottom-0 right-0 w-48 h-48 rounded-full bg-amber-500/11 blur-[60px] animate-pulse" />
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 100" preserveAspectRatio="none">
        {/* Sharp energy arcs */}
        <path d="M10 80 L60 20 L110 90 L160 10 L210 80 L260 20 L310 90 L360 10" fill="none" stroke="#f59e0b" strokeWidth="1.5" opacity="0.2">
          <animate attributeName="opacity" values="0.1;0.4;0.1" dur="0.5s" repeatCount="indefinite" />
        </path>
        {/* Fast scan lines */}
        {[...Array(3)].map((_, i) => (
          <line key={i} x1="0" y1={30 + i * 20} x2="400" y2={30 + i * 20} stroke="#f59e0b" strokeWidth="0.5" opacity="0.1">
            <animate attributeName="x1" values="-400;400" dur={`${0.8 + i * 0.2}s`} repeatCount="indefinite" />
            <animate attributeName="x2" values="0;800" dur={`${0.8 + i * 0.2}s`} repeatCount="indefinite" />
          </line>
        ))}
        {/* Flickering sparks */}
        {[...Array(8)].map((_, i) => (
          <circle key={i} cx={Math.random() * 400} cy={Math.random() * 100} r="1" fill="#fbbf24" opacity="0.6">
            <animate attributeName="opacity" values="0;0.8;0" dur={`${0.2 + Math.random() * 0.3}s`} repeatCount="indefinite" />
          </circle>
        ))}
      </svg>
    </div>
  );
}
