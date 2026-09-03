import React, { cloneElement, useEffect, useId, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { ChevronDown, X } from 'lucide-react';
import { cn } from './utils';
import { Button } from './Button';
import { useI18n } from '../../i18n';

const FOCUSABLE_SELECTOR = 'button:not([disabled]), [href], input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function useDialogLayer(open, onClose, panelRef) {
  const closeRef = useRef(onClose);
  useEffect(() => { closeRef.current = onClose; }, [onClose]);
  useEffect(() => {
    if (!open) return undefined;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const previouslyFocused = document.activeElement;
    const focusableElements = () => Array.from(panelRef.current?.querySelectorAll(FOCUSABLE_SELECTOR) || [])
      .filter((element) => element.getClientRects().length > 0 && element.getAttribute('aria-hidden') !== 'true');
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        closeRef.current?.();
        return;
      }
      if (event.key !== 'Tab' || !panelRef.current) return;
      const focusable = focusableElements();
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    requestAnimationFrame(() => {
      const preferred = panelRef.current?.querySelector('[data-autofocus]');
      (preferred && preferred.getClientRects().length > 0 ? preferred : focusableElements()[0] || panelRef.current)?.focus?.();
    });
    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener('keydown', handleKeyDown);
      if (previouslyFocused?.isConnected) previouslyFocused.focus?.();
    };
  }, [open, panelRef]);
}

const modalSizes = { sm: 'max-w-md', md: 'max-w-xl', lg: 'max-w-3xl', xl: 'max-w-5xl' };

export function Modal({ open, onClose, title, description, children, footer, size = 'md', closeLabel = 'Fermer', className }) {
  const { t } = useI18n();
  const panelRef = useRef(null);
  const titleId = useId();
  const descriptionId = useId();
  useDialogLayer(open, onClose, panelRef);
  if (!open) return null;
  return createPortal(
    <div className="fixed inset-0 z-50 flex items-end justify-center overflow-hidden bg-slate-950/60 sm:items-center sm:overflow-y-auto sm:p-4" onMouseDown={(event) => event.target === event.currentTarget && onClose?.()}>
      <section
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? titleId : undefined}
        aria-describedby={description ? descriptionId : undefined}
        className={cn('flex max-h-[calc(100dvh-env(safe-area-inset-top))] w-full flex-col overflow-hidden rounded-t-modal border-x-0 border-b-0 border-t border-border bg-surface shadow-raised sm:my-8 sm:max-h-[calc(100vh-2rem)] sm:rounded-modal sm:border', modalSizes[size], className)}
      >
        {(title || description) && (
          <header className="shrink-0 flex items-start justify-between gap-4 border-b border-border px-4 py-4 sm:px-6">
            <div>
              {title && <h2 id={titleId} className="text-xl font-bold text-ink">{title}</h2>}
              {description && <p id={descriptionId} className="mt-1 text-sm leading-6 text-muted">{description}</p>}
            </div>
            <Button data-autofocus variant="ghost" size="icon" className="-me-2 -mt-2 size-11" onClick={onClose} aria-label={closeLabel === 'Fermer' ? t('modal.closeAria') : closeLabel}>
              <X aria-hidden="true" className="size-5" />
            </Button>
          </header>
        )}
        <div className="min-h-0 flex-1 overflow-y-auto p-4 sm:p-6">{children}</div>
        {footer && <footer className="shrink-0 flex flex-col-reverse gap-3 border-t border-border bg-surface px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-4 sm:flex-row sm:justify-end sm:px-6 sm:pb-4">{footer}</footer>}
      </section>
    </div>,
    document.body,
  );
}

export function Drawer({ open, onClose, title, description, children, footer, side = 'right', className }) {
  const { t } = useI18n();
  const panelRef = useRef(null);
  const titleId = useId();
  const descriptionId = useId();
  useDialogLayer(open, onClose, panelRef);
  if (!open) return null;
  const position = side === 'left' ? 'sm:start-0' : 'sm:end-0';
  return createPortal(
    <div className="fixed inset-0 z-50 bg-slate-950/60" onMouseDown={(event) => event.target === event.currentTarget && onClose?.()}>
      <aside ref={panelRef} role="dialog" aria-modal="true" aria-labelledby={titleId} aria-describedby={description ? descriptionId : undefined} className={cn('absolute inset-x-0 bottom-0 flex max-h-[88dvh] w-full flex-col rounded-t-modal border-t border-border bg-surface shadow-raised sm:inset-y-0 sm:max-h-none sm:max-w-md sm:rounded-none', position, side === 'left' ? 'sm:border-e' : 'sm:border-s', className)}>
        <header className="shrink-0 flex items-start justify-between gap-4 border-b border-border p-4 sm:p-5">
          <div>
            <h2 id={titleId} className="text-lg font-bold text-ink">{title}</h2>
            {description && <p id={descriptionId} className="mt-1 text-sm text-muted">{description}</p>}
          </div>
          <Button data-autofocus variant="ghost" size="icon" className="-me-2 -mt-2 size-11" onClick={onClose} aria-label={t('modal.closeAria')}>
            <X aria-hidden="true" className="size-5" />
          </Button>
        </header>
        <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain p-4 sm:p-5">{children}</div>
        {footer && <footer className="shrink-0 border-t border-border bg-surface px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-4 sm:p-5">{footer}</footer>}
      </aside>
    </div>,
    document.body,
  );
}

export function Dropdown({ trigger, children, align = 'start', className, label = 'Ouvrir le menu' }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const rootRef = useRef(null);
  const menuId = useId();
  useEffect(() => {
    if (!open) return undefined;
    const dismiss = (event) => !rootRef.current?.contains(event.target) && setOpen(false);
    const escape = (event) => event.key === 'Escape' && setOpen(false);
    document.addEventListener('pointerdown', dismiss);
    document.addEventListener('keydown', escape);
    return () => {
      document.removeEventListener('pointerdown', dismiss);
      document.removeEventListener('keydown', escape);
    };
  }, [open]);
  useEffect(() => {
    if (!open) return undefined;
    const frame = requestAnimationFrame(() => rootRef.current?.querySelector('[role="menuitem"]')?.focus());
    return () => cancelAnimationFrame(frame);
  }, [open]);
  const handleMenuKeyDown = (event) => {
    const items = Array.from(event.currentTarget.querySelectorAll('[role="menuitem"]:not([disabled])'));
    const current = items.indexOf(document.activeElement);
    if (event.key === 'Escape') {
      event.preventDefault();
      setOpen(false);
      requestAnimationFrame(() => rootRef.current?.querySelector('[aria-haspopup="menu"]')?.focus());
      return;
    }
    if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key) || !items.length) return;
    event.preventDefault();
    const next = event.key === 'Home' ? 0
      : event.key === 'End' ? items.length - 1
        : event.key === 'ArrowDown' ? (current + 1 + items.length) % items.length
          : (current - 1 + items.length) % items.length;
    items[next].focus();
  };
  const triggerElement = trigger || <Button variant="secondary">Menu <ChevronDown className="size-4" /></Button>;
  return (
    <div ref={rootRef} className="relative inline-flex">
      {cloneElement(triggerElement, {
        'aria-haspopup': 'menu',
        'aria-expanded': open,
        'aria-controls': menuId,
        'aria-label': triggerElement.props['aria-label'] || (label === 'Ouvrir le menu' ? t('modal.openMenu') : label),
        onClick: (event) => {
          triggerElement.props.onClick?.(event);
          setOpen((value) => !value);
        },
      })}
      {open && (
        <div id={menuId} role="menu" aria-label={label === 'Ouvrir le menu' ? t('modal.openMenu') : label} className={cn('absolute top-full z-30 mt-2 min-w-48 rounded-control border border-border bg-surface p-1.5 shadow-raised', align === 'end' ? 'end-0' : 'start-0', className)} onKeyDown={handleMenuKeyDown} onClick={() => setOpen(false)}>
          {children}
        </div>
      )}
    </div>
  );
}

export function DropdownItem({ children, destructive = false, className, ...props }) {
  return <button type="button" role="menuitem" className={cn('flex min-h-10 w-full items-center gap-2 rounded-lg px-3 text-start text-sm font-semibold transition-colors hover:bg-stone-100 focus:bg-stone-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary/30', destructive ? 'text-error' : 'text-ink', className)} {...props}>{children}</button>;
}

export function Tooltip({ content, children, side = 'top', className }) {
  const id = useId();
  const positions = {
    top: 'bottom-full left-1/2 mb-2 -translate-x-1/2',
    bottom: 'left-1/2 top-full mt-2 -translate-x-1/2',
    left: 'end-full top-1/2 me-2 -translate-y-1/2',
    right: 'start-full top-1/2 ms-2 -translate-y-1/2',
  };
  return (
    <span className="group relative inline-flex">
      {cloneElement(children, { 'aria-describedby': id })}
      <span id={id} role="tooltip" className={cn('pointer-events-none absolute z-40 w-max max-w-60 rounded-lg bg-ink px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-raised transition-opacity group-hover:opacity-100 group-focus-within:opacity-100', positions[side], className)}>
        {content}
      </span>
    </span>
  );
}
