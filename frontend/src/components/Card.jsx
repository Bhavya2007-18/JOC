import { cn } from '../utils/cn';

export function Card({ className, title, description, children, footer }) {
  return (
    <div className={cn('overflow-hidden rounded-xl border border-gray-200 bg-white shadow-sm transition-all hover:shadow-md', className)}>
      {(title || description) && (
        <div className="border-b border-gray-100 px-6 py-4">
          {title && <h3 className="text-lg font-semibold text-gray-900">{title}</h3>}
          {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
        </div>
      )}
      <div className="px-6 py-4">{children}</div>
      {footer && <div className="border-t border-gray-100 bg-gray-50/50 px-6 py-3">{footer}</div>}
    </div>
  );
}
