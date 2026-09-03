import { KYC_STATUS, getKycStatus } from '../kyc/kycExperience.js';

export { KYC_STATUS };

export const ACCOUNT_SECTIONS = [
  { id: 'overview', label: 'Vue d’ensemble' },
  { id: 'bookings', label: 'Réservations' },
  { id: 'equipment', label: 'Mon matériel' },
  { id: 'messages', label: 'Messages' },
  { id: 'disputes', label: 'Dossiers' },
  { id: 'payments', label: 'Paiements' },
  { id: 'earnings', label: 'Revenus' },
  { id: 'documents', label: 'Documents' },
  { id: 'verification', label: 'Vérification' },
  { id: 'reviews', label: 'Avis' },
  { id: 'notifications', label: 'Notifications' },
  { id: 'settings', label: 'Paramètres' },
];

const ACCOUNT_SECTION_IDS = new Set(ACCOUNT_SECTIONS.map((section) => section.id));

export function accountSectionFromHash(hash = '') {
  const value = String(hash).replace(/^#account-/, '').split(/[?&]/, 1)[0];
  return ACCOUNT_SECTION_IDS.has(value) ? value : 'overview';
}

export function accountSectionHash(section) {
  return `#account-${ACCOUNT_SECTION_IDS.has(section) ? section : 'overview'}`;
}

export const BOOKING_STATUS = {
  brouillon: { label: 'Brouillon', tone: 'neutral' },
  en_attente_approbation: { label: 'Réponse du propriétaire attendue', tone: 'warning' },
  acceptee: { label: 'Acceptée', tone: 'info' },
  paiement_en_attente: { label: 'Paiement en attente', tone: 'warning' },
  confirmee: { label: 'Confirmée', tone: 'success' },
  prete_remise: { label: 'Prête pour la remise', tone: 'success' },
  en_cours: { label: 'Location en cours', tone: 'success' },
  en_attente_validation: { label: 'Retour à valider', tone: 'warning' },
  termine: { label: 'Terminée', tone: 'neutral' },
  rejete: { label: 'Refusée', tone: 'error' },
  annule: { label: 'Annulée', tone: 'error' },
  en_litige: { label: 'Litige en cours', tone: 'error' },
  resolu: { label: 'Litige résolu', tone: 'neutral' },
};

const TERMINAL_BOOKING_STATUSES = new Set(['termine', 'rejete', 'annule', 'resolu']);

export function normalizeId(value) {
  return value == null ? '' : String(value);
}

export function roleForBooking(booking, userId) {
  const id = normalizeId(userId);
  if (normalizeId(booking?.loueur_id) === id) return 'owner';
  if (normalizeId(booking?.locataire_id) === id) return 'renter';
  return 'unknown';
}

export function bookingStatus(status) {
  return BOOKING_STATUS[status] || {
    label: status ? String(status).replaceAll('_', ' ') : 'Statut indisponible',
    tone: 'neutral',
  };
}

const FINANCIAL_STATUS = {
  not_started: { label: 'Non démarré', tone: 'neutral' },
  not_ready: { label: 'Pas encore disponible', tone: 'neutral' },
  pending: { label: 'En attente', tone: 'warning' },
  authorization_pending: { label: 'Autorisation en attente', tone: 'warning' },
  requires_action: { label: 'Action requise', tone: 'warning' },
  authorized: { label: 'Autorisé', tone: 'info' },
  succeeded: { label: 'Confirmé', tone: 'success' },
  earned: { label: 'Acquis', tone: 'success' },
  paid: { label: 'Versé', tone: 'success' },
  released: { label: 'Libéré', tone: 'success' },
  partially_captured: { label: 'Partiellement retenu', tone: 'warning' },
  captured: { label: 'Retenu', tone: 'error' },
  partially_refunded: { label: 'Partiellement remboursé', tone: 'warning' },
  refunded: { label: 'Remboursé', tone: 'neutral' },
  failed: { label: 'Échec', tone: 'error' },
  authorization_failed: { label: 'Autorisation échouée', tone: 'error' },
  cancelled: { label: 'Annulé', tone: 'neutral' },
  reversed: { label: 'Annulé après traitement', tone: 'error' },
  mixed: { label: 'Plusieurs statuts', tone: 'info' },
};

export function financialStatus(value) {
  return FINANCIAL_STATUS[value] || {
    label: value ? String(value).replaceAll('_', ' ') : 'Statut indisponible',
    tone: 'neutral',
  };
}

export function formatMoney(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return 'Montant indisponible';
  return `${new Intl.NumberFormat('fr-MA', { maximumFractionDigits: 2 }).format(amount)} MAD`;
}

export function formatDate(value, options = {}) {
  if (!value) return 'Date indisponible';
  const date = new Date(`${String(value).slice(0, 10)}T12:00:00`);
  if (Number.isNaN(date.getTime())) return 'Date indisponible';
  return new Intl.DateTimeFormat('fr-MA', {
    day: 'numeric', month: 'short', year: options.year === false ? undefined : 'numeric',
  }).format(date);
}

function dateValue(value) {
  if (!value) return Number.POSITIVE_INFINITY;
  const parsed = new Date(`${String(value).slice(0, 10)}T12:00:00`).getTime();
  return Number.isNaN(parsed) ? Number.POSITIVE_INFINITY : parsed;
}

export function filterBookings(bookings, filter, userId) {
  if (filter === 'renter') return bookings.filter((booking) => roleForBooking(booking, userId) === 'renter');
  if (filter === 'owner') return bookings.filter((booking) => roleForBooking(booking, userId) === 'owner');
  return bookings;
}

export function nextRenterBooking(bookings, userId, now = new Date()) {
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  return bookings
    .filter((booking) => (
      roleForBooking(booking, userId) === 'renter'
      && !TERMINAL_BOOKING_STATUSES.has(booking.statut_reservation)
      && dateValue(booking.date_fin) >= today
    ))
    .sort((a, b) => dateValue(a.date_debut) - dateValue(b.date_debut))[0] || null;
}

export function buildOverviewActions({
  bookings = [], disputes = [], equipment = [], conversations = [], notifications = [], user, earnings,
}, now = new Date()) {
  const userId = user?.id;
  const actions = [];
  const activeDisputes = disputes.filter((item) => item.status !== 'resolved');
  if (activeDisputes.length) {
    actions.push({
      id: 'active-disputes', section: 'disputes', priority: 0,
      title: activeDisputes.length === 1 ? '1 dossier en cours' : `${activeDisputes.length} dossiers en cours`,
      description: 'Consultez les éléments disponibles et le dernier statut enregistré.',
      tone: 'info', icon: 'dispute',
    });
  }
  const ownerRequests = bookings.filter((booking) => (
    roleForBooking(booking, userId) === 'owner'
    && booking.statut_reservation === 'en_attente_approbation'
  ));
  if (ownerRequests.length) {
    actions.push({
      id: 'owner-requests', section: 'bookings', bookingFilter: 'owner', priority: 1,
      title: ownerRequests.length === 1 ? 'Répondre à une demande' : `Répondre à ${ownerRequests.length} demandes`,
      description: 'Des locataires attendent votre décision.',
      tone: 'warning', icon: 'calendar',
    });
  }

  const activeReturns = bookings.filter((booking) => (
    roleForBooking(booking, userId) === 'renter'
    && ['en_cours', 'en_attente_validation'].includes(booking.statut_reservation)
  )).sort((a, b) => dateValue(a.date_fin) - dateValue(b.date_fin));
  if (activeReturns.length) {
    const due = activeReturns[0];
    actions.push({
      id: 'return-due', section: 'bookings', bookingFilter: 'renter', priority: 0,
      title: due.statut_reservation === 'en_attente_validation' ? 'Retour en attente de validation' : `Retour prévu le ${formatDate(due.date_fin, { year: false })}`,
      description: due.article_titre || 'Location en cours',
      tone: 'warning', icon: 'return',
    });
  }

  const kyc = getKycStatus(user?.statut_verification);
  if (user?.statut_verification !== 'verified') {
    actions.push({
      id: 'kyc', section: 'verification', priority: 2,
      title: kyc.label,
      description: kyc.description,
      tone: kyc.tone, icon: 'shield',
    });
  }

  const unreadMessages = conversations.reduce((total, conversation) => (
    total + Math.max(0, Number(conversation.messages_non_lus) || 0)
  ), 0);
  if (unreadMessages) {
    actions.push({
      id: 'unread-messages', section: 'messages', priority: 3,
      title: unreadMessages === 1 ? '1 message non lu' : `${unreadMessages} messages non lus`,
      description: 'Une réponse peut être nécessaire pour votre location.',
      tone: 'info', icon: 'message',
    });
  }

  const unreadNotifications = notifications.filter((notification) => !notification.est_lu).length;
  if (unreadNotifications) {
    actions.push({
      id: 'unread-notifications', section: 'notifications', priority: 5,
      title: unreadNotifications === 1 ? '1 notification à consulter' : `${unreadNotifications} notifications à consulter`,
      description: 'Consultez les dernières mises à jour de votre compte.',
      tone: 'neutral', icon: 'bell',
    });
  }

  const equipmentAttention = equipment.filter((item) => item.statut !== 'actif' || item.is_available === false);
  if (equipmentAttention.length) {
    actions.push({
      id: 'equipment-attention', section: 'equipment', priority: 4,
      title: equipmentAttention.length === 1 ? '1 annonce demande votre attention' : `${equipmentAttention.length} annonces demandent votre attention`,
      description: 'Vérifiez la publication ou la disponibilité de votre matériel.',
      tone: 'warning', icon: 'equipment',
    });
  }

  if (earnings?.payout_status && !['paid', 'settled'].includes(earnings.payout_status)) {
    actions.push({
      id: 'payout', section: 'earnings', priority: 4,
      title: 'Versement à suivre',
      description: `Statut transmis par le service de paiement : ${earnings.payout_status}.`,
      tone: 'info', icon: 'wallet',
    });
  }

  return actions.sort((a, b) => a.priority - b.priority);
}
