import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('equipment detail loads authoritative detail, pricing, reviews, and similar listings', async () => {
  const source = `${await read('./EquipmentModal.jsx')}\n${await read('./ReservationJourney.jsx')}`;
  for (const api of ['getEquipment', 'calculatePricing', 'getUserReviews', 'getEquipmentPage']) {
    assert.match(source, new RegExp(api));
  }
});

test('rental total and deposit are visually and semantically separate', async () => {
  const source = await read('./ReservationJourney.jsx');
  assert.match(source, /booking\.rental/);
  assert.match(source, /booking\.deposit/);
  assert.match(source, /booking\.depositDistinct/);
  assert.match(source, /booking\.totalNote/);
});

test('detail page contains no invented delivery, guarantee, insurance, or default review claims', async () => {
  const source = await read('./EquipmentModal.jsx');
  for (const forbidden of ['Livraison Partenaire', '49 MAD', 'restituée intégralement', 'Coursier express', 'assurance incluse', 'garantie Lokiini']) {
    assert.doesNotMatch(source, new RegExp(forbidden, 'i'));
  }
  assert.match(source, /equipment\.deliveryMissing/);
  assert.match(source, /equipment\.cancellationMissing/);
  assert.match(source, /equipment\.noReviews/);
});

test('booking acknowledgement is explicit and not preselected', async () => {
  const source = `${await read('./EquipmentModal.jsx')}\n${await read('./ReservationJourney.jsx')}`;
  assert.match(source, /useState\(false\)/);
  assert.match(source, /booking\.pendingWarning/);
  assert.match(source, /disabled={!acknowledged \|\| !pricing \|\| isSubmitting}/);
  assert.match(source, /equipment\.viewDates/);
  assert.match(source, /id="booking-panel"/);
});
