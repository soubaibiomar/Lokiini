import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  CalendarDays, ChevronRight, Clock3, FileText, ImageOff, MapPin, PackageCheck, Star, Truck,
  UserRound, X,
} from 'lucide-react';
import { getEquipment, getEquipmentPage, getUserReviews } from '../services/api';
import {
  Avatar, Badge, Button, Card, PriceDisplay, Rating, Skeleton, TrustBadge,
  useDialogLayer,
} from './ui';
import ReservationJourney from './ReservationJourney';
import { useI18n } from '../i18n';

const CATEGORY_LABELS = {
  tools: 'Outils & bricolage', btp: 'BTP & chantier', audiovisual: 'Photo & audiovisuel',
  audiovisuel: 'Photo & audiovisuel', event: 'Événementiel', evenementiel: 'Événementiel',
  outdoor: 'Plein air & camping', cleaning: 'Nettoyage & entretien', energy: 'Énergie',
  transport: 'Transport', vehicles: 'Véhicules', hightech: 'High-tech', medical: 'Matériel médical',
};

const RULE_KEYS = new Set(['regles', 'règles', 'rules', 'conditions', 'conditions_location']);
const DELIVERY_KEYS = new Set(['livraison', 'delivery', 'option_livraison']);
const CANCELLATION_KEYS = new Set(['annulation', 'cancellation', 'politique_annulation']);

function categoryLabel(value = '') {
  return CATEGORY_LABELS[value] || value.replaceAll('_', ' ').replace(/^./, (letter) => letter.toUpperCase());
}

function displayValue(value, t) {
  if (typeof value === 'boolean') return value ? t('common.yes') : t('common.no');
  if (Array.isArray(value)) return value.join(', ');
  if (value && typeof value === 'object') return Object.entries(value).map(([key, item]) => `${key}: ${item}`).join(' · ');
  return String(value);
}

function metadataValue(specs, keys, t) {
  const entry = Object.entries(specs).find(([key]) => keys.has(key.toLowerCase()));
  return entry ? displayValue(entry[1], t) : null;
}

function DetailError({ children }) {
  return <div role="alert" className="rounded-control border border-error/25 bg-error-subtle px-4 py-3 text-sm font-semibold text-error">{children}</div>;
}

function SimilarCard({ item, onSelect }) {
  const { t, cityLabel } = useI18n();
  const image = item.photos?.[0] || item.image;
  return (
    <button type="button" onClick={() => onSelect(item)} className="group min-w-0 overflow-hidden rounded-card border border-border bg-surface text-start shadow-subtle transition hover:-translate-y-0.5 hover:shadow-card focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30">
      <div className="aspect-[4/3] bg-stone-100">
        {image ? <img src={image} alt="" loading="lazy" className="size-full object-cover" /> : <div className="flex size-full items-center justify-center text-muted"><ImageOff className="size-6" /></div>}
      </div>
      <div className="p-3">
        <p className="line-clamp-2 text-sm font-bold leading-5 text-ink">{item.titre || item.title}</p>
        <p className="mt-1 flex items-center gap-1 text-xs text-muted"><MapPin className="size-3" />{cityLabel(item.city)}</p>
        <div className="mt-3 flex items-end justify-between gap-2">
          <PriceDisplay amount={item.prix_par_jour ?? item.daily_price_mad} period={t('equipment.day')} size="sm" />
          <ChevronRight className="rtl-flip size-4 text-primary transition-transform group-hover:translate-x-0.5" />
        </div>
      </div>
    </button>
  );
}

export default function EquipmentModal({
  equipment,
  onClose,
  isAuthenticated,
  isKYCVerified,
  onOpenKYC,
  onOpenAuth,
  onBookingSuccess,
  onSelectSimilar,
}) {
  const { t, cityLabel, formatAddress, formatDate, formatNumber } = useI18n();
  const [detail, setDetail] = useState(equipment);
  const [detailLoading, setDetailLoading] = useState(true);
  const [detailError, setDetailError] = useState('');
  const [activeImage, setActiveImage] = useState(0);
  const [reviews, setReviews] = useState([]);
  const [reviewsError, setReviewsError] = useState('');
  const [similar, setSimilar] = useState([]);
  const scrollRootRef = useRef(null);
  const dialogRef = useRef(null);
  useDialogLayer(true, onClose, dialogRef);

  useEffect(() => {
    const controller = new AbortController();
    let current = true;
    scrollRootRef.current?.scrollTo({ top: 0 });
    setDetail(equipment);
    setDetailLoading(true);
    setDetailError('');
    setActiveImage(0);
    setReviews([]);
    setReviewsError('');
    setSimilar([]);

    const load = async () => {
      try {
        const loaded = await getEquipment(equipment.id, { signal: controller.signal });
        if (!current) return;
        setDetail(loaded);
        const ownerId = loaded.loueur?.id || loaded.loueur_id;
        const [reviewResult, similarResult] = await Promise.allSettled([
          ownerId ? getUserReviews(ownerId, { signal: controller.signal }) : Promise.resolve([]),
          getEquipmentPage({ category: loaded.categorie, available: true, limit: 4, offset: 0 }, { signal: controller.signal }),
        ]);
        if (!current) return;
        if (reviewResult.status === 'fulfilled') setReviews(reviewResult.value || []);
        else if (reviewResult.reason?.code !== 'REQUEST_CANCELLED') setReviewsError(t('equipment.reviewsUnavailable'));
        if (similarResult.status === 'fulfilled') {
          setSimilar(similarResult.value.items.filter((item) => item.id !== loaded.id).slice(0, 3));
        }
      } catch (error) {
        if (error.code !== 'REQUEST_CANCELLED' && current) {
          setDetailError(t('equipment.detailPartial'));
        }
      } finally {
        if (current) setDetailLoading(false);
      }
    };
    load();
    return () => { current = false; controller.abort(); };
  }, [equipment, t]);

  const specs = detail.specs || detail.specs_json || {};
  const rules = metadataValue(specs, RULE_KEYS, t);
  const delivery = metadataValue(specs, DELIVERY_KEYS, t);
  const cancellation = metadataValue(specs, CANCELLATION_KEYS, t);
  const visibleSpecs = Object.entries(specs).filter(([key]) => {
    const normalized = key.toLowerCase();
    return !RULE_KEYS.has(normalized) && !DELIVERY_KEYS.has(normalized) && !CANCELLATION_KEYS.has(normalized);
  });
  const images = useMemo(() => [...new Set([...(detail.photos || []), detail.image].filter(Boolean))], [detail]);
  const owner = detail.loueur || {};
  const reviewCount = reviews.length || owner.nombre_avis || 0;
  const actualAverage = reviews.length
    ? reviews.reduce((total, review) => total + Number(review.note), 0) / reviews.length
    : owner.note;
  const available = detail.is_available !== false && detail.statut === 'actif';
  const localizedApproximateAddress = detail.adresse_approximative && detail.city
    ? detail.adresse_approximative.replaceAll(detail.city, cityLabel(detail.city))
    : detail.adresse_approximative;
  const locationLabel = localizedApproximateAddress
    ? detail.city && !detail.adresse_approximative.toLowerCase().includes(detail.city.toLowerCase())
      ? formatAddress({ address: localizedApproximateAddress, city: detail.city })
      : localizedApproximateAddress
    : cityLabel(detail.city) || null;

  return (
    <div ref={scrollRootRef} className="fixed inset-0 z-50 overflow-y-auto bg-slate-950/70 p-0 sm:p-4" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <article ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="equipment-detail-title" tabIndex="-1" className="mx-auto min-h-screen w-full max-w-7xl overflow-hidden bg-canvas shadow-raised sm:my-4 sm:min-h-0 sm:rounded-modal">
        <header className="sticky top-0 z-30 flex min-h-16 items-center justify-between gap-4 border-b border-border bg-surface/95 px-4 backdrop-blur sm:px-6">
          <div className="min-w-0"><p className="text-xs font-bold uppercase tracking-wider text-primary">{t('equipment.detailEyebrow')}</p><p className="truncate text-sm font-semibold text-ink">{detail.titre || detail.title}</p></div>
          <Button variant="ghost" size="icon" onClick={onClose} aria-label={t('equipment.close')}><X className="size-5" /></Button>
        </header>

        <div className="p-4 pb-28 sm:p-6 sm:pb-28 lg:p-8">
          {detailError && <DetailError>{detailError}</DetailError>}
          <div className="grid gap-8 lg:grid-cols-[minmax(0,1.65fr)_minmax(22rem,0.75fr)] lg:items-start">
            <div className="min-w-0 space-y-8">
              <section aria-label={t('equipment.gallery')}>
                <div className="aspect-[4/3] overflow-hidden rounded-card bg-stone-100 sm:aspect-[16/9]">
                  {detailLoading && !images.length ? <Skeleton className="size-full" /> : images.length ? <img src={images[activeImage]} alt={`${detail.titre || detail.title} — ${t('equipment.photoAria', { number: formatNumber(activeImage + 1) })}`} className="size-full object-cover" /> : <div className="flex size-full flex-col items-center justify-center gap-2 text-muted"><ImageOff className="size-9" /><span className="text-sm font-semibold">{t('equipment.photoUnavailable')}</span></div>}
                </div>
                {images.length > 1 && <div className="mt-3 flex gap-2 overflow-x-auto pb-1">{images.map((image, index) => <button key={image} type="button" onClick={() => setActiveImage(index)} aria-label={t('equipment.photoAria', { number: formatNumber(index + 1) })} className={`h-16 w-24 shrink-0 overflow-hidden rounded-control border-2 ${index === activeImage ? 'border-primary' : 'border-transparent'}`}><img src={image} alt="" className="size-full object-cover" /></button>)}</div>}
              </section>

              <section>
                <div className="flex flex-wrap items-center gap-2"><Badge>{t(`category.${detail.categorie || detail.category}`, {}, categoryLabel(detail.categorie || detail.category))}</Badge><Badge variant={available ? 'success' : 'warning'} icon={PackageCheck}>{available ? t('equipment.available') : t('equipment.unavailable')}</Badge></div>
                <h1 id="equipment-detail-title" className="mt-4 font-display text-3xl font-bold tracking-tight text-ink sm:text-4xl">{detail.titre || detail.title}</h1>
                <p className="mt-3 flex items-center gap-2 text-sm text-muted"><MapPin className="size-4 text-primary" />{locationLabel || t('equipment.locationMissing')}</p>
              </section>

              <Card className="p-5 sm:p-6">
                <p className="text-xs font-bold uppercase tracking-wider text-muted">{t('equipment.owner')}</p>
                <div className="mt-4 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
                  <div className="flex items-center gap-3"><Avatar src={owner.avatar_url} name={owner.nom || detail.loueur_nom || t('equipment.owner')} size="lg" fallback={<UserRound className="size-5" />} /><div><p className="font-bold text-ink">{owner.nom || detail.loueur_nom || t('equipment.ownerProfile')}</p>{owner.company_name && <p className="text-xs text-muted">{owner.company_name}</p>}{actualAverage != null && reviewCount > 0 ? <Rating value={actualAverage} count={reviewCount} className="mt-1" /> : <p className="mt-1 text-xs text-muted">{t('equipment.noReviews')}</p>}</div></div>
                  <div className="flex flex-wrap gap-2">{owner.badge_verifie && <TrustBadge />}{owner.total_annonces != null && <Badge>{t(owner.total_annonces === 1 ? 'equipment.oneActiveListing' : 'equipment.activeListings', { count: formatNumber(owner.total_annonces) })}</Badge>}{owner.date_inscription && <Badge icon={Clock3}>{t('equipment.memberSince', { date: formatDate(owner.date_inscription, { month: 'long', year: 'numeric' }) })}</Badge>}</div>
                </div>
              </Card>

              <section><h2 className="font-display text-2xl font-bold text-ink">{t('equipment.description')}</h2><p className="mt-3 whitespace-pre-line text-sm leading-7 text-muted">{detail.description || t('equipment.noDescription')}</p></section>

              <section>
                <h2 className="font-display text-2xl font-bold text-ink">{t('equipment.specifications')}</h2>
                {visibleSpecs.length ? <dl className="mt-4 grid gap-3 sm:grid-cols-2">{visibleSpecs.map(([key, value]) => <div key={key} className="rounded-control border border-border bg-surface p-4"><dt className="text-xs font-bold uppercase tracking-wider text-muted">{key.replaceAll('_', ' ')}</dt><dd className="mt-1 font-semibold text-ink">{displayValue(value, t)}</dd></div>)}</dl> : <p className="mt-3 text-sm text-muted">{t('equipment.noSpecifications')}</p>}
              </section>

              <section className="grid gap-4 sm:grid-cols-2">
                <Card className="p-5"><div className="flex items-center gap-2 font-bold text-ink"><MapPin className="size-4 text-primary" /> {t('equipment.pickup')}</div><p className="mt-2 text-sm leading-6 text-muted">{locationLabel ? t('equipment.pickupPlace', { address: locationLabel }) : t('equipment.pickupMissing')} {t('equipment.pickupConfirm')}</p></Card>
                <Card className="p-5"><div className="flex items-center gap-2 font-bold text-ink"><Truck className="size-4 text-primary" /> {t('equipment.delivery')}</div><p className="mt-2 text-sm leading-6 text-muted">{delivery || t('equipment.deliveryMissing')}</p></Card>
                <Card className="p-5"><div className="flex items-center gap-2 font-bold text-ink"><FileText className="size-4 text-primary" /> {t('equipment.rules')}</div><p className="mt-2 text-sm leading-6 text-muted">{rules || t('equipment.rulesMissing')}</p></Card>
                <Card className="p-5"><div className="flex items-center gap-2 font-bold text-ink"><CalendarDays className="size-4 text-primary" /> {t('equipment.cancellation')}</div><p className="mt-2 text-sm leading-6 text-muted">{cancellation || t('equipment.cancellationMissing')}</p></Card>
              </section>

              <section>
                <div className="flex items-end justify-between gap-4"><div><h2 className="font-display text-2xl font-bold text-ink">{t('equipment.ownerReviews')}</h2><p className="mt-1 text-sm text-muted">{t('equipment.reviewSource')}</p></div>{actualAverage != null && reviewCount > 0 && <div className="flex items-center gap-1 font-display text-2xl font-bold text-ink"><Star className="size-5 fill-amber-400 text-amber-500" />{formatNumber(actualAverage, { maximumFractionDigits: 1 })}</div>}</div>
                {reviewsError ? <div className="mt-4"><DetailError>{reviewsError}</DetailError></div> : reviews.length ? <div className="mt-4 grid gap-3 sm:grid-cols-2">{reviews.map((review) => <Card key={review.id} className="p-4"><Rating value={review.note} /><p className="mt-3 text-sm leading-6 text-ink">{review.commentaire || t('equipment.reviewWithoutComment')}</p><p className="mt-3 text-xs font-semibold text-muted">{review.avisateur_nom}</p></Card>)}</div> : <p className="mt-4 rounded-control border border-dashed border-border p-5 text-sm text-muted">{t('equipment.ownerNoReviews')}</p>}
              </section>

              {similar.length > 0 && <section><h2 className="font-display text-2xl font-bold text-ink">{t('equipment.similar')}</h2><div className="mt-4 grid gap-4 sm:grid-cols-3">{similar.map((item) => <SimilarCard key={item.id} item={item} onSelect={(selected) => onSelectSimilar?.(selected)} />)}</div></section>}
            </div>

            <aside id="booking-panel" className="scroll-mt-20 lg:sticky lg:top-24" aria-label={t('equipment.bookingAria')}>
              {available ? <Card className="overflow-hidden border-primary/15 shadow-card"><ReservationJourney key={detail.id} equipment={detail} ownerName={owner.nom || detail.loueur_nom || t('equipment.owner')} isAuthenticated={isAuthenticated} isKYCVerified={isKYCVerified} onOpenKYC={onOpenKYC} onOpenAuth={onOpenAuth} onBookingSuccess={onBookingSuccess} onClose={onClose} /></Card> : <Card className="p-5 text-center"><PackageCheck className="mx-auto size-8 text-warning" /><p className="mt-3 font-bold text-ink">{t('equipment.listingUnavailable')}</p><p className="mt-2 text-sm text-muted">{t('equipment.listingUnavailableHelp')}</p></Card>}
            </aside>
          </div>
        </div>
        <div className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-surface/95 px-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-3 shadow-raised backdrop-blur lg:hidden">
          <div className="mx-auto flex max-w-lg items-center justify-between gap-4">
            <PriceDisplay amount={detail.prix_par_jour ?? detail.daily_price_mad} period={t('equipment.day')} size="sm" />
            <Button variant="action" onClick={() => document.getElementById('booking-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' })}>{t('equipment.viewDates')}</Button>
          </div>
        </div>
      </article>
    </div>
  );
}
