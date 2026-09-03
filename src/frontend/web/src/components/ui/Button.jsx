import React, { forwardRef } from 'react';
import { LoaderCircle } from 'lucide-react';
import { cn } from './utils';

const variants = {
  primary: 'border-transparent bg-primary text-white hover:bg-primary-hover',
  action: 'border-transparent bg-action text-white hover:bg-action-hover',
  secondary: 'border-border bg-surface text-ink hover:border-slate-300 hover:bg-stone-50',
  ghost: 'border-transparent bg-transparent text-ink hover:bg-stone-100',
  danger: 'border-transparent bg-error text-white hover:bg-red-800',
  link: 'min-h-0 border-transparent bg-transparent p-0 text-primary shadow-none hover:text-primary-hover hover:underline',
};

const sizes = {
  sm: 'min-h-11 px-3 text-sm sm:min-h-9 sm:text-xs',
  md: 'min-h-11 px-4 text-sm',
  lg: 'min-h-12 px-5 text-sm',
  icon: 'size-11 p-0',
};

export const Button = forwardRef(function Button(
  { className, variant = 'primary', size = 'md', loading = false, loadingLabel = 'Chargement…', children, disabled, type = 'button', ...props },
  ref,
) {
  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-control border font-bold shadow-subtle transition-colors duration-180 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-55',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    >
      {loading && <LoaderCircle aria-hidden="true" className="size-4 animate-spin" />}
      {loading ? <span>{loadingLabel}</span> : children}
    </button>
  );
});
