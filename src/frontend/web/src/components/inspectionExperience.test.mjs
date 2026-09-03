import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import {
  currentUserHasConfirmed, inspectionPayload, inspectionSubmissionKey,
  validateInspectionStep,
} from './inspection/inspectionExperience.js';


const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');
const photo = (id) => ({ status: 'uploaded', record: { id, media_kind: 'photo' } });
const video = (id) => ({ status: 'uploaded', record: { id, media_kind: 'video' } });


test('inspection evidence requirements are enforced before continuing', () => {
  assert.match(validateInspectionStep(0, {
    evidence: [photo('1'), photo('2')], requirements: { minimum_photos: 3 },
  }), /au moins 3 photos/);
  assert.match(validateInspectionStep(0, {
    evidence: [photo('1'), photo('2'), photo('3')],
    requirements: { minimum_photos: 3, video_required: true },
  }), /vidéo est requise/);
  assert.equal(validateInspectionStep(0, {
    evidence: [photo('1'), photo('2'), photo('3'), video('4')],
    requirements: { minimum_photos: 3, video_required: true },
  }), '');
});


test('serial number, meter reading and final confirmation are guided explicitly', () => {
  assert.match(validateInspectionStep(2, {
    evidence: [], serialRelevant: true, serialNumber: '', meterType: 'none', meterReading: '',
  }), /numéro de série/);
  assert.match(validateInspectionStep(2, {
    evidence: [], serialRelevant: false, serialNumber: '', meterType: 'hours', meterReading: '',
  }), /relevé de compteur/);
  assert.match(validateInspectionStep(3, { evidence: [], confirmed: false }), /Confirmez/);
});


test('inspection payload sends evidence identifiers and observations, never computed hashes', () => {
  const payload = inspectionPayload({
    bookingId: 'booking-1', type: 'check_out',
    evidence: [photo('evidence-1'), video('evidence-2')], condition: 'good',
    existingDamage: 'Rayure gauche', accessories: 'batterie, chargeur',
    serialNumber: 'SN-123', meterType: 'hours', meterReading: '42.5', notes: 'Testé',
  });
  assert.deepEqual(payload.evidence_ids, ['evidence-1', 'evidence-2']);
  assert.deepEqual(payload.accessories, ['batterie', 'chargeur']);
  assert.equal(payload.meter_reading, 42.5);
  assert.equal(payload.confirmed, true);
  assert.equal('sha256_hash' in payload, false);
});


test('each participant confirmation is read from backend identity associations', () => {
  const inspection = {
    owner_id: 'owner-1', renter_id: 'renter-1',
    confirmed_by_owner: true, confirmed_by_renter: false,
  };
  assert.equal(currentUserHasConfirmed(inspection, 'owner-1'), true);
  assert.equal(currentUserHasConfirmed(inspection, 'renter-1'), false);
});


test('submission retries reuse a session idempotency key', () => {
  const values = new Map();
  const storage = { getItem: (key) => values.get(key), setItem: (key, value) => values.set(key, value) };
  const first = inspectionSubmissionKey('booking-1', 'check_in', storage);
  assert.equal(inspectionSubmissionKey('booking-1', 'check_in', storage), first);
  assert.notEqual(inspectionSubmissionKey('booking-1', 'check_out', storage), first);
});


test('mobile capture, progress, private backend hashing and counterparty confirmation are wired', async () => {
  const modal = await read('./InspectionModal.jsx');
  const api = await read('../services/api.js');
  assert.match(modal, /capture="environment"/);
  assert.match(modal, /max-h-\[100dvh\]/);
  assert.match(modal, /uploadFile/);
  assert.match(modal, /confirmInspection/);
  assert.match(modal, /item\.record\.sha256_hash/);
  assert.match(api, /FormData/);
  assert.match(api, /xhr\.upload\.onprogress/);
  assert.match(api, /'Idempotency-Key': idempotencyKey/);
  assert.doesNotMatch(modal, /REC LIVE|RFC\s*3161|Hachage SHA-256 continu/i);
});
