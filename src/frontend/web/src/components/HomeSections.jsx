import React from 'react';
import { ArrowRight, CalendarCheck2, ClipboardCheck, FileCheck2, Fingerprint, PackageCheck, Search, ShieldCheck } from 'lucide-react';
import { Button, Card } from './ui';
import { Container } from './layout';
import { useI18n } from '../i18n';

const steps = [
  { icon: Search, key: 'search' },
  { icon: CalendarCheck2, key: 'request' },
  { icon: PackageCheck, key: 'return' },
];

const trustItems = [
  { icon: Fingerprint, key: 'identity' },
  { icon: FileCheck2, key: 'contract' },
  { icon: ClipboardCheck, key: 'inspection' },
  { icon: ShieldCheck, key: 'status' },
];

export function HowLokiiniWorks() {
  const { t, formatNumber } = useI18n();
  return (
    <section aria-labelledby="how-heading" className="bg-surface py-14 sm:py-18">
      <Container>
        <div className="max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">{t('home.howEyebrow')}</p>
          <h2 id="how-heading" className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">{t('home.howTitle')}</h2>
        </div>
        <ol className="mt-8 grid gap-4 md:grid-cols-3">
          {steps.map((step, index) => (
            <li key={step.key}>
              <Card className="h-full p-5 sm:p-6">
                <div className="flex items-center justify-between">
                  <span className="flex size-11 items-center justify-center rounded-control bg-primary-subtle text-primary"><step.icon aria-hidden="true" className="size-5" /></span>
                  <span className="font-display text-2xl font-bold text-stone-300">{formatNumber(index + 1, { minimumIntegerDigits: 2 })}</span>
                </div>
                <h3 className="mt-5 text-lg font-bold text-ink">{t(`home.steps.${step.key}Title`)}</h3>
                <p className="mt-2 text-sm leading-6 text-muted">{t(`home.steps.${step.key}Text`)}</p>
              </Card>
            </li>
          ))}
        </ol>
      </Container>
    </section>
  );
}

export function TrustSafetySection() {
  const { t } = useI18n();
  return (
    <section aria-labelledby="trust-heading" className="border-y border-border bg-canvas py-14 sm:py-18">
      <Container className="grid gap-8 lg:grid-cols-[0.72fr_1.28fr] lg:items-start lg:gap-12">
        <div className="lg:sticky lg:top-28">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">{t('home.trustEyebrow')}</p>
          <h2 id="trust-heading" className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">{t('home.trustTitle')}</h2>
          <p className="mt-4 text-sm leading-6 text-muted">{t('home.trustText')}</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {trustItems.map((item) => (
            <Card key={item.key} className="p-5">
              <item.icon aria-hidden="true" className="size-5 text-primary" />
              <h3 className="mt-4 text-base font-bold text-ink">{t(`home.trust.${item.key}Title`)}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{t(`home.trust.${item.key}Text`)}</p>
            </Card>
          ))}
        </div>
      </Container>
    </section>
  );
}

export function OwnerCallToAction({ onRentOut }) {
  const { t } = useI18n();
  return (
    <section className="bg-surface py-14 sm:py-18">
      <Container>
        <div className="overflow-hidden rounded-modal bg-primary px-6 py-9 text-white shadow-card sm:px-10 sm:py-12 lg:flex lg:items-center lg:justify-between lg:gap-10">
          <div className="max-w-2xl">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-200">{t('home.ownerEyebrow')}</p>
            <h2 className="mt-2 font-display text-3xl font-bold tracking-tight sm:text-4xl">{t('home.ownerTitle')}</h2>
            <p className="mt-4 text-sm leading-6 text-emerald-50 sm:text-base">{t('home.ownerText')}</p>
          </div>
          <Button variant="action" size="lg" className="mt-7 w-full shrink-0 lg:mt-0 lg:w-auto" onClick={onRentOut}>
            {t('nav.rentOut')} <ArrowRight aria-hidden="true" className="rtl-flip size-4" />
          </Button>
        </div>
      </Container>
    </section>
  );
}
