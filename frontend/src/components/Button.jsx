import { cn } from '../utils/cn';

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
    primary: 'nm-convex text-accent-blue hover:text-blue-400 active:nm-inset',
    secondary: 'nm-flat text-slate-300 hover:text-white active:nm-inset',
    danger: 'nm-convex text-red-500 hover:text-red-400 active:nm-inset',
    outline: 'nm-flat border border-slate-700 text-slate-400 hover:text-slate-200 active:nm-inset',
    ghost: 'bg-transparent text-slate-400 hover:bg-slate-800/50',
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-xs uppercase tracking-widest',
    md: 'px-6 py-2.5 text-sm font-bold uppercase tracking-wider',
    lg: 'px-8 py-4 text-base font-bold uppercase tracking-widest',
  };

  return (
    <button
      type={type}
      className={cn(
        'inline-flex items-center justify-center rounded-xl transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : null}
      {children}
    </button>
  );
}
