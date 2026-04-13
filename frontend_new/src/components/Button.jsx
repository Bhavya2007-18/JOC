import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';
import { cn } from '../utils/cn';

export function Button({ 
  className, 
  variant = 'primary', 
  size = 'md', 
  isLoading, 
  children, 
  type = 'button',
  onClick,
  ...props 
}) {
  const [ripples, setRipples] = useState([]);

  const createRipple = (event) => {
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;

    const newRipple = { x, y, size, id: Date.now() };
    setRipples((prev) => [...prev, newRipple]);
    
    // Cleanup ripple
    setTimeout(() => {
      setRipples((prev) => prev.filter((r) => r.id !== newRipple.id));
    }, 600);

    if (onClick) onClick(event);
  };

  const variants = {
    primary: 'bg-cyan-500/10 border border-cyan-500/30 text-[#00E5FF] hover:bg-cyan-500/20 hover:border-cyan-500/50 shadow-[0_0_15px_rgba(0,229,255,0.1)]',
    secondary: 'bg-slate-800/50 border border-slate-700 text-slate-300 hover:text-white hover:bg-slate-800',
    danger: 'bg-red-500/10 border border-red-500/30 text-[#FF3D57] hover:bg-red-500/20 hover:border-red-500/50 shadow-[0_0_15px_rgba(255,61,87,0.1)]',
    outline: 'bg-transparent border border-slate-700 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/50',
    ghost: 'bg-transparent text-slate-400 hover:text-white hover:underline decoration-cyan-500 underline-offset-4',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-[10px] tracking-widest',
    md: 'px-6 py-2.5 text-xs font-bold tracking-[0.2em]',
    lg: 'px-8 py-4 text-sm font-bold tracking-[0.3em]',
  };

  return (
    <motion.button
      type={type}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.96 }}
      disabled={isLoading}
      onClick={createRipple}
      className={cn(
        'group relative inline-flex items-center justify-center rounded-lg font-mono uppercase transition-all overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {/* Hover Shimmer Sweep */}
      <span className="absolute inset-0 block pointer-events-none overflow-hidden rounded-lg">
        <span className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 ease-in-out bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      </span>

      {/* Ripple Container */}
      <span className="absolute inset-0 pointer-events-none">
        {ripples.map((ripple) => (
          <motion.span
            key={ripple.id}
            initial={{ scale: 0, opacity: 0.5 }}
            animate={{ scale: 4, opacity: 0 }}
            transition={{ duration: 0.6 }}
            className="absolute rounded-full bg-white/20"
            style={{
              width: ripple.size,
              height: ripple.size,
              top: ripple.y,
              left: ripple.x,
            }}
          />
        ))}
      </span>

      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="loader"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            <Loader2 className="h-4 w-4 animate-spin" />
          </motion.div>
        ) : (
          <motion.span
            key="children"
            className="relative z-10 flex items-center gap-2"
          >
            {children}
          </motion.span>
        )}
      </AnimatePresence>
    </motion.button>
  );
}