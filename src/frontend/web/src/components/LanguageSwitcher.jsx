import React from 'react';
import { Languages } from 'lucide-react';
import { useI18n } from '../i18n';
import { cn } from './ui';

export default function LanguageSwitcher({ compact = false, inverse = false }) {
  const { locale, setLocale, t } = useI18n();
  const options = ['fr', 'ar'];

  const handleKeyDown = (event, index) => {
    let nextIndex = null;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') nextIndex = (index + 1) % options.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') nextIndex = (index - 1 + options.length) % options.length;
    if (event.key === 'Home') nextIndex = 0;
    if (event.key === 'End') nextIndex = options.length - 1;
    if (nextIndex === null) return;

    event.preventDefault();
    setLocale(options[nextIndex]);
    event.currentTarget.parentElement?.querySelectorAll('[role="radio"]')[nextIndex]?.focus();
  };

  return (
    <div
      className={cn('inline-flex items-center rounded-lg border p-0.5', inverse ? 'border-slate-600 bg-slate-800' : 'border-border bg-stone-50')}
      role="radiogroup"
      aria-label={t('language.name')}
    >
      {!compact && <Languages aria-hidden="true" className={cn('mx-1 size-4', inverse ? 'text-slate-300' : 'text-muted')} />}
      {options.map((option, index) => (
        <button
          key={option}
          type="button"
          lang={option === 'ar' ? 'ar-MA' : 'fr-MA'}
          dir={option === 'ar' ? 'rtl' : 'ltr'}
          role="radio"
          aria-checked={locale === option}
          tabIndex={locale === option ? 0 : -1}
          onClick={() => setLocale(option)}
          onKeyDown={(event) => handleKeyDown(event, index)}
          className={cn(
            'min-h-11 rounded-md px-3 text-xs font-bold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/40 sm:min-h-8 sm:px-2',
            locale === option
              ? 'bg-white text-primary shadow-subtle'
              : inverse ? 'text-slate-300 hover:text-white' : 'text-muted hover:text-ink',
          )}
        >
          {compact ? option.toUpperCase() : t(`language.${option}`)}
        </button>
      ))}
    </div>
  );
}
