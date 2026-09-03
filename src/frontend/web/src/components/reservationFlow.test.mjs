import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('reservation journey follows the supported request stages', async () => {
  const source = await read('./ReservationJourney.jsx');
  for (const stage of ["'dates'", "'fulfilment'", "'verification'", "'review'", 'booking.future.owner', 'booking.future.contract', 'booking.future.payment', 'booking.future.confirmation']) {
    assert.match(source, new RegExp(stage));
  }
  assert.match(source, /booking\.pendingWarning/);
});

test('reservation summary always includes authoritative commercial fields', async () => {
  const source = await read('./ReservationJourney.jsx');
  for (const field of ['booking.owner', 'booking.dates', 'booking.duration', 'booking.handover', 'booking.rental', 'booking.platformFee', 'booking.deposit', 'booking.handoverTotal']) {
    assert.match(source, new RegExp(field));
  }
  assert.match(source, /total_location_mad/);
  assert.match(source, /frais_service_plateforme_mad/);
  assert.match(source, /montant_caution_mad/);
  assert.match(source, /total_a_payer_a_la_remise_mad/);
});

test('pricing is requested from FastAPI and never recomputed in the browser', async () => {
  const source = await read('./ReservationJourney.jsx');
  assert.match(source, /calculatePricing\(equipment\.id, startDate, endDate/);
  assert.match(source, /booking\.pricingUnavailable/);
  assert.doesNotMatch(source, /daily.*\*.*days|subtotal|discountedRate|Math\.ceil/);
});

test('date conflicts return the renter to editable dates with a useful message', async () => {
  const source = await read('./ReservationJourney.jsx');
  assert.match(source, /BOOKING_DATE_UNAVAILABLE/);
  assert.match(source, /booking\.unavailable/);
  assert.match(source, /setStep\(0\)/);
  assert.match(source, /error={conflictError/);
});

test('duplicate submissions are blocked synchronously', async () => {
  const source = await read('./ReservationJourney.jsx');
  assert.match(source, /submittingRef\.current \|\| !pricing \|\| !acknowledged/);
  assert.match(source, /submittingRef\.current = true/);
  assert.match(source, /disabled={!acknowledged \|\| !pricing \|\| isSubmitting}/);
});

test('unsupported delivery and future lifecycle actions remain unavailable', async () => {
  const source = await read('./ReservationJourney.jsx');
  assert.match(source, /booking\.deliveryUnavailable/);
  assert.match(source, /booking\.deliveryUnavailableHelp/);
  assert.match(source, /booking\.reference/);
  assert.doesNotMatch(source, /Livraison Partenaire|49 MAD|Préparer la remise/);
});
