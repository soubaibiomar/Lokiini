import assert from 'node:assert/strict';
import test from 'node:test';

import {
  CONVERSATION_POLL_INTERVAL_MS,
  MESSAGE_POLL_INTERVAL_MS,
  MESSAGE_REFRESH_MODE,
  conversationContext,
  mergeConversationMessages,
  messagingErrorMessage,
  totalUnreadMessages,
} from './messaging/messagingExperience.js';

test('messaging explicitly uses polling intervals instead of pretending to be realtime', () => {
  assert.equal(MESSAGE_REFRESH_MODE, 'polling');
  assert.ok(MESSAGE_POLL_INTERVAL_MS >= 5_000);
  assert.ok(CONVERSATION_POLL_INTERVAL_MS >= MESSAGE_POLL_INTERVAL_MS);
});

test('message polling merges by backend id without duplicate bubbles', () => {
  const merged = mergeConversationMessages(
    [{ id: '2', contenu: 'Second', cree_le: '2026-09-01T10:02:00Z' }],
    [
      { id: '1', contenu: 'First', cree_le: '2026-09-01T10:01:00Z' },
      { id: '2', contenu: 'Second updated', cree_le: '2026-09-01T10:02:00Z' },
    ],
  );
  assert.deepEqual(merged.map((message) => message.id), ['1', '2']);
  assert.equal(merged[1].contenu, 'Second updated');
});

test('conversation context distinguishes reservation and equipment', () => {
  assert.deepEqual(
    conversationContext({ reservation_id: '12345678-aaaa', article_titre: 'Mini-pelle' }),
    { kind: 'reservation', eyebrow: 'Réservation', reference: 'LK-12345678', title: 'Mini-pelle' },
  );
  assert.equal(conversationContext({ article_id: 'equipment-1', article_titre: 'Perceuse' }).kind, 'equipment');
});

test('unread totals and message errors remain backend-driven', () => {
  assert.equal(totalUnreadMessages([{ messages_non_lus: 2 }, { messages_non_lus: 3 }]), 5);
  assert.match(messagingErrorMessage({ code: 'CONVERSATION_FORBIDDEN' }), /participez pas/);
  assert.match(messagingErrorMessage({ code: 'NETWORK_ERROR' }), /connexion/);
});
