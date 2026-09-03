import assert from 'node:assert/strict';
import test from 'node:test';

import {
  NOTIFICATION_EVENTS,
  filterNotifications,
  notificationTarget,
  unreadNotificationCount,
} from './notifications/notificationExperience.js';

test('every supported real event has one account destination', () => {
  const expected = [
    'reservation_requested', 'reservation_accepted', 'reservation_rejected',
    'kyc_updated', 'payment_updated', 'deposit_updated', 'inspection_required',
    'message_received', 'dispute_updated', 'payout_updated',
  ];
  assert.deepEqual(Object.keys(NOTIFICATION_EVENTS), expected);
  expected.forEach((eventType) => {
    const target = notificationTarget({ event_type: eventType, destination: { section: NOTIFICATION_EVENTS[eventType].section } });
    assert.match(target.deepLink, /^#account-/);
  });
});

test('a backend destination outside the account allowlist is never followed', () => {
  const target = notificationTarget({
    event_type: 'message_received',
    destination: { section: 'https://attacker.example', resource_id: 'conversation-1' },
  });
  assert.equal(target.section, 'messages');
  assert.equal(target.deepLink, '#account-messages');
});

test('read and unread views use only actual backend records', () => {
  const records = [{ id: '1', est_lu: false }, { id: '2', est_lu: true }];
  assert.deepEqual(filterNotifications(records, 'unread').map((item) => item.id), ['1']);
  assert.equal(unreadNotificationCount(records), 1);
  assert.equal(filterNotifications([], 'all').length, 0);
});
