import React, { useEffect, useRef, useState } from 'react';
import {
  ArrowLeft, CalendarDays, Check, CheckCircle2, CircleAlert, Clock3,
  FileCheck2, LockKeyhole, MapPin, PackageCheck, ShieldCheck, WalletCards,
} from 'lucide-react';
import { calculatePricing, createBooking } from '../services/api';
import { Badge, Button, Card, Checkbox, Input, Skeleton } from './ui';
import { useI18n } from '../i18n';

const REQUEST_STEPS = ['dates', 'fulfilment', 'verification', 'review'];

function todayString(offsetDays = 0) {
  const value = new Date();
  value.setDate(value.getDate() + offsetDays);
  return value.toISOString().slice(0, 10);
}

function Progress({ current, complete }) {
  const { t } = useI18n();
  return (
    <ol aria-label={t('booking.progressAria')} className="grid grid-cols-4 gap-2">
      {REQUEST_STEPS.map((stepKey, index) => {
        const done = complete || index < current;
        const active = !complete && index === current;
        return (
          <li key={stepKey} aria-current={active ? 'step' : undefined}>
            <div className={`h-1.5 rounded-full ${done ? 'bg-primary' : active ? 'bg-action' : 'bg-stone-200'}`} />
            <p className={`mt-2 text-[10px] font-bold ${done || active ? 'text-ink' : 'text-muted'}`}>{t(`booking.steps.${stepKey}`)}</p>
          </li>
        );
      })}
    </ol>
  );
}

function SummaryRow({ label, value, strong = false, note }) {
  return (
    <div className="flex flex-col items-start gap-1 py-2 sm:flex-row sm:justify-between sm:gap-4">
      <div><dt className="text-xs text-muted">{label}</dt>{note && <p className="mt-0.5 max-w-44 text-[10px] leading-4 text-muted">{note}</p>}</div>
      <dd className={`break-words text-start text-xs sm:max-w-[58%] sm:text-end ${strong ? 'font-display text-base font-bold text-ink' : 'font-semibold text-ink'}`}>{value}</dd>
    </div>
  );
}

function BookingSummary({ equipment, ownerName, startDate, endDate, pricing }) {
  const { t, formatDate, formatMAD, formatNumber } = useI18n();
  const daysLabel = pricing ? t(pricing.nombre_jours === 1 ? 'booking.oneDay' : 'booking.days', { count: formatNumber(pricing.nombre_jours) }) : t('booking.toCalculate');
  return (
    <div className="rounded-card border border-border bg-canvas p-4" aria-label={t('booking.summaryAria')}>
      <div className="flex items-start gap-3 border-b border-border pb-3">
        <div className="flex size-9 shrink-0 items-center justify-center rounded-control bg-primary-subtle text-primary"><PackageCheck className="size-4" /></div>
        <div className="min-w-0"><p className="line-clamp-2 text-sm font-bold text-ink">{equipment.titre || equipment.title}</p><p className="mt-0.5 text-xs text-muted">{t('booking.owner', { name: ownerName })}</p></div>
      </div>
      <dl className="mt-1 divide-y divide-border">
        <SummaryRow label={t('booking.dates')} value={`${formatDate(startDate, { day: 'numeric', month: 'short', year: 'numeric' }) || t('booking.toChoose')} – ${formatDate(endDate, { day: 'numeric', month: 'short', year: 'numeric' }) || t('booking.toChoose')}`} />
        <SummaryRow label={t('booking.duration')} value={daysLabel} />
        <SummaryRow label={t('booking.handover')} value={t('booking.pickupOnSite')} />
        <SummaryRow label={t('booking.rental')} value={pricing ? formatMAD(pricing.total_location_mad) : t('booking.toCalculate')} strong />
        <SummaryRow label={t('booking.platformFee')} value={pricing ? formatMAD(pricing.frais_service_plateforme_mad) : t('booking.toCalculate')} note={t('booking.platformFeeNote')} />
        <SummaryRow label={t('booking.deposit')} value={formatMAD(pricing ? pricing.montant_caution_mad : equipment.montant_caution || 0)} strong note={t('booking.depositDistinct')} />
        <SummaryRow label={t('booking.handoverTotal')} value={pricing ? formatMAD(pricing.total_a_payer_a_la_remise_mad) : t('booking.toCalculate')} strong note={t('booking.totalNote')} />
      </dl>
    </div>
  );
}

function FutureLifecycle() {
  const { t } = useI18n();
  const phases = [
    [t('booking.future.owner'), Clock3, t('booking.future.ownerHelp')],
    [t('booking.future.contract'), FileCheck2, t('booking.future.contractHelp')],
    [t('booking.future.payment'), WalletCards, t('booking.future.paymentHelp')],
    [t('booking.future.confirmation'), LockKeyhole, t('booking.future.confirmationHelp')],
  ];
  return (
    <div className="rounded-card border border-border bg-surface p-4">
      <p className="text-xs font-bold uppercase tracking-wider text-muted">{t('booking.afterSubmit')}</p>
      <ol className="mt-3 space-y-3">
        {phases.map(([label, Icon, description]) => <li key={label} className="flex gap-3"><span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-stone-100 text-muted"><Icon className="size-4" /></span><div><p className="text-xs font-bold text-ink">{label}</p><p className="mt-0.5 text-[11px] leading-4 text-muted">{description}</p></div></li>)}
      </ol>
    </div>
  );
}

export default function ReservationJourney({
  equipment,
  ownerName,
  isAuthenticated,
  isKYCVerified,
  onOpenKYC,
  onOpenAuth,
  onBookingSuccess,
  onClose,
}) {
  const { t, formatMAD, formatNumber } = useI18n();
  const [step, setStep] = useState(0);
  const [startDate, setStartDate] = useState(todayString());
  const [endDate, setEndDate] = useState(todayString(2));
  const [pricing, setPricing] = useState(null);
  const [pricingLoading, setPricingLoading] = useState(true);
  const [pricingError, setPricingError] = useState('');
  const [conflictError, setConflictError] = useState('');
  const [submitError, setSubmitError] = useState(null);
  const [acknowledged, setAcknowledged] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [booking, setBooking] = useState(null);
  const submittingRef = useRef(false);
  const datesValid = Boolean(startDate && endDate && endDate >= startDate && startDate >= todayString());
  const kycRequired = Boolean(equipment.kyc_requis || equipment.niveau_risque === 'eleve');
  const verificationReady = Boolean(isAuthenticated && (!kycRequired || isKYCVerified));

  useEffect(() => {
    const controller = new AbortController();
    setAcknowledged(false);
    setConflictError('');
    setSubmitError(null);
    if (!datesValid) {
      setPricing(null);
      setPricingLoading(false);
      setPricingError(t('booking.invalidDates'));
      return () => controller.abort();
    }
    setPricingLoading(true);
    setPricingError('');
    const timer = setTimeout(async () => {
      try {
        const result = await calculatePricing(equipment.id, startDate, endDate, { signal: controller.signal });
        setPricing(result);
      } catch (error) {
        if (error.code !== 'REQUEST_CANCELLED') {
          setPricing(null);
          setPricingError(t('booking.pricingUnavailable'));
        }
      } finally {
        if (!controller.signal.aborted) setPricingLoading(false);
      }
    }, 250);
    return () => { clearTimeout(timer); controller.abort(); };
  }, [equipment.id, startDate, endDate, datesValid, t]);

  const submit = async () => {
    if (submittingRef.current || !pricing || !acknowledged) return;
    submittingRef.current = true;
    setIsSubmitting(true);
    setSubmitError(null);
    let succeeded = false;
    try {
      const record = await createBooking(equipment.id, startDate, endDate);
      succeeded = true;
      setBooking(record);
      onBookingSuccess?.(record);
    } catch (error) {
      if (error.code === 'BOOKING_DATE_UNAVAILABLE') {
        setConflictError(t('booking.unavailable'));
        setStep(0);
      } else if (error.code === 'KYC_REQUIRED') {
        setSubmitError({ code: error.code, message: t('booking.kycRequired') });
        setStep(2);
      } else if (error.code === 'AUTH_REQUIRED') {
        setSubmitError({ code: error.code, message: t('booking.authRequired') });
      } else if (error.code === 'FORBIDDEN') {
        setSubmitError({ code: error.code, message: t('booking.forbidden') });
      } else {
        setSubmitError({ code: error.code || 'BOOKING_FAILED', message: error.message || t('booking.failed') });
      }
    } finally {
      if (!succeeded) submittingRef.current = false;
      setIsSubmitting(false);
    }
  };

  if (booking) {
    const reservationId = booking.reservation_id || booking.id;
    return (
      <div className="space-y-5 p-5">
        <Progress current={4} complete />
        <div className="rounded-card border border-success/25 bg-success-subtle p-5 text-center"><CheckCircle2 className="mx-auto size-10 text-success" /><h2 className="mt-3 font-display text-xl font-bold text-ink">{t('booking.sent')}</h2><Badge variant="warning" className="mt-3">{t('booking.awaitingOwner')}</Badge><p className="mt-3 text-sm leading-6 text-muted">{t('booking.reference', { id: String(reservationId).slice(0, 8).toUpperCase() })}</p></div>
        <BookingSummary equipment={equipment} ownerName={ownerName} startDate={startDate} endDate={endDate} pricing={pricing} />
        <FutureLifecycle />
        <Button className="w-full" onClick={onClose}>{t('booking.closeAndTrack')}</Button>
      </div>
    );
  }

  return (
    <div className="space-y-5 p-5">
      <Progress current={step} />
      <BookingSummary equipment={equipment} ownerName={ownerName} startDate={startDate} endDate={endDate} pricing={pricing} />

      {step === 0 && <section aria-labelledby="booking-dates-title">
        <h2 id="booking-dates-title" className="font-display text-lg font-bold text-ink">{t('booking.chooseDates')}</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2"><Input label={t('booking.start')} type="date" min={todayString()} value={startDate} onChange={(event) => setStartDate(event.target.value)} error={conflictError || undefined} /><Input label={t('booking.end')} type="date" min={startDate || todayString()} value={endDate} onChange={(event) => setEndDate(event.target.value)} /></div>
        {pricingLoading ? <Skeleton className="mt-4 h-16 rounded-control" /> : pricingError && <div role="alert" className="mt-4 rounded-control border border-error/25 bg-error-subtle p-3 text-xs font-semibold text-error">{pricingError}</div>}
        {pricing && <div className="mt-4 rounded-control border border-primary/20 bg-primary-subtle p-3 text-xs text-primary"><Check className="me-1 inline size-4" />{t('booking.quoteReady', { days: t(pricing.nombre_jours === 1 ? 'booking.oneDay' : 'booking.days', { count: formatNumber(pricing.nombre_jours) }) })}</div>}
      </section>}

      {step === 1 && <section aria-labelledby="booking-handover-title"><h2 id="booking-handover-title" className="font-display text-lg font-bold text-ink">{t('booking.handoverMode')}</h2><div className="mt-4 rounded-card border-2 border-primary/30 bg-primary-subtle p-4"><div className="flex items-center gap-2 font-bold text-primary"><MapPin className="size-4" /> {t('booking.pickupOnSite')}</div><p className="mt-2 text-xs leading-5 text-muted">{t('booking.pickupHelp')}</p></div><div className="mt-3 rounded-card border border-dashed border-border p-4"><p className="text-sm font-bold text-muted">{t('booking.deliveryUnavailable')}</p><p className="mt-1 text-xs leading-5 text-muted">{t('booking.deliveryUnavailableHelp')}</p></div></section>}

      {step === 2 && <section aria-labelledby="booking-verification-title"><h2 id="booking-verification-title" className="font-display text-lg font-bold text-ink">{t('booking.steps.verification')}</h2>{!isAuthenticated ? <div className="mt-4 rounded-card border border-information/25 bg-information-subtle p-4"><p className="font-bold text-ink">{t('booking.authTitle')}</p><p className="mt-2 text-xs leading-5 text-muted">{t('booking.authHelp')}</p><Button className="mt-4 w-full" onClick={onOpenAuth}>{t('footer.signIn')}</Button></div> : kycRequired ? isKYCVerified ? <div className="mt-4 rounded-card border border-success/25 bg-success-subtle p-4"><div className="flex items-center gap-2 font-bold text-success"><ShieldCheck className="size-4" /> {t('trust.verified')}</div><p className="mt-2 text-xs leading-5 text-muted">{t('booking.verifiedBackend')}</p></div> : <div className="mt-4 rounded-card border border-warning/30 bg-warning-subtle p-4"><p className="font-bold text-ink">{t('booking.verificationRequired')}</p><p className="mt-2 text-xs leading-5 text-muted">{t('booking.verificationHelp')}</p><Button className="mt-4 w-full" onClick={onOpenKYC}>{t('nav.verifyIdentity')}</Button></div> : <div className="mt-4 rounded-card border border-information/25 bg-information-subtle p-4"><p className="font-bold text-information">{t('booking.noVerification')}</p><p className="mt-2 text-xs leading-5 text-muted">{t('booking.noVerificationHelp')}</p></div>}{submitError?.code === 'KYC_REQUIRED' && <p role="alert" className="mt-3 text-xs font-semibold text-error">{submitError.message}</p>}</section>}

      {step === 3 && <section aria-labelledby="booking-review-title"><h2 id="booking-review-title" className="font-display text-lg font-bold text-ink">{t('booking.reviewTitle')}</h2><div className="mt-4 rounded-control border border-information/25 bg-information-subtle p-3 text-xs leading-5 text-information"><CircleAlert className="me-1 inline size-4" />{t('booking.pendingWarning')}</div><Checkbox className="mt-3" checked={acknowledged} onChange={(event) => setAcknowledged(event.target.checked)} label={t('booking.acknowledge')} description={t('booking.acknowledgeHelp')} />{submitError && submitError.code !== 'KYC_REQUIRED' && <div role="alert" className="mt-3 rounded-control border border-error/25 bg-error-subtle p-3 text-xs font-semibold text-error"><p>{submitError.message}</p>{submitError.code === 'AUTH_REQUIRED' && onOpenAuth && <Button variant="secondary" size="sm" className="mt-3" onClick={onOpenAuth}>{t('footer.signIn')}</Button>}</div>}<Button variant="action" size="lg" className="mt-4 w-full" disabled={!acknowledged || !pricing || isSubmitting} onClick={submit}>{isSubmitting ? t('booking.secureSubmit') : t('booking.submit', { price: pricing ? formatMAD(pricing.total_location_mad) : '—' })}</Button></section>}

      <div className="flex gap-3 border-t border-border pt-4">
        {step > 0 && <Button variant="secondary" className="flex-1" onClick={() => { setSubmitError(null); setStep((value) => value - 1); }}><ArrowLeft className="rtl-flip size-4" /> {t('common.back')}</Button>}
        {step < 3 && <Button className="flex-1" disabled={(step === 0 && (!pricing || pricingLoading)) || (step === 2 && !verificationReady)} onClick={() => setStep((value) => value + 1)}>{t('common.continue')}</Button>}
      </div>
      <FutureLifecycle />
    </div>
  );
}
