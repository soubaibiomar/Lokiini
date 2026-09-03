import { apiClient } from './apiClient';

export async function getConversations() {
  return apiClient.get('/messages/conversations');
}

export async function getConversationMessages(conversationId) {
  return apiClient.get(`/messages/conversations/${encodeURIComponent(String(conversationId))}`);
}

export async function sendMessage({ conversationId, recipientId, bookingId, equipmentId, content }) {
  const payload = {
    contenu: content,
  };
  if (conversationId) {
    payload.conversation_id = conversationId;
  }
  if (recipientId) {
    payload.destinataire_id = recipientId;
  }
  if (bookingId) {
    payload.reservation_id = bookingId;
  }
  if (equipmentId) {
    payload.article_id = equipmentId;
  }
  return apiClient.post('/messages', payload);
}

export async function markConversationAsRead(conversationId) {
  return apiClient.put(`/messages/conversations/${encodeURIComponent(String(conversationId))}/lus`);
}
