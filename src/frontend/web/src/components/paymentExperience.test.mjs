import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import {
  canInitiateRentalPayment, getOrCreatePaymentAttempt, paymentAttemptMessage, refundStatus,
  rentalPaymentStatus, securityDepositStatus,
} from './payments/paymentExperience.js';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('only backend-confirmed rental states are presented as confirmed', () => {
  for (const status of ['not_started', 'pending', 'requires_action', 'failed', 'cancelled']) {
    assert.equal(rentalPaymentStatus(status).confirmed, false);
  }
  assert.deepEqual(
    ['succeeded', 'partially_refunded', 'refunded'].map((status) => rentalPaymentStatus(status).confirmed),
    [true, true, true],
  );
  assert.equal(rentalPaymentStatus('succeeded').label, 'Payé');
  assert.equal(rentalPaymentStatus('provider_unknown').confirmed, false);
});

test('deposit and refund states remain separate and accurately labelled', () => {
  assert.equal(securityDepositStatus('authorized').label, 'Autorisé');
  assert.equal(securityDepositStatus('released').label, 'Libéré');
  assert.equal(securityDepositStatus('partially_captured').label, 'Partiellement retenu');
  assert.equal(securityDepositStatus('captured').label, 'Retenu');
  assert.equal(securityDepositStatus('provider_unknown').confirmed, false);
  assert.equal(refundStatus('pending').confirmed, false);
  assert.equal(refundStatus('succeeded').label, 'Remboursé');
});

test('payment can start only for the renter at the backend payment stage', () => {
  const booking = { locataire_id: 'renter-1', statut_reservation: 'paiement_en_attente' };
  assert.equal(canInitiateRentalPayment({
    booking, userId: 'renter-1', financial: { rental_payment: { status: 'failed' } },
  }), true);
  assert.equal(canInitiateRentalPayment({
    booking, userId: 'owner-1', financial: { rental_payment: { status: 'failed' } },
  }), false);
  assert.equal(canInitiateRentalPayment({
    booking, userId: 'renter-1', financial: { rental_payment: { status: 'pending' } },
  }), false);
});

test('uncertain failures tell the user to refresh and remain recoverable', () => {
  assert.match(paymentAttemptMessage({ code: 'REQUEST_TIMEOUT' }), /Actualisez d’abord le statut/);
  assert.match(paymentAttemptMessage({ code: 'PAYMENT_PROVIDER_UNAVAILABLE' }), /réessayer/);
});

test('payment UI prevents duplicate submission and sends an idempotency key', async () => {
  const dashboard = await read('./AccountDashboard.jsx');
  const api = await read('../services/api.js');
  assert.match(dashboard, /paymentInFlightRef\.current\.has\(bookingId\)/);
  assert.match(dashboard, /paymentInFlightRef\.current\.add\(bookingId\)/);
  assert.match(api, /'Idempotency-Key': idempotencyKey/);
});

test('an uncertain retry reuses its idempotency key across a page reload', () => {
  const values = new Map();
  const storage = {
    getItem: (key) => values.get(key) || null,
    setItem: (key, value) => values.set(key, value),
    removeItem: (key) => values.delete(key),
  };
  const first = getOrCreatePaymentAttempt('booking-1', 'not_started', storage);
  const afterReload = getOrCreatePaymentAttempt('booking-1', 'not_started', storage);
  assert.equal(first.key, afterReload.key);
  const retryAfterConfirmedFailure = getOrCreatePaymentAttempt('booking-1', 'failed', storage);
  assert.notEqual(first.key, retryAfterConfirmedFailure.key);
});

test('payment UI explains the two concepts without exposing provider details', async () => {
  const panel = await read('./payments/PaymentStatusPanel.jsx');
  assert.match(panel, /payment\.rental/);
  assert.match(panel, /payment\.deposit/);
  assert.match(panel, /payment\.depositHelp/);
  assert.doesNotMatch(panel, /provider_transaction_id|financial\.[a-z_]+\.provider|numéro de carte/i);
});
