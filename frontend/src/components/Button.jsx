import { motion } from 'framer-motion';
import { cn } from '../utils/cn';

const springConfig = {
  type: "spring",
  stiffness: 500,
  damping: 30,
  mass: 1
};

export function Button({ 
  className, 
  variant = 'primary', 
  size = 'md', 
  isLoading, 
  children, 
  type = 'button',
  ...props 
}) {
  const variants = {
    primary: 'nm-convex text-accent-blue hover:text-blue-400',
    secondary: 'nm-flat text-slate-300 hover:text-white',
    danger: 'nm-convex text-red-500 hover:text-red-400',
    outline: 'nm-flat border border-slate-700 text-slate-400 hover:text-slate-200',
    ghost: 'bg-transparent text-slate-400 hover:bg-slate-800/50',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs uppercase tracking-widest',
    md: 'px-6 py-2.5 text-sm font-bold uppercase tracking-wider',
    lg: 'px-8 py-4 text-base font-bold uppercase tracking-widest',
  };

  return (
    <motion.button
      type={type}
      whileHover={{ scale: 1.02, transition: springConfig }}
      whileTap={{ scale: 0.96 }}
      className={cn(
        'inline-flex items-center justify-center rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className,
        // Swap to inset shadow on tap via simple tailwind class since motion can't easily animate complex box-shadows without lag
        'active:nm-inset'
      )}
      disabled={isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : null}
      {children}
    </motion.button>
  );
}
