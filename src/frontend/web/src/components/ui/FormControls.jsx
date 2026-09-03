import React, { forwardRef, useId } from 'react';
import { Check, ChevronDown } from 'lucide-react';
import { cn } from './utils';

function FieldShell({ id, label, hint, error, required, children, className }) {
  const messageId = `${id}-message`;
  return (
    <div className={className}>
      {label && (
        <label htmlFor={id} className="ui-label">
          {label}{required && <span aria-hidden="true" className="text-error"> *</span>}
        </label>
      )}
      {children(messageId, Boolean(error))}
      {(error || hint) && (
        <p id={messageId} role={error ? 'alert' : undefined} className={cn('ui-help', error && 'font-semibold text-error')}>
          {error || hint}
        </p>
      )}
    </div>
  );
}

export const Input = forwardRef(function Input(
  { id: suppliedId, label, hint, error, required, leadingIcon: LeadingIcon, trailing, className, inputClassName, ...props },
  ref,
) {
  const generatedId = useId();
  const id = suppliedId || generatedId;
  return (
    <FieldShell id={id} label={label} hint={hint} error={error} required={required} className={className}>
      {(messageId, hasError) => (
        <div className="relative">
          {LeadingIcon && <LeadingIcon aria-hidden="true" className="pointer-events-none absolute start-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />}
          <input
            ref={ref}
            id={id}
            required={required}
            aria-invalid={Boolean(error)}
            aria-describedby={(error || hint) ? messageId : undefined}
            aria-errormessage={hasError ? messageId : undefined}
            className={cn('ui-control', LeadingIcon && 'ps-10', trailing && 'pe-10', error && 'ui-control-error', inputClassName)}
            {...props}
          />
          {trailing && <span aria-hidden="true" className="absolute end-3.5 top-1/2 -translate-y-1/2 text-muted">{trailing}</span>}
        </div>
      )}
    </FieldShell>
  );
});

export const Textarea = forwardRef(function Textarea(
  { id: suppliedId, label, hint, error, required, className, textareaClassName, rows = 4, ...props },
  ref,
) {
  const generatedId = useId();
  const id = suppliedId || generatedId;
  return (
    <FieldShell id={id} label={label} hint={hint} error={error} required={required} className={className}>
      {(messageId, hasError) => (
        <textarea
          ref={ref}
          id={id}
          rows={rows}
          required={required}
          aria-invalid={Boolean(error)}
          aria-describedby={(error || hint) ? messageId : undefined}
          aria-errormessage={hasError ? messageId : undefined}
          className={cn('ui-control resize-y py-3', error && 'ui-control-error', textareaClassName)}
          {...props}
        />
      )}
    </FieldShell>
  );
});

export const Select = forwardRef(function Select(
  { id: suppliedId, label, hint, error, required, options, placeholder, className, selectClassName, children, ...props },
  ref,
) {
  const generatedId = useId();
  const id = suppliedId || generatedId;
  return (
    <FieldShell id={id} label={label} hint={hint} error={error} required={required} className={className}>
      {(messageId, hasError) => (
        <div className="relative">
          <select
            ref={ref}
            id={id}
            required={required}
            aria-invalid={Boolean(error)}
            aria-describedby={(error || hint) ? messageId : undefined}
            aria-errormessage={hasError ? messageId : undefined}
            className={cn('ui-control appearance-none pe-10', error && 'ui-control-error', selectClassName)}
            {...props}
          >
            {placeholder && <option value="">{placeholder}</option>}
            {options?.map((option) => (
              <option key={option.value} value={option.value} disabled={option.disabled}>{option.label}</option>
            ))}
            {children}
          </select>
          <ChevronDown aria-hidden="true" className="pointer-events-none absolute end-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />
        </div>
      )}
    </FieldShell>
  );
});

function Choice({ type, label, description, className, inputClassName, ...props }) {
  const id = useId();
  const labelId = `${id}-label`;
  const descriptionId = `${id}-description`;
  return (
    <label className={cn('flex min-h-11 cursor-pointer items-start gap-3 rounded-control p-2 focus-within:ring-2 focus-within:ring-primary/25', className)}>
      <input
        type={type}
        aria-labelledby={labelId}
        aria-describedby={description ? descriptionId : undefined}
        className={cn('mt-0.5 size-4 shrink-0 border-slate-300 text-primary accent-primary focus:ring-primary', inputClassName)}
        {...props}
      />
      <span>
        <span id={labelId} className="block text-sm font-semibold text-ink">{label}</span>
        {description && <span id={descriptionId} className="mt-0.5 block text-xs leading-5 text-muted">{description}</span>}
      </span>
    </label>
  );
}

export function Checkbox(props) {
  return <Choice type="checkbox" {...props} />;
}

export function Radio(props) {
  return <Choice type="radio" {...props} />;
}

export const Switch = forwardRef(function Switch({ checked, onChange, label, description, disabled, className, ...props }, ref) {
  const id = useId();
  const labelId = `${id}-label`;
  const descriptionId = `${id}-description`;
  return (
    <div className={cn('flex min-h-11 items-center justify-between gap-4', disabled && 'opacity-55', className)}>
      <span>
        <span id={labelId} className="block text-sm font-semibold text-ink">{label}</span>
        {description && <span id={descriptionId} className="mt-0.5 block text-xs leading-5 text-muted">{description}</span>}
      </span>
      <button
        ref={ref}
        type="button"
        role="switch"
        aria-checked={checked}
        aria-labelledby={labelId}
        aria-describedby={description ? descriptionId : undefined}
        disabled={disabled}
        onClick={() => onChange?.(!checked)}
        className={cn('relative h-6 w-11 shrink-0 rounded-full transition-colors focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2', checked ? 'bg-primary' : 'bg-slate-300')}
        {...props}
      >
        <span className={cn('absolute top-0.5 flex size-5 items-center justify-center rounded-full bg-white shadow transition-transform', checked ? 'translate-x-5 rtl:-translate-x-5' : 'translate-x-0.5 rtl:-translate-x-0.5')}>
          {checked && <Check aria-hidden="true" className="size-3 text-primary" />}
        </span>
      </button>
    </div>
  );
});
