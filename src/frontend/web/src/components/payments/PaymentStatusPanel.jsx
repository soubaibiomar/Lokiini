import React from 'react';
import { CircleAlert, CreditCard, RefreshCw, ShieldCheck, Undo2, WalletCards } from 'lucide-react';
import { Badge, Button } from '../ui';
import {
  canInitiateRentalPayment, ownerPayoutStatus, refundStatus,
  rentalPaymentStatus, securityDepositStatus,
} from './paymentExperience';
import { useI18n } from '../../i18n';


function MoneyLine({ label, value, formatMoney, strong = false }) {
  return (
    <div className="flex items-center justify-between gap-4 py-1.5 text-sm">
      <span className="text-muted">{label}</span>
      <span className={strong ? 'font-bold text-ink' : 'font-semibold text-ink'}>{formatMoney(value)}</span>
    </div>
  );
}


export default function PaymentStatusPanel({
  financial, booking, userId,
  attempt, onInitiate, onRefresh,
}) {
  const { t, formatMAD: formatMoney, formatDate } = useI18n();
  const rentalState = rentalPaymentStatus(financial.rental_payment?.status);
  const depositState = securityDepositStatus(financial.deposit?.status);
  const canInitiate = canInitiateRentalPayment({ booking, financial, userId });
  const refunds = Array.isArray(financial.refunds) ? financial.refunds : [];
  const refundedAmount = refunds.reduce((sum, item) => sum + Number(item.amount_mad || 0), 0);
  const latestRefundState = refundStatus(refunds[0]?.status);
  const payoutState = ownerPayoutStatus(financial.owner_payout?.status);

  return (
    <article className="rounded-card border border-border bg-surface p-5 shadow-subtle">
      <div className="flex flex-col gap-2 border-b border-border pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="font-display text-lg font-bold text-ink">
            {booking?.article_titre || t('payment.booking', { id: String(financial.booking_id).slice(0, 8) })}
          </h3>
          {booking && <p className="mt-1 text-xs text-muted">{formatDate(booking.date_debut)} — {formatDate(booking.date_fin)}</p>}
        </div>
        <Button variant="ghost" size="sm" onClick={onRefresh} disabled={attempt?.loading}>
          <RefreshCw aria-hidden="true" className="size-4" /> {t('payment.refreshStatuses')}
        </Button>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <section aria-label={t('payment.rental')} className="rounded-card border border-primary/15 bg-primary-subtle/35 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white text-primary shadow-subtle"><CreditCard aria-hidden="true" className="size-5" /></span>
              <div><h4 className="text-sm font-bold text-ink">{t('payment.rental')}</h4><p className="mt-1 text-xs leading-5 text-muted">{t('payment.rentalHelp')}</p></div>
            </div>
            <Badge variant={rentalState.tone}>{t(`payment.state.${rentalState.key}`, {}, rentalState.label)}</Badge>
          </div>
          <div className="mt-4 border-t border-primary/10 pt-3">
            <MoneyLine label={t('payment.rentalAmount')} value={financial.rental_payment?.amount_mad} formatMoney={formatMoney} strong />
            <MoneyLine label={t('payment.platformFee')} value={financial.platform_fee?.amount_mad} formatMoney={formatMoney} />
            {refundedAmount > 0 && <MoneyLine label={t('payment.refundedAmount')} value={refundedAmount} formatMoney={formatMoney} />}
          </div>

          {(rentalState.key === 'failed' || attempt?.error) && (
            <div role="alert" className="mt-3 rounded-control border border-error/20 bg-error-subtle p-3 text-xs leading-5 text-error">
              <div className="flex items-start gap-2"><CircleAlert aria-hidden="true" className="mt-0.5 size-4 shrink-0" /><p>{attempt?.error || t('payment.failedHelp')}</p></div>
            </div>
          )}
          {rentalState.key === 'pending' && <p className="mt-3 text-xs leading-5 text-muted">{t('payment.pendingHelp')}</p>}
          {canInitiate && (
            <Button className="mt-4 w-full" loading={attempt?.loading} loadingLabel={t('payment.attempting')} onClick={onInitiate}>
              {t(`payment.action.${rentalState.key}`, {}, t('payment.action.default'))}
            </Button>
          )}
        </section>

        <section aria-label={t('payment.deposit')} className="rounded-card border border-warning/20 bg-warning-subtle/45 p-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-white text-warning shadow-subtle"><ShieldCheck aria-hidden="true" className="size-5" /></span>
              <div><h4 className="text-sm font-bold text-ink">{t('payment.deposit')}</h4><p className="mt-1 text-xs leading-5 text-muted">{t('payment.depositHelp')}</p></div>
            </div>
            <Badge variant={depositState.tone}>{t(`payment.state.${depositState.key}`, {}, depositState.label)}</Badge>
          </div>
          <div className="mt-4 border-t border-warning/15 pt-3">
            <MoneyLine label={t('payment.authorizationAmount')} value={financial.deposit?.authorized_amount_mad} formatMoney={formatMoney} strong />
            <MoneyLine label={t('payment.capturedAmount')} value={financial.deposit?.captured_amount_mad} formatMoney={formatMoney} />
            <MoneyLine label={t('payment.releasedAmount')} value={financial.deposit?.released_amount_mad} formatMoney={formatMoney} />
          </div>
          {depositState.key === 'authorized' && <p className="mt-3 text-xs leading-5 text-muted">{t('payment.authorizedHelp')}</p>}
          {depositState.key === 'released' && <p className="mt-3 text-xs leading-5 text-success">{t('payment.releasedHelp')}</p>}
          {depositState.key === 'partially_captured' && <p className="mt-3 text-xs leading-5 text-warning">{t('payment.partialCaptureHelp')}</p>}
          {depositState.key === 'captured' && <p className="mt-3 text-xs leading-5 text-error">{t('payment.captureHelp')}</p>}
          {depositState.key === 'authorization_failed' && <p className="mt-3 text-xs leading-5 text-error">{t('payment.authorizationFailedHelp')}</p>}
        </section>
      </div>

      {(refunds.length > 0 || financial.owner_payout) && (
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          {refunds.length > 0 && <div className="rounded-control border border-border p-3"><div className="flex items-center justify-between gap-2"><div className="flex items-center gap-2 text-sm font-bold text-ink"><Undo2 aria-hidden="true" className="size-4 text-primary" /> {t('payment.refund')}</div><Badge variant={latestRefundState.tone}>{t(`payment.state.${latestRefundState.key}`, {}, latestRefundState.label)}</Badge></div><p className="mt-2 text-xs font-semibold text-ink">{formatMoney(refundedAmount)}</p></div>}
          {financial.owner_payout && <div className="rounded-control border border-border p-3"><div className="flex items-center justify-between gap-2"><div className="flex items-center gap-2 text-sm font-bold text-ink"><WalletCards aria-hidden="true" className="size-4 text-primary" /> {t('payment.ownerPayout')}</div><Badge variant={payoutState.tone}>{t(`payment.state.${payoutState.key}`, {}, payoutState.label)}</Badge></div><p className="mt-2 text-xs font-semibold text-ink">{formatMoney(financial.owner_payout.amount_mad)}</p></div>}
        </div>
      )}
    </article>
  );
}
