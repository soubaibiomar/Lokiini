const ALLOWED_SECTIONS = new Set([
  'bookings', 'verification', 'payments', 'messages', 'disputes', 'earnings',
]);

export const NOTIFICATION_EVENTS = {
  reservation_requested: { label: 'Demande de réservation', tone: 'warning', section: 'bookings' },
  reservation_accepted: { label: 'Réservation acceptée', tone: 'success', section: 'bookings' },
  reservation_rejected: { label: 'Réservation refusée', tone: 'error', section: 'bookings' },
  kyc_updated: { label: 'Vérification', tone: 'info', section: 'verification' },
  payment_updated: { label: 'Paiement', tone: 'info', section: 'payments' },
  deposit_updated: { label: 'Dépôt', tone: 'info', section: 'payments' },
  inspection_required: { label: 'Inspection requise', tone: 'warning', section: 'bookings' },
  message_received: { label: 'Message', tone: 'info', section: 'messages' },
  dispute_updated: { label: 'Dossier', tone: 'warning', section: 'disputes' },
  payout_updated: { label: 'Versement', tone: 'info', section: 'earnings' },
};

export function notificationEvent(value) {
  return NOTIFICATION_EVENTS[value] || { label: 'Mise à jour Lokiini', tone: 'neutral', section: 'bookings' };
}

export function notificationTarget(notification) {
  const event = notificationEvent(notification?.event_type);
  const section = notification?.destination?.section;
  const safeSection = ALLOWED_SECTIONS.has(section) ? section : event.section;
  return {
    view: 'dashboard',
    section: safeSection,
    resourceId: notification?.destination?.resource_id || null,
    deepLink: `#account-${safeSection}`,
  };
}

export function filterNotifications(notifications = [], filter = 'all') {
  if (filter === 'unread') return notifications.filter((notification) => !notification.est_lu);
  return notifications;
}

export function unreadNotificationCount(notifications = []) {
  return notifications.filter((notification) => !notification.est_lu).length;
}

export function notificationErrorMessage(error) {
  if (['NETWORK_ERROR', 'REQUEST_TIMEOUT'].includes(error?.code)) {
    return 'Les notifications ne peuvent pas être actualisées pour le moment. Réessayez.';
  }
  return error?.message || 'Le centre de notifications est temporairement indisponible.';
}
