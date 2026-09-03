import React, { useId, useState } from 'react';
import { Check, ChevronRight } from 'lucide-react';
import { cn } from './utils';
import { useI18n } from '../../i18n';

export function Tabs({ items, value, defaultValue, onChange, className }) {
  const [internalValue, setInternalValue] = useState(defaultValue || items[0]?.value);
  const selected = value ?? internalValue;
  const baseId = useId();
  const select = (next) => {
    if (value === undefined) setInternalValue(next);
    onChange?.(next);
  };
  const handleKeyDown = (event, index) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const nextIndex = event.key === 'Home' ? 0
      : event.key === 'End' ? items.length - 1
        : event.key === 'ArrowRight' ? (index + 1) % items.length
          : (index - 1 + items.length) % items.length;
    select(items[nextIndex].value);
    requestAnimationFrame(() => document.getElementById(`${baseId}-${items[nextIndex].value}-tab`)?.focus());
  };
  return (
    <div className={className}>
      <div role="tablist" aria-orientation="horizontal" className="flex gap-1 overflow-x-auto rounded-control bg-stone-100 p-1">
        {items.map((item, index) => (
          <button key={item.value} id={`${baseId}-${item.value}-tab`} type="button" role="tab" tabIndex={selected === item.value ? 0 : -1} aria-selected={selected === item.value} aria-controls={`${baseId}-${item.value}-panel`} onClick={() => select(item.value)} onKeyDown={(event) => handleKeyDown(event, index)} className={cn('min-h-10 flex-1 whitespace-nowrap rounded-lg px-3 text-sm font-bold text-muted transition-colors', selected === item.value && 'bg-surface text-primary shadow-subtle')}>
            {item.label}
          </button>
        ))}
      </div>
      {items.map((item) => selected === item.value && (
        <div key={item.value} id={`${baseId}-${item.value}-panel`} role="tabpanel" aria-labelledby={`${baseId}-${item.value}-tab`} tabIndex={0} className="pt-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30">
          {item.content}
        </div>
      ))}
    </div>
  );
}

export function Stepper({ steps, current = 0, className }) {
  const { t, formatNumber } = useI18n();
  return (
    <ol aria-label={t('navigation.progress')} className={cn('grid gap-3 sm:grid-flow-col sm:auto-cols-fr', className)}>
      {steps.map((step, index) => {
        const complete = index < current;
        const active = index === current;
        return (
          <li key={step.label} aria-current={active ? 'step' : undefined} className="flex items-start gap-3">
            <span className={cn('flex size-8 shrink-0 items-center justify-center rounded-full border text-xs font-bold', complete && 'border-primary bg-primary text-white', active && 'border-primary bg-primary-subtle text-primary', !complete && !active && 'border-border bg-surface text-muted')}>
              {complete ? <Check aria-hidden="true" className="size-4" /> : formatNumber(index + 1)}
              <span className="sr-only">{complete ? t('navigation.completed', {}, 'Terminée') : active ? t('navigation.current', {}, 'Étape actuelle') : ''}</span>
            </span>
            <span className="pt-1">
              <span className={cn('block text-sm font-bold', active || complete ? 'text-ink' : 'text-muted')}>{step.label}</span>
              {step.description && <span className="mt-0.5 block text-xs text-muted">{step.description}</span>}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

export function Breadcrumb({ items, className }) {
  const { t } = useI18n();
  return (
    <nav aria-label={t('navigation.breadcrumb')} className={className}>
      <ol className="flex flex-wrap items-center gap-1.5 text-sm text-muted">
        {items.map((item, index) => {
          const last = index === items.length - 1;
          return (
            <li key={`${item.label}-${index}`} className="flex items-center gap-1.5">
              {index > 0 && <ChevronRight aria-hidden="true" className="rtl-flip size-4" />}
              {last ? <span aria-current="page" className="font-semibold text-ink">{item.label}</span> : <a href={item.href} onClick={item.onClick} className="inline-flex min-h-11 items-center rounded hover:text-primary hover:underline sm:min-h-0">{item.label}</a>}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
