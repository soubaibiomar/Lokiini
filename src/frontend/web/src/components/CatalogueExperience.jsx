import React, { useEffect, useMemo, useState } from 'react';
import { Crosshair, Filter, MapPin, RotateCcw, SlidersHorizontal, X } from 'lucide-react';
import { MOROCCAN_CITIES } from '../data/mockData';
import { Badge, Button, Checkbox, Drawer, Input, Select } from './ui';
import { Container } from './layout';
import EquipmentGrid from './EquipmentGrid';
import { useI18n } from '../i18n';

function FilterFields({
  categories,
  filters,
  draftMin,
  draftMax,
  onDraftMin,
  onDraftMax,
  onChange,
  onApplyPrices,
  onLocate,
  locating,
  locationError,
  priceError,
}) {
  const { t, cityLabel } = useI18n();
  return (
    <div className="space-y-6">
      <Select
        label={t('catalogue.category')}
        value={filters.category}
        onChange={(event) => onChange({ category: event.target.value })}
      >
        <option value="all">{t('catalogue.allCategories')}</option>
        {categories.map((category) => <option key={category.id} value={category.id}>{t(`category.${category.id}`, {}, category.label)}</option>)}
      </Select>

      <Select
        label={t('catalogue.city')}
        value={filters.city}
        onChange={(event) => onChange({ city: event.target.value })}
      >
        {MOROCCAN_CITIES.map((city) => <option key={city} value={city}>{city === 'Toutes les villes' ? t('city.all') : cityLabel(city)}</option>)}
      </Select>

      <fieldset>
        <legend className="ui-label">{t('catalogue.price')}</legend>
        <div className="grid grid-cols-2 gap-3">
          <Input
            type="number"
            min="0"
            step="10"
            inputMode="numeric"
            value={draftMin}
            onChange={(event) => onDraftMin(event.target.value)}
            placeholder={t('catalogue.minimum')}
            trailing="MAD"
            aria-label={`${t('catalogue.minimum')} ${t('catalogue.price')}`}
            error={priceError}
          />
          <Input
            type="number"
            min="0"
            step="10"
            inputMode="numeric"
            value={draftMax}
            onChange={(event) => onDraftMax(event.target.value)}
            placeholder={t('catalogue.maximum')}
            trailing="MAD"
            aria-label={`${t('catalogue.maximum')} ${t('catalogue.price')}`}
            aria-invalid={Boolean(priceError)}
          />
        </div>
        <Button variant="secondary" size="sm" className="mt-3 w-full" onClick={onApplyPrices}>{t('catalogue.applyPrice')}</Button>
      </fieldset>

      <div className="space-y-1 border-t border-border pt-5">
        <Checkbox
          checked={filters.available}
          onChange={(event) => onChange({ available: event.target.checked })}
          label={t('catalogue.available')}
          description={t('catalogue.availableHelp')}
        />
        <Checkbox
          checked={filters.verified}
          onChange={(event) => onChange({ verified: event.target.checked })}
          label={t('catalogue.verified')}
          description={t('catalogue.verifiedHelp')}
        />
      </div>

      <div className="border-t border-border pt-5">
        <p className="ui-label">{t('catalogue.distance')}</p>
        {filters.position ? (
          <div className="rounded-control border border-primary/20 bg-primary-subtle p-3">
            <div className="flex items-center gap-2 text-sm font-bold text-primary">
              <Crosshair aria-hidden="true" className="size-4" /> {t('catalogue.positionUsed')}
            </div>
            <Select
              className="mt-3"
              value={filters.radius}
              onChange={(event) => onChange({ radius: Number(event.target.value) })}
              aria-label={t('catalogue.distance')}
            >
              {[5, 10, 25, 50, 100].map((radius) => <option key={radius} value={radius}>{radius} km</option>)}
            </Select>
            <button type="button" onClick={() => onChange({ position: null })} className="mt-2 inline-flex min-h-10 items-center gap-1.5 text-xs font-bold text-primary hover:underline">
              <X aria-hidden="true" className="size-3.5" /> {t('catalogue.stopLocation')}
            </button>
          </div>
        ) : (
          <Button variant="secondary" className="w-full" onClick={onLocate} disabled={locating}>
            <MapPin aria-hidden="true" className="size-4" /> {locating ? t('catalogue.locating') : t('catalogue.nearMe')}
          </Button>
        )}
        {locationError && <p role="alert" className="mt-2 text-xs font-semibold leading-5 text-error">{locationError}</p>}
        <p className="mt-2 text-xs leading-5 text-muted">{t('catalogue.locationHelp')}</p>
      </div>
    </div>
  );
}

export default function CatalogueExperience({
  equipmentList,
  total,
  categories,
  filters,
  onChangeFilters,
  onResetFilters,
  onSelectEquipment,
  loading,
  loadingMore,
  hasMore,
  error,
  onRetry,
  onLoadMore,
}) {
  const { t, cityLabel, formatMAD, formatNumber } = useI18n();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [draftMin, setDraftMin] = useState(filters.prix_min ?? '');
  const [draftMax, setDraftMax] = useState(filters.prix_max ?? '');
  const [locating, setLocating] = useState(false);
  const [locationError, setLocationError] = useState('');
  const [priceError, setPriceError] = useState('');

  useEffect(() => setDraftMin(filters.prix_min ?? ''), [filters.prix_min]);
  useEffect(() => setDraftMax(filters.prix_max ?? ''), [filters.prix_max]);

  const activeFilters = useMemo(() => {
    const items = [];
    if (filters.search) items.push({ key: 'search', label: `« ${filters.search} »`, clear: { search: '' } });
    if (filters.category !== 'all') {
      const category = categories.find((item) => item.id === filters.category);
      items.push({ key: 'category', label: t(`category.${filters.category}`, {}, category?.label || filters.category), clear: { category: 'all' } });
    }
    if (filters.city !== 'Toutes les villes') items.push({ key: 'city', label: cityLabel(filters.city), clear: { city: 'Toutes les villes' } });
    if (filters.prix_min != null) items.push({ key: 'min', label: t('catalogue.from', { price: formatMAD(filters.prix_min) }), clear: { prix_min: null } });
    if (filters.prix_max != null) items.push({ key: 'max', label: t('catalogue.upTo', { price: formatMAD(filters.prix_max) }), clear: { prix_max: null } });
    if (filters.verified) items.push({ key: 'verified', label: t('catalogue.verified'), clear: { verified: false } });
    if (!filters.available) items.push({ key: 'availability', label: t('catalogue.includeUnavailable'), clear: { available: true } });
    if (filters.position) items.push({ key: 'position', label: t('catalogue.within', { radius: formatNumber(filters.radius) }), clear: { position: null } });
    return items;
  }, [categories, cityLabel, filters, formatMAD, formatNumber, t]);

  const applyPrices = () => {
    const min = draftMin === '' ? null : Math.max(0, Number(draftMin));
    const max = draftMax === '' ? null : Math.max(0, Number(draftMax));
    if (min != null && max != null && min > max) {
      setPriceError(t('catalogue.priceError'));
      return false;
    }
    setPriceError('');
    onChangeFilters({ prix_min: Number.isFinite(min) ? min : null, prix_max: Number.isFinite(max) ? max : null });
    return true;
  };

  const locate = () => {
    setLocationError('');
    if (!navigator.geolocation) {
      setLocationError(t('catalogue.locationUnsupported'));
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        setLocating(false);
        onChangeFilters({ position: { lat: coords.latitude, lng: coords.longitude } });
      },
      () => {
        setLocating(false);
        setLocationError(t('catalogue.locationDenied'));
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  };

  const filterProps = {
    categories,
    filters,
    draftMin,
    draftMax,
    onDraftMin: setDraftMin,
    onDraftMax: setDraftMax,
    onChange: onChangeFilters,
    onApplyPrices: applyPrices,
    onLocate: locate,
    locating,
    locationError,
    priceError,
  };

  return (
    <section id="catalogue-grid" className="scroll-mt-24 border-b border-border bg-surface py-10 sm:py-12">
      <Container>
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">{t('catalogue.eyebrow')}</p>
            <h2 className="mt-1 font-display text-2xl font-bold tracking-tight text-ink sm:text-3xl">{t('catalogue.title')}</h2>
            <p aria-live="polite" aria-atomic="true" className="mt-1 text-sm text-muted">
              {loading ? t('catalogue.searching') : error ? t('catalogue.temporarilyUnavailable') : t((total ?? equipmentList.length) === 1 ? 'catalogue.oneResult' : 'catalogue.results', { count: formatNumber(total ?? equipmentList.length) })}
            </p>
          </div>
          <Button variant="secondary" className="lg:hidden" onClick={() => setDrawerOpen(true)}>
            <Filter aria-hidden="true" className="size-4" /> {t('catalogue.filters')}
            {activeFilters.length > 0 && <Badge>{activeFilters.length}</Badge>}
          </Button>
        </div>

        {activeFilters.length > 0 && (
          <div className="mb-6 flex flex-wrap items-center gap-2" aria-label={t('catalogue.activeFilters')}>
            {activeFilters.map((item) => (
              <button key={item.key} type="button" aria-label={`${t('catalogue.removeFilter', {}, 'Supprimer le filtre')} ${item.label}`} onClick={() => onChangeFilters(item.clear)} className="inline-flex min-h-9 items-center gap-1.5 rounded-full border border-primary/20 bg-primary-subtle px-3 text-xs font-bold text-primary hover:border-primary/40">
                {item.label} <X aria-hidden="true" className="size-3.5" />
              </button>
            ))}
            <button type="button" onClick={onResetFilters} className="inline-flex min-h-9 items-center gap-1.5 px-2 text-xs font-bold text-muted hover:text-ink">
              <RotateCcw aria-hidden="true" className="size-3.5" /> {t('catalogue.clearAll')}
            </button>
          </div>
        )}

        <div className="grid items-start gap-8 lg:grid-cols-[17rem_minmax(0,1fr)]">
          <aside className="sticky top-24 hidden rounded-card border border-border bg-canvas p-5 lg:block" aria-label={t('catalogue.filterAria')}>
            <div className="mb-5 flex items-center gap-2 border-b border-border pb-4">
              <SlidersHorizontal aria-hidden="true" className="size-4 text-primary" />
              <h3 className="font-bold text-ink">{t('catalogue.refine')}</h3>
            </div>
            <FilterFields {...filterProps} />
          </aside>

          <EquipmentGrid
            embedded
            equipmentList={equipmentList}
            onSelectEquipment={onSelectEquipment}
            hasFilters={activeFilters.length > 0}
            onResetFilters={onResetFilters}
            loading={loading}
            loadingMore={loadingMore}
            error={error}
            onRetry={onRetry}
            hasMore={hasMore}
            onLoadMore={onLoadMore}
          />
        </div>
      </Container>

      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={t('catalogue.filterAria')}
        description={t('catalogue.filterDescription')}
        footer={<div className="grid grid-cols-2 gap-3"><Button variant="secondary" onClick={onResetFilters}>{t('catalogue.reset')}</Button><Button onClick={() => { if (applyPrices()) setDrawerOpen(false); }}>{t('catalogue.viewResults')}</Button></div>}
      >
        <FilterFields {...filterProps} />
      </Drawer>
    </section>
  );
}
