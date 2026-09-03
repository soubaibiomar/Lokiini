import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import {
  DISPUTE_STEPS, canOpenDispute, disputeDecision, disputeStatus, disputeSubmissionKey,
} from './disputes/disputeExperience.js';


const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');


test('the user-facing lifecycle exposes every backend dispute stage', () => {
  assert.deepEqual(DISPUTE_STEPS.map((item) => item.key), [
    'open', 'evidence_collection', 'under_review', 'decision', 'resolved',
  ]);
  assert.equal(disputeStatus('under_review').label, 'En cours d’examen');
  assert.equal(disputeStatus('resolved').step, 4);
});


test('a booking cannot open a duplicate active dispute', () => {
  const booking = { id: 'booking-1', statut_reservation: 'en_cours' };
  assert.equal(canOpenDispute(booking, []), true);
  assert.equal(canOpenDispute(booking, [{ booking_id: 'booking-1', status: 'under_review' }]), false);
  assert.equal(canOpenDispute(booking, [{ booking_id: 'booking-1', status: 'resolved' }]), true);
  assert.equal(canOpenDispute({ ...booking, statut_reservation: 'brouillon' }, []), false);
});


test('financial decisions are displayed from backend state only', () => {
  assert.equal(disputeDecision({ decision_code: 'release_deposit' }), 'Libération du dépôt');
  assert.equal(disputeDecision({ decision_code: null }), null);
});


test('opening retries reuse an idempotency key', () => {
  const values = new Map();
  const storage = { getItem: (key) => values.get(key), setItem: (key, value) => values.set(key, value) };
  const first = disputeSubmissionKey('booking-1', storage);
  assert.equal(disputeSubmissionKey('booking-1', storage), first);
  assert.notEqual(disputeSubmissionKey('booking-2', storage), first);
});


test('dispute center supports evidence, inspections, messages and neutral tracking', async () => {
  const center = await read('./disputes/DisputeCenter.jsx');
  const api = await read('../services/api.js');
  for (const phrase of [
    'Pièces ajoutées par les participants', 'États des lieux associés',
    'Messages liés à la réservation', 'sans présumer de la responsabilité',
  ]) assert.match(center, new RegExp(phrase));
  assert.match(center, /item\.sha256_hash/);
  assert.match(api, /xhr\.upload\.onprogress/);
  assert.match(api, /getDisputeContext/);
  assert.doesNotMatch(center, /coupable|faute commise|responsable des dégâts/i);
});


test('the web client cannot submit a decision or compensation amount', async () => {
  const center = await read('./disputes/DisputeCenter.jsx');
  const api = await read('../services/api.js');
  assert.doesNotMatch(api, /recordDisputeDecision|submitDisputeDecision/);
  assert.doesNotMatch(center, /decision_code\s*:|deposit_capture_amount_mad\s*:/);
  assert.doesNotMatch(center, /label="Montant.*(?:retenue|compensation)/i);
});


test('the account dashboard treats disputes as a first-class section', async () => {
  const dashboard = await read('./AccountDashboard.jsx');
  const model = await read('./account/dashboardModel.js');
  assert.match(dashboard, /getDisputes\(\)/);
  assert.match(dashboard, /DisputeCenter/);
  assert.match(model, /id: 'disputes', label: 'Dossiers'/);
});
