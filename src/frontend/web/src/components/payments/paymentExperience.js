const UNKNOWN = Object.freeze({
  key: 'unknown', label: 'Statut indisponible', tone: 'neutral', confirmed: false,
});

const RENTAL_PAYMENT_STATES = Object.freeze({
  not_started: { key: 'not_started', label: 'À payer', tone: 'neutral', confirmed: false },
  pending: { key: 'pending', label: 'Paiement en cours', tone: 'warning', confirmed: false },
  requires_action: { key: 'requires_action', label: 'Action requise', tone: 'warning', confirmed: false },
  succeeded: { key: 'succeeded', label: 'Payé', tone: 'success', confirmed: true },
  failed: { key: 'failed', label: 'Paiement échoué', tone: 'error', confirmed: false },
  cancelled: { key: 'cancelled', label: 'Paiement annulé', tone: 'neutral', confirmed: false },
  partially_refunded: { key: 'partially_refunded', label: 'Partiellement remboursé', tone: 'warning', confirmed: true },
  refunded: { key: 'refunded', label: 'Remboursé', tone: 'neutral', confirmed: true },
});

const DEPOSIT_STATES = Object.freeze({
  not_started: { key: 'not_started', label: 'Non autorisé', tone: 'neutral', confirmed: false },
  authorization_pending: { key: 'authorization_pending', label: 'Autorisation en cours', tone: 'warning', confirmed: false },
  authorized: { key: 'authorized', label: 'Autorisé', tone: 'info', confirmed: true },
  authorization_failed: { key: 'authorization_failed', label: 'Autorisation échouée', tone: 'error', confirmed: false },
  released: { key: 'released', label: 'Libéré', tone: 'success', confirmed: true },
  partially_captured: { key: 'partially_captured', label: 'Partiellement retenu', tone: 'warning', confirmed: true },
  captured: { key: 'captured', label: 'Retenu', tone: 'error', confirmed: true },
});

const REFUND_STATES = Object.freeze({
  pending: { key: 'pending', label: 'Remboursement en cours', tone: 'warning', confirmed: false },
  succeeded: { key: 'succeeded', label: 'Remboursé', tone: 'success', confirmed: true },
  failed: { key: 'failed', label: 'Remboursement échoué', tone: 'error', confirmed: false },
});

const PAYOUT_STATES = Object.freeze({
  not_ready: { key: 'not_ready', label: 'Pas encore disponible', tone: 'neutral', confirmed: false },
  pending: { key: 'pending', label: 'Versement en cours', tone: 'warning', confirmed: false },
  paid: { key: 'paid', label: 'Versé', tone: 'success', confirmed: true },
  failed: { key: 'failed', label: 'Versement échoué', tone: 'error', confirmed: false },
  reversed: { key: 'reversed', label: 'Versement annulé', tone: 'error', confirmed: false },
});

export function rentalPaymentStatus(status) {
  return RENTAL_PAYMENT_STATES[status] || UNKNOWN;
}

export function securityDepositStatus(status) {
  return DEPOSIT_STATES[status] || UNKNOWN;
}

export function refundStatus(status) {
  return REFUND_STATES[status] || UNKNOWN;
}

export function ownerPayoutStatus(status) {
  return PAYOUT_STATES[status] || UNKNOWN;
}

export function canInitiateRentalPayment({ booking, financial, userId }) {
  const isRenter = String(booking?.locataire_id || '') === String(userId || '');
  const paymentState = rentalPaymentStatus(financial?.rental_payment?.status).key;
  return isRenter
    && booking?.statut_reservation === 'paiement_en_attente'
    && ['not_started', 'failed', 'requires_action'].includes(paymentState);
}

export function paymentActionLabel(status) {
  if (status === 'failed') return 'Réessayer le paiement';
  if (status === 'requires_action') return 'Continuer le paiement';
  return 'Procéder au paiement';
}

export function paymentAttemptMessage(error) {
  if (error?.code === 'PAYMENT_PROVIDER_UNAVAILABLE') {
    return 'Le service de paiement est temporairement indisponible. Aucun paiement n’a été confirmé. Vous pourrez réessayer avec la même tentative sécurisée.';
  }
  if (['NETWORK_ERROR', 'REQUEST_TIMEOUT'].includes(error?.code)) {
    return 'La confirmation n’a pas été reçue. Actualisez d’abord le statut, puis réessayez si le paiement reste non confirmé.';
  }
  return error?.message || 'Le paiement n’a pas pu être démarré. Actualisez le statut avant de réessayer.';
}

export function createPaymentIdempotencyKey(bookingId) {
  const suffix = globalThis.crypto?.randomUUID?.()
    || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  return `web-payment-${bookingId}-${suffix}`.slice(0, 128);
}

function attemptStorageKey(bookingId) {
  return `lokiini:payment-attempt:${bookingId}`;
}

export function getOrCreatePaymentAttempt(bookingId, sourceStatus, storage = globalThis.sessionStorage) {
  let existing = null;
  try {
    existing = JSON.parse(storage?.getItem(attemptStorageKey(bookingId)) || 'null');
  } catch {
    existing = null;
  }
  const needsNewAttempt = !existing?.key
    || (sourceStatus === 'failed' && existing.sourceStatus !== 'failed');
  if (!needsNewAttempt) return existing;
  const attempt = { key: createPaymentIdempotencyKey(bookingId), sourceStatus };
  try {
    storage?.setItem(attemptStorageKey(bookingId), JSON.stringify(attempt));
  } catch {
    // In-memory duplicate protection remains active when session storage is unavailable.
  }
  return attempt;
}

export function clearPaymentAttempt(bookingId, storage = globalThis.sessionStorage) {
  try {
    storage?.removeItem(attemptStorageKey(bookingId));
  } catch {
    // Storage availability must not change the backend-authoritative payment status.
  }
}
