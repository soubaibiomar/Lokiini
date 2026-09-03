export const INSPECTION_STEPS = ['Preuves', 'État', 'Détails', 'Confirmation'];

export const CONDITION_OPTIONS = [
  { value: 'excellent', label: 'Excellent état' },
  { value: 'good', label: 'Bon état' },
  { value: 'fair', label: 'État d’usage' },
  { value: 'damaged', label: 'Endommagé' },
];

export const METER_OPTIONS = [
  { value: 'none', label: 'Aucun compteur pertinent' },
  { value: 'hours', label: 'Compteur d’heures' },
  { value: 'odometer', label: 'Odomètre / kilométrage' },
];

export function inspectionTypeLabel(type) {
  return type === 'check_out' ? 'Check-out · retour' : 'Check-in · remise';
}

export function inspectionConditionLabel(condition) {
  return CONDITION_OPTIONS.find((item) => item.value === condition)?.label || 'Non renseigné';
}

export function validateInspectionStep(step, {
  evidence, requirements, condition, serialRelevant, serialNumber,
  meterType, meterReading, confirmed,
}) {
  const uploaded = evidence.filter((item) => item.status === 'uploaded' && item.record);
  if (step === 0) {
    const photos = uploaded.filter((item) => item.record.media_kind === 'photo').length;
    const videos = uploaded.filter((item) => item.record.media_kind === 'video').length;
    if (photos < (requirements?.minimum_photos || 3)) return `Ajoutez au moins ${requirements?.minimum_photos || 3} photos.`;
    if (requirements?.video_required && videos < 1) return 'Une vidéo est requise pour ce matériel.';
    if (evidence.some((item) => ['uploading', 'failed'].includes(item.status))) return 'Terminez ou corrigez les importations avant de continuer.';
  }
  if (step === 1 && !condition) return 'Sélectionnez l’état général du matériel.';
  if (step === 2) {
    if (serialRelevant && !serialNumber.trim()) return 'Saisissez le numéro de série visible.';
    if (meterType !== 'none' && (meterReading === '' || Number(meterReading) < 0)) {
      return 'Saisissez un relevé de compteur valide.';
    }
  }
  if (step === 3 && !confirmed) return 'Confirmez l’exactitude des informations avant l’envoi.';
  return '';
}

export function inspectionPayload({ bookingId, type, evidence, condition, existingDamage, accessories, serialNumber, meterType, meterReading, notes }) {
  return {
    booking_id: bookingId,
    inspection_type: type,
    evidence_ids: evidence.filter((item) => item.status === 'uploaded' && item.record).map((item) => item.record.id),
    condition,
    existing_damage: existingDamage.trim() || null,
    accessories: accessories.split(',').map((item) => item.trim()).filter(Boolean),
    serial_number: serialNumber.trim() || null,
    meter_type: meterType,
    meter_reading: meterType === 'none' ? null : Number(meterReading),
    notes: notes.trim() || null,
    confirmed: true,
  };
}

export function currentUserHasConfirmed(inspection, userId) {
  if (String(inspection?.owner_id) === String(userId)) return Boolean(inspection.confirmed_by_owner);
  if (String(inspection?.renter_id) === String(userId)) return Boolean(inspection.confirmed_by_renter);
  return true;
}

export function inspectionSubmissionKey(bookingId, type, storage = globalThis.sessionStorage) {
  const storageKey = `lokiini:inspection-submit:${bookingId}:${type}`;
  try {
    const existing = storage?.getItem(storageKey);
    if (existing) return existing;
  } catch {
    // Continue with an in-memory key when storage is unavailable.
  }
  const suffix = globalThis.crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(16).slice(2)}`;
  const key = `web-inspection-${bookingId}-${type}-${suffix}`.slice(0, 128);
  try { storage?.setItem(storageKey, key); } catch { /* no-op */ }
  return key;
}
