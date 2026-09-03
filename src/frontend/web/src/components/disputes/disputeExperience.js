export const DISPUTE_REASONS = [
  { value: 'equipment_condition', label: 'État du matériel' },
  { value: 'missing_accessory', label: 'Accessoire ou élément manquant' },
  { value: 'late_return', label: 'Délai de retour' },
  { value: 'handover_problem', label: 'Remise ou retour du matériel' },
  { value: 'payment_issue', label: 'Paiement ou dépôt' },
  { value: 'cancellation', label: 'Annulation' },
  { value: 'other', label: 'Autre situation' },
];

export const DISPUTE_STEPS = [
  { key: 'open', label: 'Ouvert' },
  { key: 'evidence_collection', label: 'Collecte' },
  { key: 'under_review', label: 'Examen' },
  { key: 'decision', label: 'Décision' },
  { key: 'resolved', label: 'Résolu' },
];

export const DISPUTE_STATUS = {
  open: { label: 'Dossier ouvert', tone: 'info', step: 0 },
  evidence_collection: { label: 'Collecte des éléments', tone: 'warning', step: 1 },
  under_review: { label: 'En cours d’examen', tone: 'info', step: 2 },
  decision: { label: 'Décision enregistrée', tone: 'warning', step: 3 },
  resolved: { label: 'Dossier résolu', tone: 'success', step: 4 },
};

export const DISPUTE_ELIGIBLE_BOOKING_STATUSES = new Set([
  'confirmee', 'prete_remise', 'en_cours', 'en_attente_validation', 'termine', 'en_litige',
]);

export function disputeStatus(value) {
  return DISPUTE_STATUS[value] || { label: 'Statut indisponible', tone: 'neutral', step: 0 };
}

export function disputeReason(value) {
  return DISPUTE_REASONS.find((item) => item.value === value)?.label || 'Autre situation';
}

export function disputeDecision(dispute) {
  const decisions = {
    no_financial_adjustment: 'Aucun ajustement financier',
    release_deposit: 'Libération du dépôt',
    partial_deposit_capture: 'Retenue partielle sur le dépôt',
    full_deposit_capture: 'Retenue du dépôt',
  };
  return decisions[dispute?.decision_code] || null;
}

export function disputeDepositStatus(value) {
  return {
    not_applicable: 'Aucun traitement du dépôt requis',
    pending_provider: 'Confirmation du prestataire attendue',
    confirmed: 'Traitement confirmé par le prestataire',
    failed: 'Traitement non confirmé',
  }[value] || null;
}

export function canOpenDispute(booking, disputes = []) {
  if (!DISPUTE_ELIGIBLE_BOOKING_STATUSES.has(booking?.statut_reservation)) return false;
  return !disputes.some((item) => String(item.booking_id) === String(booking.id) && item.status !== 'resolved');
}

export function disputeSubmissionKey(bookingId, storage = globalThis.sessionStorage) {
  const storageKey = `lokiini:dispute:${bookingId}`;
  try {
    const existing = storage?.getItem(storageKey);
    if (existing) return existing;
  } catch { /* continue with an in-memory key */ }
  const suffix = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const key = `web-dispute-${bookingId}-${suffix}`.slice(0, 128);
  try { storage?.setItem(storageKey, key); } catch { /* no-op */ }
  return key;
}
