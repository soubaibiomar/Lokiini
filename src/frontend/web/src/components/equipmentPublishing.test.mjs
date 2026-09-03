import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import {
  PUBLISHING_STEPS, buildEquipmentPayload, createEmptyListing,
  validateCompleteListing, validatePublishingStep,
} from './equipmentPublishing.js';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('publishing uses the complete guided sequence', () => {
  assert.deepEqual(PUBLISHING_STEPS, [
    'Catégorie', 'Informations', 'Photos', 'Description', 'Spécifications',
    'Localisation', 'Prix', 'Dépôt', 'Disponibilité', 'Remise', 'Règles',
    'Aperçu', 'Publication',
  ]);
});

test('every required publishing field fails clearly before submission', () => {
  const listing = createEmptyListing();
  const errors = validateCompleteListing(listing, []);
  for (const field of [
    'category', 'title', 'condition', 'photos', 'description', 'address',
    'dailyPrice', 'depositAmount', 'pickupInstructions', 'rules', 'confirmed',
  ]) assert.ok(errors[field], `${field} must be validated`);
});

test('photo step blocks pending and failed uploads', () => {
  const listing = createEmptyListing();
  assert.match(validatePublishingStep(2, listing, [{ status: 'uploading' }]).photos, /fin/);
  assert.match(validatePublishingStep(2, listing, [{ status: 'failed' }]).photos, /Réessayez/);
  assert.deepEqual(validatePublishingStep(2, listing, [{ status: 'uploaded' }]), {});
});

test('payload preserves entered values and delegates commercial calculations to FastAPI', () => {
  const listing = {
    ...createEmptyListing(), category: 'tools', title: 'Perforateur Bosch', condition: 'bon',
    description: 'Perforateur entretenu avec poignée, coffret et deux forets inclus.',
    city: 'Rabat', address: 'Agdal', dailyPrice: '120', depositAmount: '900',
    pickupInstructions: 'Retrait sur rendez-vous', noAdditionalRules: true,
    specifications: [{ id: '1', key: 'Puissance', value: '1500 W' }],
  };
  const payload = buildEquipmentPayload(listing, [
    { url: '/api/v1/media/equipment/photo-1.webp' },
    { url: '/api/v1/media/equipment/photo-2.webp' },
  ]);
  assert.equal(payload.daily_price_mad, 120);
  assert.equal(payload.deposit_amount_mad, 900);
  assert.deepEqual(payload.images_urls, [
    '/api/v1/media/equipment/photo-1.webp', '/api/v1/media/equipment/photo-2.webp',
  ]);
  assert.equal(payload.specs_json.Puissance, '1500 W');
  assert.equal(payload.specs_json.option_livraison, 'Retrait sur place');
  assert.equal('commission' in payload, false);
  assert.equal('total' in payload, false);
});

test('image UX has compression, progress, ordering, deletion and retry without fake draft success', async () => {
  const [modal, helper, api] = await Promise.all([
    read('./AddEquipmentModal.jsx'), read('./equipmentPublishing.js'), read('../services/api.js'),
  ]);
  assert.match(helper, /compressEquipmentPhoto/);
  assert.match(api, /xhr\.upload\.onprogress/);
  assert.match(modal, /movePhoto/);
  assert.match(modal, /removePhoto/);
  assert.match(modal, /retryPhoto/);
  assert.match(modal, /backend ne prend pas encore en charge l’enregistrement de brouillons partiels/);
  assert.doesNotMatch(modal, /Brouillon enregistré|weeklyRate|commission\s*\*|Math\.ceil/);
});
