import { apiClient } from './apiClient';

export async function getUserBookings(role = 'locataire', status = null) {
  const query = {
    role,
    statut: status || undefined,
  };
  return apiClient.get('/reservations', query);
}

export async function calculateBookingQuote({ articleId, startDate, endDate }) {
  return apiClient.post('/reservations/calculer-prix', {
    article_id: articleId,
    date_debut: startDate,
    date_fin: endDate,
  });
}

export async function createBooking({ articleId, startDate, endDate, paymentMethod = 'cash_on_delivery' }) {
  return apiClient.post('/reservations/creer', {
    article_id: articleId,
    date_debut: startDate,
    date_fin: endDate,
    mode_paiement: paymentMethod,
  });
}

export async function updateBookingStatus(bookingId, newStatus, reason = null) {
  return apiClient.patch(`/reservations/${encodeURIComponent(String(bookingId))}/statut`, {
    statut: newStatus,
    raison: reason || undefined,
  });
}
