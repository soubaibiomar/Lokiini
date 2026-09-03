import React, { useCallback, useEffect, useState } from 'react';
import { Check, ExternalLink, RefreshCw, ShieldCheck } from 'lucide-react';

import { getDiditKYCStatus, initiateDiditKYC } from '../services/api';
import { Badge, Button, Modal, Skeleton } from './ui';
import {
  canInitiateKyc, getKycStatus, isKycProcessing, normalizeKycStatus,
} from './kyc/kycExperience';
import { useI18n } from '../i18n';

function errorText(error, fallback) {
  return error?.message || fallback;
}

export default function KYCVerificationModal({ isOpen, onClose, currentUser, onStatusChange }) {
  const { t } = useI18n();
  const [status, setStatus] = useState(() => normalizeKycStatus(currentUser?.statut_verification));
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const refreshStatus = useCallback(async ({ quiet = false } = {}) => {
    if (!currentUser?.id) {
      setErrorMessage(t('kyc.signInRequired'));
      return;
    }
    if (!quiet) setIsLoadingStatus(true);
    setErrorMessage(null);
    try {
      const response = await getDiditKYCStatus(currentUser.id);
      const nextStatus = normalizeKycStatus(response?.status);
      setStatus(nextStatus);
      onStatusChange?.(nextStatus, response);
    } catch (error) {
      if (error?.code !== 'REQUEST_CANCELLED') {
        setErrorMessage(errorText(error, t('kyc.statusUnavailable')));
      }
    } finally {
      if (!quiet) setIsLoadingStatus(false);
    }
  }, [currentUser?.id, onStatusChange, t]);

  useEffect(() => {
    if (!isOpen) return;
    setStatus(normalizeKycStatus(currentUser?.statut_verification));
    setErrorMessage(null);
    refreshStatus();
  }, [isOpen, currentUser?.statut_verification, refreshStatus]);

  const handleStartVerification = async () => {
    setIsProcessing(true);
    setErrorMessage(null);
    try {
      const session = await initiateDiditKYC();
      if (!session?.verification_url) throw new Error(t('kyc.linkMissing'));
      const nextStatus = normalizeKycStatus(session.status);
      setStatus(nextStatus);
      onStatusChange?.(nextStatus, session);
      window.location.assign(session.verification_url);
    } catch (error) {
      if (error?.code === 'KYC_IN_PROGRESS') await refreshStatus({ quiet: true });
      setErrorMessage(errorText(error, t('kyc.unavailable')));
    } finally {
      setIsProcessing(false);
    }
  };

  const statusInfo = getKycStatus(status);
  const mayStart = canInitiateKyc(status);
  const processing = isKycProcessing(status);
  const statusKey = statusInfo.key === 'unknown' ? 'UNKNOWN' : statusInfo.key.toUpperCase();
  const reasons = ['fraud', 'renters', 'owners', 'contracts', 'disputes'];

  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      title={t('kyc.title')}
      description={t('kyc.description')}
      size="lg"
    >
      <div className="space-y-6">
        <section aria-labelledby="kyc-current-status" className="rounded-card border border-border bg-stone-50 p-5">
          <div className="flex items-start gap-4">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-primary-subtle text-primary">
              <ShieldCheck aria-hidden="true" className="size-5" />
            </span>
            <div className="min-w-0 flex-1">
              <p id="kyc-current-status" className="text-xs font-bold uppercase tracking-wide text-muted">{t('kyc.currentStatus')}</p>
              {isLoadingStatus ? (
                <div className="mt-3 space-y-2" role="status">
                  <span className="sr-only">{t('kyc.loadingStatus')}</span>
                  <Skeleton className="h-6 w-44" />
                  <Skeleton className="h-4 w-full max-w-lg" />
                </div>
              ) : (
                <>
                  <Badge variant={statusInfo.tone} className="mt-2">{t(`kyc.status.${statusKey}`, {}, statusInfo.label)}</Badge>
                  <p className="mt-3 text-sm leading-6 text-ink">{t(`kyc.status.${statusInfo.key}.description`, {}, statusInfo.description)}</p>
                  <p className="mt-1 text-sm leading-6 text-muted">{t(`kyc.status.${statusInfo.key}.guidance`, {}, statusInfo.guidance)}</p>
                </>
              )}
            </div>
          </div>
        </section>

        {errorMessage && (
          <div role="alert" className="rounded-control border border-error/25 bg-error-subtle px-4 py-3 text-sm font-semibold text-error">
            {errorMessage}
          </div>
        )}

        <section aria-labelledby="kyc-why-title">
          <h3 id="kyc-why-title" className="font-display text-base font-bold text-ink">{t('kyc.why')}</h3>
          <p className="mt-1 text-sm leading-6 text-muted">{t('kyc.reasons.intro')}</p>
          <ul className="mt-4 grid gap-2 sm:grid-cols-2">
            {reasons.map((reason) => (
              <li key={reason} className="flex items-start gap-2 rounded-control bg-stone-50 px-3 py-2.5 text-sm text-ink">
                <Check aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-primary" />
                <span>{t(`kyc.reasons.${reason}`)}</span>
              </li>
            ))}
          </ul>
        </section>

        <section className="rounded-control border border-border px-4 py-3">
          <h3 className="text-sm font-bold text-ink">{t('kyc.dataTitle')}</h3>
          <p className="mt-1 text-xs leading-5 text-muted">{t('kyc.dataDescription')}</p>
        </section>

        <div className="flex flex-col-reverse gap-3 border-t border-border pt-5 sm:flex-row sm:justify-end">
          <Button variant="secondary" onClick={onClose}>{t('common.close')}</Button>
          {(processing || status === 'unknown') && (
            <Button variant="secondary" onClick={() => refreshStatus()} loading={isLoadingStatus} loadingLabel={t('common.refreshing')}>
              <RefreshCw aria-hidden="true" className="size-4" />
              {t('kyc.refreshStatus')}
            </Button>
          )}
          {mayStart && (
            <Button onClick={handleStartVerification} loading={isProcessing} loadingLabel={t('kyc.opening')}>
              {status === 'requires_action' ? t('common.continue') : status === 'rejected' ? t('common.retry') : t('kyc.start')}
              <ExternalLink aria-hidden="true" className="size-4" />
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
