import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import {
  accountSectionFromHash, accountSectionHash, buildOverviewActions, roleForBooking,
} from './account/dashboardModel.js';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('one identity can be renter and owner across different reservations', () => {
  const userId = 'user-1';
  assert.equal(roleForBooking({ locataire_id: userId, loueur_id: 'user-2' }, userId), 'renter');
  assert.equal(roleForBooking({ locataire_id: 'user-3', loueur_id: userId }, userId), 'owner');
});

test('account notification destinations survive a page reload through safe hashes', () => {
  assert.equal(accountSectionFromHash('#account-notifications'), 'notifications');
  assert.equal(accountSectionFromHash('#account-payments'), 'payments');
  assert.equal(accountSectionFromHash('#account-https://attacker.example'), 'overview');
  assert.equal(accountSectionHash('messages'), '#account-messages');
  assert.equal(accountSectionHash('unknown'), '#account-overview');
});

test('overview actions are derived from real account records', () => {
  const actions = buildOverviewActions({
    user: { id: 'user-1', statut_verification: 'requires_action' },
    bookings: [{
      id: 'booking-1', loueur_id: 'user-1', locataire_id: 'user-2',
      statut_reservation: 'en_attente_approbation', article_titre: 'Perceuse',
      date_debut: '2026-09-10', date_fin: '2026-09-12',
    }],
    conversations: [{ messages_non_lus: 2 }],
    notifications: [{ est_lu: false }],
    equipment: [{ statut: 'en_pause', is_available: false }],
    earnings: {},
  }, new Date('2026-08-31T12:00:00'));

  assert.deepEqual(actions.map((action) => action.id), [
    'owner-requests', 'kyc', 'unread-messages', 'equipment-attention', 'unread-notifications',
  ]);
  assert.equal(actions.some((action) => action.id === 'payout'), false);
});

test('account dashboard loads the shared account domains from FastAPI', async () => {
  const source = await read('./AccountDashboard.jsx');
  for (const call of [
    "getBookings('all')", 'getMyEquipment()', 'getUserConversations()',
    'getDisputes()', 'getFinancialSummaries()', 'getNotifications()', 'getUserReviews(currentUser.id)', "getOwnerEarningsDashboard('mois')",
  ]) assert.match(source, new RegExp(call.replace(/[()'.]/g, '\\$&')));

  for (const section of [
    'Vue d’ensemble', 'Réservations', 'Mon matériel', 'Messages', 'Dossiers', 'Paiements',
    'Revenus', 'Documents', 'Vérification', 'Avis', 'Notifications', 'Paramètres',
  ]) assert.match(await read('./account/dashboardModel.js'), new RegExp(section));
});

test('dashboard does not claim payment, payout, contract or CMI success without evidence', async () => {
  const source = await read('./AccountDashboard.jsx');
  const paymentPanel = await read('./payments/PaymentStatusPanel.jsx');
  const model = await read('./account/dashboardModel.js');
  assert.doesNotMatch(source, /Règlement CMI garanti|100% avec baux|Cautions CMI sous Séquestre/);
  assert.match(source, /getFinancialSummaries/);
  assert.doesNotMatch(model, /cmi_status/);
  for (const concept of ['payment.rental', 'payment.platformFee', 'payment.deposit', 'payment.capturedAmount', 'payment.releasedAmount', 'payment.refund', 'payment.ownerPayout']) {
    assert.match(`${source}\n${paymentPanel}`, new RegExp(concept));
  }
  assert.doesNotMatch(source, /taux_occupation_pct/);
});

test('dashboard filters expose complete keyboard tab semantics', async () => {
  const source = await read('./AccountDashboard.jsx');
  assert.match(source, /function handleRovingTabKey/);
  assert.match(source, /aria-orientation="horizontal"/);
  assert.match(source, /tabIndex=\{bookingFilter === value \? 0 : -1\}/);
  assert.match(source, /tabIndex=\{notificationFilter === value \? 0 : -1\}/);
  assert.match(source, /role="tabpanel"/);
  assert.match(source, /ArrowRight/);
});
