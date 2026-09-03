import React from 'react';
import { ArrowRight, MapPin } from 'lucide-react';
import { cn } from './ui';
import { Container } from './layout';
import { useI18n } from '../i18n';

export default function GeoCitiesSection({ cities, selectedCity, onSelectCity }) {
  const { t, cityLabel } = useI18n();
  if (!cities.length) return null;
  return (
    <section aria-labelledby="cities-heading" className="bg-canvas py-12 sm:py-14">
      <Container>
        <div className="max-w-2xl">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">{t('home.citiesEyebrow')}</p>
          <h2 id="cities-heading" className="mt-2 font-display text-3xl font-bold tracking-tight text-ink">{t('home.citiesTitle')}</h2>
          <p className="mt-3 text-sm leading-6 text-muted">{t('home.citiesText')}</p>
        </div>
        <div className="mt-7 flex flex-wrap gap-3">
          {cities.map((city) => {
            const active = selectedCity === city;
            return (
              <button key={city} type="button" aria-pressed={active} onClick={() => onSelectCity(city)} className={cn('group inline-flex min-h-12 items-center gap-3 rounded-control border px-4 text-sm font-bold transition-colors', active ? 'border-primary bg-primary text-white' : 'border-border bg-surface text-ink hover:border-primary/35 hover:text-primary')}>
                <MapPin aria-hidden="true" className={cn('size-4', active ? 'text-white' : 'text-action')} />
                {cityLabel(city)}
                <ArrowRight aria-hidden="true" className="rtl-flip size-4 opacity-50 transition-transform group-hover:translate-x-0.5" />
              </button>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
