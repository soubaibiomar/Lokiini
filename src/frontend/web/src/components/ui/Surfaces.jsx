import React, { forwardRef } from 'react';
import { cn, initials } from './utils';

const badgeVariants = {
  neutral: 'border-border bg-stone-100 text-slate-700',
  primary: 'border-primary/20 bg-primary-subtle text-primary-hover',
  action: 'border-action/20 bg-action-subtle text-action-hover',
  success: 'border-success/20 bg-success-subtle text-success',
  warning: 'border-warning/20 bg-warning-subtle text-warning',
  error: 'border-error/20 bg-error-subtle text-error',
  info: 'border-info/20 bg-info-subtle text-info',
};

export function Badge({ children, variant = 'neutral', icon: Icon, className }) {
  return (
    <span className={cn('inline-flex max-w-full items-center gap-1 rounded-full border px-2.5 py-1 text-[11px] font-bold leading-none', badgeVariants[variant], className)}>
      {Icon && <Icon aria-hidden="true" className="size-3 shrink-0" />}
      <span className="truncate">{children}</span>
    </span>
  );
}

export function Avatar({ src, alt = '', name, size = 'md', status, className }) {
  const sizes = { sm: 'size-8 text-xs', md: 'size-10 text-sm', lg: 'size-14 text-lg' };
  return (
    <span className={cn('relative inline-flex shrink-0', className)}>
      <span className={cn('inline-flex items-center justify-center overflow-hidden rounded-full bg-primary-subtle font-bold text-primary', sizes[size])}>
        {src
          ? <img src={src} alt={alt || name || ''} className="size-full object-cover" />
          : <span role={name ? 'img' : undefined} aria-label={name || undefined}><span aria-hidden="true">{initials(name)}</span></span>}
      </span>
      {status && <span role="img" className={cn('absolute bottom-0 end-0 size-3 rounded-full border-2 border-white', status === 'online' ? 'bg-success' : 'bg-slate-400')} aria-label={status === 'online' ? 'En ligne' : 'Hors ligne'} />}
    </span>
  );
}

export const Card = forwardRef(function Card({ as: Component = 'div', interactive = false, className, children, ...props }, ref) {
  return (
    <Component
      ref={ref}
      className={cn('rounded-card border border-border bg-surface shadow-subtle', interactive && 'transition duration-180 hover:-translate-y-0.5 hover:border-primary/25 hover:shadow-card', className)}
      {...props}
    >
      {children}
    </Component>
  );
});

export function CardHeader({ className, children }) {
  return <div className={cn('p-5 pb-3', className)}>{children}</div>;
}

export function CardContent({ className, children }) {
  return <div className={cn('p-5 pt-2', className)}>{children}</div>;
}

export function CardFooter({ className, children }) {
  return <div className={cn('flex items-center gap-3 border-t border-border p-5', className)}>{children}</div>;
}
