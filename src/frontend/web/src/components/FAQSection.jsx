import React, { useState } from 'react';
import { ChevronDown, HelpCircle } from 'lucide-react';
import { cn } from './ui';
import { Container } from './layout';
import { useI18n } from '../i18n';

export default function FAQSection() {
  const { t } = useI18n();
  const faqItems = [1, 2, 3, 4, 5].map((item) => ({ question: t(`faq.${item}.q`), answer: t(`faq.${item}.a`) }));
  const [openIndex, setOpenIndex] = useState(null);
  return (
    <section aria-labelledby="faq-heading" className="bg-canvas py-14 sm:py-18">
      <Container size="lg">
        <div className="mx-auto max-w-2xl text-center">
          <HelpCircle aria-hidden="true" className="mx-auto size-6 text-primary" />
          <h2 id="faq-heading" className="mt-3 font-display text-3xl font-bold tracking-tight text-ink">{t('faq.title')}</h2>
          <p className="mt-3 text-sm leading-6 text-muted">{t('faq.subtitle')}</p>
        </div>
        <div className="mx-auto mt-8 max-w-3xl divide-y divide-border overflow-hidden rounded-card border border-border bg-surface shadow-subtle">
          {faqItems.map((item, index) => {
            const open = index === openIndex;
            return (
              <div key={item.question}>
                <button type="button" id={`faq-trigger-${index}`} onClick={() => setOpenIndex(open ? null : index)} aria-expanded={open} aria-controls={`faq-panel-${index}`} className="flex min-h-16 w-full items-center justify-between gap-4 px-5 py-4 text-start text-sm font-bold text-ink hover:bg-stone-50 sm:px-6">
                  {item.question}
                  <ChevronDown aria-hidden="true" className={cn('size-4 shrink-0 text-muted transition-transform', open && 'rotate-180')} />
                </button>
                {open && <div id={`faq-panel-${index}`} role="region" aria-labelledby={`faq-trigger-${index}`} className="px-5 pb-5 text-sm leading-6 text-muted sm:px-6">{item.answer}</div>}
              </div>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
