import React, { useEffect, useState } from 'react';
import { ArrowRight, MapPin, PackageSearch, Search, X } from 'lucide-react';
import { MOROCCAN_CITIES } from '../data/mockData';
import { Button } from './ui';
import { Container } from './layout';
import { useI18n } from '../i18n';

export default function Hero({ selectedCity, setSelectedCity, searchTerm, setSearchTerm, onRentOut }) {
  const { t, cityLabel } = useI18n();
  const [query, setQuery] = useState(searchTerm);

  useEffect(() => setQuery(searchTerm), [searchTerm]);

  const submitSearch = (event) => {
    event.preventDefault();
    setSearchTerm(query.trim());
    requestAnimationFrame(() => document.getElementById('catalogue-grid')?.scrollIntoView({ behavior: 'smooth' }));
  };

  return (
    <section className="relative overflow-hidden border-b border-border bg-canvas py-10 sm:py-14 lg:py-20">
      <div aria-hidden="true" className="absolute inset-y-0 end-0 hidden w-[42%] bg-primary-subtle/60 lg:block" />
      <Container className="relative grid items-center gap-9 lg:grid-cols-[1.1fr_0.9fr] lg:gap-14">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-primary">{t('hero.eyebrow')}</p>
          <h1 className="mt-4 max-w-3xl font-display text-4xl font-bold leading-[1.08] tracking-tight text-ink sm:text-5xl lg:text-6xl">
            {t('hero.title')}
          </h1>
          <p className="mt-5 max-w-2xl text-base leading-7 text-muted sm:text-lg">
            {t('hero.subtitle')}
          </p>

          <form onSubmit={submitSearch} className="mt-8 rounded-card border border-border bg-surface p-3 shadow-card sm:p-4" role="search">
            <div className="grid gap-3 md:grid-cols-2 md:items-end lg:grid-cols-[0.78fr_1.35fr_auto]">
              <label className="block">
                <span className="ui-label">{t('hero.where')}</span>
                <span className="relative block">
                  <MapPin aria-hidden="true" className="pointer-events-none absolute start-3.5 top-1/2 size-4 -translate-y-1/2 text-action" />
                  <select value={selectedCity} onChange={(event) => setSelectedCity(event.target.value)} className="ui-control appearance-none ps-10">
                    {MOROCCAN_CITIES.map((city) => <option key={city} value={city}>{city === 'Toutes les villes' ? t('city.all') : cityLabel(city)}</option>)}
                  </select>
                </span>
              </label>
              <label className="block">
                <span className="ui-label">{t('hero.what')}</span>
                <span className="relative block">
                  <Search aria-hidden="true" className="pointer-events-none absolute start-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" />
                  <input
                    type="search"
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder={t('hero.searchPlaceholder')}
                    className="ui-control ps-10 pe-10"
                  />
                  {query && (
                    <button type="button" onClick={() => setQuery('')} className="absolute end-2.5 top-1/2 flex size-8 -translate-y-1/2 items-center justify-center rounded-lg text-muted hover:bg-stone-100 hover:text-ink" aria-label={t('hero.clearSearch')}>
                      <X aria-hidden="true" className="size-4" />
                    </button>
                  )}
                </span>
              </label>
              <Button type="submit" variant="action" size="lg" className="w-full md:col-span-2 lg:col-span-1 lg:w-auto">
                <PackageSearch aria-hidden="true" className="size-4" /> {t('common.search')}
              </Button>
            </div>
          </form>

          <button type="button" onClick={onRentOut} className="mt-5 inline-flex min-h-11 items-center gap-2 rounded-lg text-sm font-bold text-primary hover:text-primary-hover hover:underline">
            {t('hero.ownerCta')} <ArrowRight aria-hidden="true" className="rtl-flip size-4" />
          </button>
        </div>

        <div className="relative mx-auto w-full max-w-xl lg:max-w-none">
          <div className="overflow-hidden rounded-modal border border-primary/15 bg-surface p-3 shadow-raised sm:p-4">
            <img src="/images/mini_excavator_lokiini.png" alt={t('hero.imageAlt')} className="aspect-[4/3] w-full rounded-card bg-stone-100 object-cover" />
            <div className="flex items-center justify-between gap-4 px-2 pb-1 pt-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-primary">{t('hero.moment')}</p>
                <p className="mt-1 font-display text-xl font-bold text-ink">{t('hero.promise')}</p>
              </div>
              <span className="hidden rounded-full bg-action-subtle px-3 py-1.5 text-xs font-bold text-action-hover sm:inline-flex">{t('hero.mad')}</span>
            </div>
          </div>
        </div>
      </Container>
    </section>
  );
}
