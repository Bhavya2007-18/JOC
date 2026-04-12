import React from 'react';

/**
 * A highly reusable glassmorphic container that responds
 * structurally to CSS mode filtering and adds soft drop shadows.
 */
export function GlassPanel({ children, className = '', title, accentColor = 'cyan', hoverEffect = false }) {
  return (
    <div className={`glass-card rounded-2xl relative overflow-hidden transition-all duration-300 ${hoverEffect ? 'glass-card-hover' : ''} ${className}`}>
      {/* Decorative accent glow embedded inside card depth */}
      <div 
        className="absolute -top-[50px] -right-[50px] w-[150px] h-[150px] blur-[60px] rounded-full pointer-events-none opacity-20 mix-blend-screen transition-opacity duration-1000"
        style={{ backgroundColor: `var(--color-accent-${accentColor})` }}
      />
      
      {title && (
        <div className="px-6 pt-5 pb-3 border-b border-white/5 bg-slate-900/30">
            <h3 className="font-semibold text-lg text-slate-100 flex items-center tracking-wide uppercase text-xs opacity-80">
            <span 
                className="w-[6px] h-[6px] rounded-full mr-3 shadow-md" 
                style={{ backgroundColor: `var(--color-accent-${accentColor})`, boxShadow: `0 0 10px var(--color-accent-${accentColor})` }}
            />
            {title}
            </h3>
        </div>
      )}
      
      <div className="relative z-10 w-full h-full p-6">
        {children}
      </div>
    </div>
  );
}
