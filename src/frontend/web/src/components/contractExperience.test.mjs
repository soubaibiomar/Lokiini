import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('contract UX follows the real confirmed-to-document journey', async () => {
  const source = await read('./ContractViewerModal.jsx');
  for (const step of [
    'Réservation confirmée', 'Contrat généré', 'Revue des parties', 'Acceptation', 'Document final',
  ]) assert.match(source, new RegExp(step));
  for (const field of [
    'contract.owner', 'contract.renter', 'contract.equipment', 'contract.start_date',
    'contract.rental_price_mad', 'contract.deposit_amount_mad', 'contract.responsibilities',
    'contract.important_conditions', 'owner_signature_status', 'renter_signature_status',
  ]) assert.match(source, new RegExp(field.replace('.', '\\.')));
});

test('signing is visible only when the backend enables it', async () => {
  const [component, api] = await Promise.all([
    read('./ContractViewerModal.jsx'), read('../services/api.js'),
  ]);
  assert.match(component, /contract\.signature_available/);
  assert.match(component, /Aucun prestataire de signature professionnellement validé/);
  assert.match(api, /signContract = \(bookingId, payload, options\)/);
  assert.doesNotMatch(component, /signature qualifiée conforme|certificat d'authenticité|Lokiini Trust Authority/i);
});

test('French is shown and Arabic is offered only when backend content exists', async () => {
  const source = await read('./ContractViewerModal.jsx');
  assert.match(source, /available_languages/);
  assert.match(source, /contract_text_ar/);
  assert.match(source, /availableLanguages\.map/);
  assert.doesNotMatch(source, /translate|traduction automatique|Google Translate/i);
});

test('backend contract generation is gated by confirmed lifecycle states', async () => {
  const router = await read('../../../../backend/app/routers/contracts.py');
  assert.match(router, /CONTRACT_READY_STATUSES/);
  assert.match(router, /CONTRACT_NOT_READY/);
  assert.match(router, /signature_available=False/);
  assert.match(router, /owner_signature_status="unavailable"/);
  assert.match(router, /renter_signature_status="unavailable"/);
  assert.doesNotMatch(router, /Lokiini Trust Authority|conforme_loi_53_05=True|CERT-/);
});

test('generated contract copy avoids unsupported proof and identity claims', async () => {
  const generator = await read('../../../../backend/app/services/contract_generator_service.py');
  assert.match(generator, /ne valent pas, à elles seules, signature électronique qualifiée/);
  assert.doesNotMatch(generator, /CIN Certifiée Didit|RFC 3161|certifiée conforme à la Loi/i);
});
