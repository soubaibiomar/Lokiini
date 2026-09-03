import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  KYC_REASONS, KYC_STATUS, canInitiateKyc, getKycStatus, normalizeKycStatus,
} from './kyc/kycExperience.js';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('all backend KYC states have explicit friendly user-facing content', () => {
  assert.deepEqual(Object.keys(KYC_STATUS), [
    'not_started', 'pending', 'in_review', 'verified', 'rejected', 'requires_action',
  ]);
  for (const state of Object.values(KYC_STATUS)) {
    assert.ok(state.label);
    assert.ok(state.description);
    assert.ok(state.guidance);
    assert.doesNotMatch(state.label, /^[A-Z_]+$/);
  }
});

test('unknown provider values are never presented as success or not started', () => {
  assert.equal(normalizeKycStatus('provider_new_state'), 'unknown');
  assert.equal(getKycStatus('provider_new_state').label, 'Statut indisponible');
  assert.equal(canInitiateKyc('provider_new_state'), false);
  assert.equal(canInitiateKyc('verified'), false);
  assert.equal(canInitiateKyc('requires_action'), true);
});

test('the experience explains the five legitimate reasons for verification', () => {
  assert.deepEqual(KYC_REASONS, [
    'Réduire les tentatives de fraude',
    'Protéger les locataires',
    'Protéger les propriétaires',
    'Associer l’identité aux contrats',
    'Fournir un repère lors du traitement des litiges',
  ]);
});

test('web KYC reads backend status, never exposes scores, and makes no unsupported claims', async () => {
  const source = `${await read('./KYCVerificationModal.jsx')}\n${await read('./kyc/kycExperience.js')}`;
  assert.match(source, /getDiditKYCStatus/);
  assert.match(source, /initiateDiditKYC/);
  assert.doesNotMatch(source, /liveness|vivacité|CNDP|gouvernement|government approved|légalement garanti|score/i);
});

test('all visible KYC entry points avoid unsupported compliance and paid-priority claims', async () => {
  const sources = await Promise.all([
    read('./AuthModal.jsx'),
    read('./HowItWorksModal.jsx'),
    read('./PricingModal.jsx'),
    read('./PricingSection.jsx'),
    read('../../../mobile/src/screens/HomeScreen.js'),
    read('../../../mobile/src/screens/KYCCameraScreen.js'),
  ]);
  const source = sources.join('\n');
  assert.match(source, /getKYCStatus/);
  assert.doesNotMatch(source, /CNDP|liveness|vivacité|KYC Didit prioritaire|identité certifiée|score/i);
});
