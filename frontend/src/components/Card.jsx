import { motion } from 'framer-motion';
import { cn } from '../utils/cn';

const springConfig = {
  type: "spring",
  stiffness: 400,
  damping: 25,
};

export function Card({ className, title, description, icon: Icon, children, footer }) {
  return (
    <motion.div 
      whileHover={{ scale: 1.01, y: -2 }}
      whileTap={{ scale: 0.99 }}
      transition={springConfig}
      className={cn('nm-flat rounded-3xl p-1 transition-shadow', className)}
    >
      <div className="h-full w-full rounded-[calc(1.5rem-4px)] p-6 bg-slate-800">
        {(title || description || Icon) && (
          <div className="flex items-center gap-4 mb-6">
            {Icon && (
              <div className="nm-inset p-3 rounded-2xl flex items-center justify-center">
                <Icon className="h-6 w-6 text-accent-blue" />
              </div>
            )}
            <div>
              {title && <h3 className="text-xl font-bold text-white tracking-tight">{title}</h3>}
              {description && <p className="text-sm text-slate-400">{description}</p>}
            </div>
          </div>
        )}
        <div className="text-slate-200">{children}</div>
        {footer && (
          <div className="mt-6 pt-6 border-t border-slate-700/50">
            {footer}
          </div>
        )}
      </div>
    </motion.div>
  );
}
