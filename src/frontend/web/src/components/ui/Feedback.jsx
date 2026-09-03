import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle2, Info, Inbox, TriangleAlert, X } from 'lucide-react';
import { createPortal } from 'react-dom';
import { cn } from './utils';
import { Button } from './Button';

const toastStyles = {
  success: { icon: CheckCircle2, className: 'border-success/25 bg-success-subtle text-success' },
  warning: { icon: TriangleAlert, className: 'border-warning/25 bg-warning-subtle text-warning' },
  error: { icon: AlertCircle, className: 'border-error/25 bg-error-subtle text-error' },
  info: { icon: Info, className: 'border-info/25 bg-info-subtle text-info' },
};

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const dismiss = useCallback((id) => setToasts((current) => current.filter((toast) => toast.id !== id)), []);
  const toast = useCallback(({ title, description, variant = 'info', duration = 5000 }) => {
    const id = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random()}`;
    setToasts((current) => [...current, { id, title, description, variant }]);
    if (duration > 0) globalThis.setTimeout(() => dismiss(id), duration);
    return id;
  }, [dismiss]);
  const value = useMemo(() => ({ toast, dismiss }), [toast, dismiss]);
  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismiss} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error('useToast must be used inside ToastProvider');
  return context;
}

function ToastViewport({ toasts, onDismiss }) {
  if (!toasts.length) return null;
  return createPortal(
    <div className="pointer-events-none fixed inset-x-4 bottom-4 z-[70] flex flex-col items-end gap-3 sm:start-auto sm:w-96" aria-live="polite" aria-atomic="false">
      {toasts.map((toast) => {
        const style = toastStyles[toast.variant] || toastStyles.info;
        const Icon = style.icon;
        return (
          <div key={toast.id} role={toast.variant === 'error' ? 'alert' : 'status'} className={cn('pointer-events-auto flex w-full items-start gap-3 rounded-card border p-4 shadow-raised', style.className)}>
            <Icon aria-hidden="true" className="mt-0.5 size-5 shrink-0" />
            <div className="min-w-0 flex-1">
              <p className="text-sm font-bold text-ink">{toast.title}</p>
              {toast.description && <p className="mt-1 text-xs leading-5 text-muted">{toast.description}</p>}
            </div>
            <button type="button" onClick={() => onDismiss(toast.id)} className="flex size-10 shrink-0 items-center justify-center rounded text-muted hover:bg-black/5 hover:text-ink focus-visible:ring-2 focus-visible:ring-primary/30" aria-label="Fermer la notification">
              <X aria-hidden="true" className="size-4" />
            </button>
          </div>
        );
      })}
    </div>,
    document.body,
  );
}

export function Skeleton({ className, ...props }) {
  return <div aria-hidden="true" className={cn('animate-pulse rounded-lg bg-stone-200', className)} {...props} />;
}

function StatePanel({ icon: Icon, title, description, action, tone = 'neutral', className, role }) {
  const toneClass = tone === 'error' ? 'bg-error-subtle text-error' : 'bg-stone-100 text-muted';
  return (
    <div role={role} className={cn('mx-auto flex max-w-lg flex-col items-center px-5 py-14 text-center', className)}>
      <span className={cn('mb-4 flex size-14 items-center justify-center rounded-full', toneClass)}>
        <Icon aria-hidden="true" className="size-7" />
      </span>
      <h3 className="text-lg font-bold text-ink">{title}</h3>
      {description && <p className="mt-2 max-w-md text-sm leading-6 text-muted">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function EmptyState({ icon = Inbox, title, description, action, className }) {
  return <StatePanel icon={icon} title={title} description={description} action={action} className={className} />;
}

export function ErrorState({ title = 'Impossible de charger ce contenu', description, onRetry, retryLabel = 'Réessayer', action, className }) {
  return <StatePanel role="alert" tone="error" icon={AlertCircle} title={title} description={description} action={action || (onRetry && <Button variant="secondary" onClick={onRetry}>{retryLabel}</Button>)} className={className} />;
}
