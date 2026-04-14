import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { cn } from '../utils/cn';

export function Card({ 
  className, 
  title, 
  description, 
  icon: Icon, 
  children, 
  footer,
  badge,
  collapsible = false,
  glowColor = 'cyan' // options: cyan, amber, red, purple
}) {
  const [isOpen, setIsOpen] = useState(true);

  const glowStyles = {
    cyan: 'group-hover:border-t-[#00E5FF] group-hover:shadow-[0_-10px_20px_-10px_rgba(0,229,255,0.3)]',
    amber: 'group-hover:border-t-[#FFB300] group-hover:shadow-[0_-10px_20px_-10px_rgba(255,179,0,0.3)]',
    red: 'group-hover:border-t-[#FF3D57] group-hover:shadow-[0_-10px_20px_-10px_rgba(255,61,87,0.3)]',
    purple: 'group-hover:border-t-[#BF5FFF] group-hover:shadow-[0_-10px_20px_-10px_rgba(191,95,255,0.3)]',
  };

  return (
    <motion.div 
      initial={false}
      className={cn(
        'group relative rounded-xl border border-white/5 bg-[#0A0D14]/80 backdrop-blur-md transition-all duration-300',
        'border-t-2 border-t-transparent',
        glowStyles[glowColor],
        className
      )}
    >
      <div className="p-6">
        {(title || description || Icon) && (
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex items-center gap-4">
              {Icon && (
                <div className="p-2.5 rounded-lg bg-black/40 border border-white/5 flex items-center justify-center">
                  <Icon className="h-5 w-5 text-[#00E5FF]" />
                </div>
              )}
              <div>
                <div className="flex items-center gap-3">
                  {title && <h3 className="text-sm font-heading font-extrabold text-white uppercase tracking-wider">{title}</h3>}
                  {badge && (
                    <span className="px-2 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-[9px] font-mono font-bold text-[#00E5FF] uppercase">
                      {badge}
                    </span>
                  )}
                </div>
                {description && <p className="text-[10px] font-mono text-slate-500 uppercase tracking-tight mt-0.5">{description}</p>}
              </div>
            </div>

            {collapsible && (
              <button 
                onClick={() => setIsOpen(!isOpen)}
                className="p-1 hover:bg-white/5 rounded transition-colors"
              >
                <motion.div animate={{ rotate: isOpen ? 0 : -90 }}>
                  <ChevronDown className="h-4 w-4 text-slate-500" />
                </motion.div>
              </button>
            )}
          </div>
        )}

        <AnimatePresence initial={false}>
          {isOpen && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="text-slate-300 font-mono text-xs leading-relaxed">
                {children}
              </div>
              
              {footer && (
                <div className="mt-6 pt-4 border-t border-white/5">
                  {footer}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}