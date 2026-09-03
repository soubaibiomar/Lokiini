export const MESSAGE_REFRESH_MODE = 'polling';
export const MESSAGE_POLL_INTERVAL_MS = 8_000;
export const CONVERSATION_POLL_INTERVAL_MS = 15_000;

export function normalizeMessageId(value) {
  return value == null ? '' : String(value);
}

export function mergeConversationMessages(current = [], incoming = []) {
  const byId = new Map();
  [...current, ...incoming].forEach((message) => {
    const key = normalizeMessageId(message?.id);
    if (key) byId.set(key, message);
  });
  return [...byId.values()].sort((left, right) => {
    const leftTime = new Date(left.cree_le || 0).getTime();
    const rightTime = new Date(right.cree_le || 0).getTime();
    return leftTime - rightTime;
  });
}

export function totalUnreadMessages(conversations = []) {
  return conversations.reduce(
    (total, conversation) => total + Math.max(0, Number(conversation?.messages_non_lus) || 0),
    0,
  );
}

export function conversationContext(conversation) {
  if (!conversation) return null;
  if (conversation.reservation_id) {
    return {
      kind: 'reservation',
      eyebrow: 'Réservation',
      reference: `LK-${String(conversation.reservation_id).slice(0, 8).toUpperCase()}`,
      title: conversation.article_titre || 'Matériel réservé',
    };
  }
  if (conversation.article_id) {
    return {
      kind: 'equipment',
      eyebrow: 'Équipement',
      reference: null,
      title: conversation.article_titre || 'Annonce Lokiini',
    };
  }
  return {
    kind: 'legacy',
    eyebrow: 'Conversation',
    reference: null,
    title: conversation.article_titre || null,
  };
}

export function messagingErrorMessage(error, fallback = 'La messagerie est temporairement indisponible.') {
  if (error?.code === 'CONVERSATION_FORBIDDEN') {
    return 'Vous ne participez pas à cette conversation.';
  }
  if (error?.code === 'CONVERSATION_NOT_FOUND') {
    return 'Cette conversation n’est plus disponible.';
  }
  if (error?.code === 'REQUEST_TIMEOUT' || error?.code === 'NETWORK_ERROR') {
    return 'La connexion a été interrompue. Réessayez sans renvoyer votre message automatiquement.';
  }
  return error?.message || fallback;
}
