import * as Crypto from 'expo-crypto';
import { apiClient } from './apiClient';

export async function getInspectionRequirements(bookingId) {
  return apiClient.get(`/inspections/bookings/${encodeURIComponent(String(bookingId))}/requirements`);
}

export async function getBookingInspections(bookingId) {
  return apiClient.get(`/inspections/bookings/${encodeURIComponent(String(bookingId))}`);
}

export async function computeFileHash(uri) {
  try {
    const response = await fetch(uri);
    const blob = await response.blob();
    const reader = new FileReader();
    return new Promise((resolve, reject) => {
      reader.onload = async () => {
        try {
          const binaryString = reader.result;
          const hash = await Crypto.digestStringAsync(
            Crypto.CryptoDigestAlgorithm.SHA256,
            binaryString,
          );
          resolve(hash);
        } catch (err) {
          reject(err);
        }
      };
      reader.onerror = reject;
      reader.readAsBinaryString(blob);
    });
  } catch {
    return null;
  }
}

export async function uploadInspectionEvidence({ bookingId, inspectionType, fileUri, filename, contentType = 'image/jpeg' }) {
  const formData = new FormData();
  formData.append('booking_id', bookingId);
  formData.append('inspection_type', inspectionType);
  formData.append('evidence_file', {
    uri: fileUri,
    name: filename || `evidence-${Date.now()}.jpg`,
    type: contentType,
  });

  return apiClient.upload('/inspections/evidence', formData);
}

export async function submitStructuredInspection({
  bookingId,
  inspectionType,
  evidenceIds,
  condition = 'good',
  existingDamage = null,
  accessories = [],
  serialNumber = null,
  meterType = null,
  meterReading = null,
  notes = null,
  confirmed = true,
  idempotencyKey = null,
}) {
  const headers = {};
  if (idempotencyKey) {
    headers['Idempotency-Key'] = idempotencyKey;
  }

  return apiClient.post('/inspections', {
    booking_id: bookingId,
    inspection_type: inspectionType,
    evidence_ids: evidenceIds,
    condition,
    existing_damage: existingDamage,
    accessories,
    serial_number: serialNumber,
    meter_type: meterType,
    meter_reading: meterReading,
    notes,
    confirmed,
  }, { headers });
}

export async function confirmInspection(inspectionId, { confirmed = true, notes = null } = {}) {
  return apiClient.post(`/inspections/${encodeURIComponent(String(inspectionId))}/confirm`, {
    confirmed,
    notes,
  });
}
