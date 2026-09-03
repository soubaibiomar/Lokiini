import React from 'react';
import { MapPin, Package, ShieldCheck, Sparkles, Star } from 'lucide-react';
import { cn } from './utils';
import { Badge, Card } from './Surfaces';
import { Button } from './Button';
import { useI18n } from '../../i18n';

export function PriceDisplay({ amount, period, prefix, size = 'md', className }) {
  const { formatMAD } = useI18n();
  const sizes = { sm: 'text-base', md: 'text-xl', lg: 'text-3xl' };
  const numericAmount = Number(amount);
  return (
    <div className={cn('leading-tight', className)}>
      {prefix && <span className="mb-0.5 block text-[11px] font-medium text-muted">{prefix}</span>}
      <span className={cn('font-display font-bold tracking-tight text-ink', sizes[size])}>
        {Number.isFinite(numericAmount) ? formatMAD(numericAmount) : '—'}
      </span>
      {period && <span className="ms-1 text-xs font-semibold text-muted">/ {period}</span>}
    </div>
  );
}

export function Rating({ value, count, size = 'sm', className }) {
  const { t, formatNumber } = useI18n();
  const validValue = Number(value);
  if (!Number.isFinite(validValue)) return null;
  const rating = formatNumber(validValue, { maximumFractionDigits: 1 });
  const hasCount = Number.isFinite(Number(count));
  return (
    <span className={cn('inline-flex items-center gap-1 font-bold text-ink', size === 'sm' ? 'text-xs' : 'text-sm', className)} aria-label={t(hasCount ? 'rating.ariaWithCount' : 'rating.aria', { rating, count: formatNumber(count) })}>
      <Star aria-hidden="true" className={cn('fill-amber-400 text-amber-500', size === 'sm' ? 'size-3.5' : 'size-4')} />
      <span>{rating}</span>
      {hasCount && <span className="font-normal text-muted">({formatNumber(count)})</span>}
    </span>
  );
}

export function TrustBadge({ level = 'identity', children, className }) {
  const { t } = useI18n();
  const labels = {
    identity: t('trust.verified'),
    history: t('trust.history'),
    equipment: t('trust.equipment'),
    transaction: t('trust.transaction'),
  };
  return <Badge variant="success" icon={ShieldCheck} className={className}>{children || labels[level]}</Badge>;
}

export function EquipmentCard({ equipment, onDetails, onBook, className }) {
  const { t, cityLabel, formatNumber } = useI18n();
  const title = equipment.title || equipment.titre;
  const image = equipment.image || equipment.photos?.[0] || null;
  const city = equipment.city || equipment.ville;
  const distance = equipment.distance || equipment.distance_km;
  const price = equipment.daily_price_mad ?? equipment.prix_par_jour;
  const verified = equipment.is_verified ?? equipment.loueur?.is_verified;
  const discount = Number(equipment.discount_pct || 0);
  return (
    <Card as="article" interactive className={cn('group flex h-full flex-col overflow-hidden', className)}>
      <div className="relative aspect-[4/3] overflow-hidden bg-stone-100">
        {image ? (
          <img src={image} alt={title || t('equipment.imageAlt')} loading="lazy" className="size-full object-cover transition-transform duration-300 group-hover:scale-[1.025]" />
        ) : (
          <div className="flex size-full flex-col items-center justify-center gap-2 text-muted">
            <Package aria-hidden="true" className="size-8" />
            <span className="text-xs font-semibold">{t('equipment.photoUnavailable')}</span>
          </div>
        )}
        {discount > 0 && <Badge variant="warning" icon={Sparkles} className="absolute end-3 top-3 shadow-subtle">-{discount}%</Badge>}
      </div>
      <div className="flex flex-1 flex-col p-4">
        <h3 className="line-clamp-2 text-sm font-bold leading-5 text-ink">{title}</h3>
        {(city || distance) && (
          <p className="mt-2 flex items-center gap-1 text-xs text-muted">
            <MapPin aria-hidden="true" className="size-3.5 text-primary" />
            <span>{[cityLabel(city), distance && `${formatNumber(distance)} km`].filter(Boolean).join(' · ')}</span>
          </p>
        )}
        <div className="mt-3 flex min-h-6 flex-wrap items-center justify-between gap-2">
          <Rating value={equipment.rating ?? equipment.note_moyenne} count={equipment.reviews_count ?? equipment.nombre_avis} />
          {verified && <TrustBadge />}
        </div>
        <div className="mt-auto flex items-end justify-between gap-3 border-t border-border pt-4">
          <PriceDisplay amount={price} period={t('equipment.day')} prefix={t('equipment.from')} />
        </div>
        <div className="mt-4 grid grid-cols-2 gap-2">
          <Button variant="secondary" size="sm" aria-label={`${t('equipment.details')} — ${title}`} onClick={() => onDetails?.(equipment)}>{t('equipment.details')}</Button>
          <Button variant="action" size="sm" aria-label={`${t('equipment.bookShort')} — ${title}`} onClick={() => onBook?.(equipment)}>{t('equipment.bookShort')}</Button>
        </div>
      </div>
    </Card>
  );
}
