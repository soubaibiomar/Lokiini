import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowLeft, ArrowRight, Bell, Building2, CalendarDays, Check, ChevronRight, CircleDollarSign,
  FileText, MapPin, MessageSquare, Package, RotateCcw, Send,
  Scale, ShieldCheck, Star, UserRound, WalletCards, X,
} from 'lucide-react';
import {
  getBookings, getConversationMessages, getDisputes, getFinancialSummaries, getMyEquipment, getNotifications,
  getOwnerEarningsDashboard, getUserConversations, getUserReviews,
  initiateBookingPayment, markAllNotificationsRead, performBookingAction, sendConversationMessage,
  updateCurrentUser, updateNotificationRead,
} from '../services/api';
import DashboardShell from './layout/DashboardShell';
import {
  Avatar, Badge, Button, Card, EmptyState, ErrorState, Input, Skeleton, useToast,
} from './ui';
import {
  ACCOUNT_SECTIONS, accountSectionFromHash, accountSectionHash, bookingStatus, buildOverviewActions, filterBookings,
  financialStatus, nextRenterBooking, normalizeId, roleForBooking,
} from './account/dashboardModel';
import { getKycStatus } from './kyc/kycExperience';
import PaymentStatusPanel from './payments/PaymentStatusPanel';
import {
  clearPaymentAttempt, getOrCreatePaymentAttempt, paymentAttemptMessage, rentalPaymentStatus,
} from './payments/paymentExperience';
import DisputeCenter from './disputes/DisputeCenter';
import { canOpenDispute } from './disputes/disputeExperience';
import {
  CONVERSATION_POLL_INTERVAL_MS, MESSAGE_POLL_INTERVAL_MS, conversationContext,
  mergeConversationMessages, messagingErrorMessage, totalUnreadMessages,
} from './messaging/messagingExperience';
import {
  filterNotifications, notificationErrorMessage, notificationEvent,
  notificationTarget, unreadNotificationCount,
} from './notifications/notificationExperience';
import { useI18n } from '../i18n';

const EMPTY_DATA = {
  bookings: [], disputes: [], financials: [], equipment: [], conversations: [], notifications: [], reviews: [], earnings: null,
};

const ACTION_ICONS = {
  calendar: CalendarDays,
  return: RotateCcw,
  shield: ShieldCheck,
  message: MessageSquare,
  bell: Bell,
  equipment: Package,
  wallet: WalletCards,
  dispute: Scale,
};

const NOTIFICATION_ICONS = {
  reservation_requested: CalendarDays,
  reservation_accepted: CalendarDays,
  reservation_rejected: CalendarDays,
  kyc_updated: ShieldCheck,
  payment_updated: WalletCards,
  deposit_updated: WalletCards,
  inspection_required: FileText,
  message_received: MessageSquare,
  dispute_updated: Scale,
  payout_updated: CircleDollarSign,
};

const ACTION_TONES = {
  warning: 'border-warning/20 bg-warning-subtle text-warning',
  info: 'border-info/20 bg-info-subtle text-info',
  error: 'border-error/20 bg-error-subtle text-error',
  success: 'border-success/20 bg-success-subtle text-success',
  neutral: 'border-border bg-stone-50 text-muted',
};

const DOCUMENT_STATUSES = new Set([
  'confirmee', 'prete_remise', 'en_cours',
  'en_attente_validation', 'termine', 'en_litige', 'resolu',
]);

function handleRovingTabKey(event, index, values, onSelect) {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
  event.preventDefault();
  const nextIndex = event.key === 'Home' ? 0
    : event.key === 'End' ? values.length - 1
      : event.key === 'ArrowRight' ? (index + 1) % values.length
        : (index - 1 + values.length) % values.length;
  onSelect(values[nextIndex]);
  requestAnimationFrame(() => event.currentTarget.parentElement?.querySelectorAll('[role="tab"]')[nextIndex]?.focus());
}

function SectionSkeleton() {
  return (
    <div className="space-y-4" role="status">
      <span className="sr-only">Chargement du compte</span>
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-28 w-full" />
      <Skeleton className="h-28 w-full" />
    </div>
  );
}

function SectionIntro({ title, description, action }) {
  return (
    <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        <h2 className="font-display text-xl font-bold text-ink">{title}</h2>
        {description && <p className="mt-1 text-sm leading-6 text-muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}

function InlineError({ message, onRetry }) {
  if (!message) return null;
  return (
    <div role="alert" className="mb-4 flex flex-col gap-3 rounded-card border border-error/20 bg-error-subtle p-4 sm:flex-row sm:items-center sm:justify-between">
      <p className="text-sm font-semibold text-error">{message}</p>
      {onRetry && <Button variant="secondary" size="sm" onClick={onRetry}>Réessayer</Button>}
    </div>
  );
}

function BookingCard({ booking, disputes, financial, userId, onOpenContract, onOpenInspection, onOpenDispute, onAction, acting }) {
  const { formatDate, formatMAD: formatMoney } = useI18n();
  const role = roleForBooking(booking, userId);
  const status = bookingStatus(booking.statut_reservation);
  const payment = rentalPaymentStatus(financial?.rental_payment?.status);
  const image = Array.isArray(booking.article_photos) ? booking.article_photos[0] : null;
  const canOpenDocument = DOCUMENT_STATUSES.has(booking.statut_reservation);
  const disputeDataAvailable = Array.isArray(disputes);

  return (
    <Card className="overflow-hidden">
      <div className="grid gap-0 sm:grid-cols-[128px_minmax(0,1fr)]">
        <div className="flex min-h-28 items-center justify-center bg-stone-100">
          {image ? <img src={image} alt="" className="h-full w-full object-cover" /> : <Package aria-hidden="true" className="size-8 text-slate-400" />}
        </div>
        <div className="p-4 sm:p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <Badge variant={role === 'owner' ? 'action' : 'primary'}>{role === 'owner' ? 'Je suis propriétaire' : 'Je suis locataire'}</Badge>
                <Badge variant={status.tone}>{status.label}</Badge>
              </div>
              <h3 className="mt-3 truncate font-display text-lg font-bold text-ink">{booking.article_titre || 'Matériel Lokiini'}</h3>
              <p className="mt-1 flex items-center gap-1.5 text-xs text-muted">
                <CalendarDays aria-hidden="true" className="size-3.5" />
                {formatDate(booking.date_debut)} — {formatDate(booking.date_fin)}
              </p>
            </div>
            <div className="shrink-0 sm:text-end">
              <p className="text-sm font-bold text-ink">{formatMoney(booking.prix_total)}</p>
              <Badge variant={payment.tone} className="mt-2">{payment.label}</Badge>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2 border-t border-border pt-4">
            {role === 'owner' && booking.statut_reservation === 'en_attente_approbation' && (
              <>
                <Button size="sm" loading={acting === `${booking.id}:owner_accept`} loadingLabel="Acceptation…" onClick={() => onAction(booking, 'owner_accept')}>
                  <Check aria-hidden="true" className="size-4" /> Accepter
                </Button>
                <Button size="sm" variant="secondary" loading={acting === `${booking.id}:owner_reject`} loadingLabel="Refus…" onClick={() => onAction(booking, 'owner_reject')}>
                  <X aria-hidden="true" className="size-4" /> Refuser
                </Button>
              </>
            )}
            {canOpenDocument && (
              <Button size="sm" variant="secondary" onClick={() => onOpenContract?.(booking.id, booking)}>
                <FileText aria-hidden="true" className="size-4" /> Contrat
              </Button>
            )}
            {booking.statut_reservation === 'prete_remise' && (
              <Button size="sm" variant="secondary" onClick={() => onOpenInspection?.(booking, 'check_in')}>Préparer la remise</Button>
            )}
            {booking.statut_reservation === 'en_cours' && (
              <Button size="sm" variant="secondary" onClick={() => onOpenInspection?.(booking, 'check_out')}>Préparer le retour</Button>
            )}
            {booking.statut_reservation === 'en_attente_validation' && (
              <Button size="sm" variant="secondary" onClick={() => onOpenInspection?.(booking, 'check_out')}>Vérifier le retour</Button>
            )}
            {disputeDataAvailable && booking.statut_reservation === 'en_litige' && (
              <Button size="sm" variant="secondary" onClick={() => onOpenDispute?.(booking)}>Suivre le dossier</Button>
            )}
            {disputeDataAvailable && booking.statut_reservation !== 'en_litige' && canOpenDispute(booking, disputes) && (
              <Button size="sm" variant="ghost" onClick={() => onOpenDispute?.(booking)}><Scale aria-hidden="true" className="size-4" />Ouvrir un dossier</Button>
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}

export default function AccountDashboard({
  onNewEquipment, onOpenContract, onOpenInspection, onOpenKYC,
  onNavigate, currentUser, onUserUpdated,
  refreshKey,
}) {
  const { t, formatDate, formatDateTime, formatMAD: formatMoney, normalizePhone } = useI18n();
  const { toast } = useToast();
  const [activeSection, setActiveSection] = useState(() => accountSectionFromHash(window.location.hash));
  const [bookingFilter, setBookingFilter] = useState('all');
  const [data, setData] = useState(EMPTY_DATA);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [acting, setActing] = useState(null);
  const [selectedConversationId, setSelectedConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [messagesError, setMessagesError] = useState(null);
  const [messageDraft, setMessageDraft] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [messagesRefreshing, setMessagesRefreshing] = useState(false);
  const [messagesUpdatedAt, setMessagesUpdatedAt] = useState(null);
  const [notificationFilter, setNotificationFilter] = useState('all');
  const [notificationsRefreshing, setNotificationsRefreshing] = useState(false);
  const [notificationAction, setNotificationAction] = useState(null);
  const [profile, setProfile] = useState({ nom_complet: '', telephone: '', city: '', company_name: '', company_ice: '' });
  const [savingProfile, setSavingProfile] = useState(false);
  const [paymentAttempts, setPaymentAttempts] = useState({});
  const [disputeBookingId, setDisputeBookingId] = useState(null);
  const paymentInFlightRef = useRef(new Set());
  const paymentKeysRef = useRef(new Map());
  const messagingPollInFlightRef = useRef(false);

  useEffect(() => {
    setProfile({
      nom_complet: currentUser?.nom_complet || '',
      telephone: currentUser?.telephone || '',
      city: currentUser?.city || '',
      company_name: currentUser?.company_name || '',
      company_ice: currentUser?.company_ice || '',
    });
  }, [currentUser]);

  const loadDashboard = useCallback(async ({ quiet = false } = {}) => {
    if (quiet) setRefreshing(true);
    else setLoading(true);

    const requests = {
      bookings: getBookings('all'),
      disputes: getDisputes(),
      financials: getFinancialSummaries(),
      equipment: getMyEquipment(),
      conversations: getUserConversations(),
      notifications: getNotifications(),
      reviews: currentUser?.id ? getUserReviews(currentUser.id) : Promise.resolve([]),
      earnings: getOwnerEarningsDashboard('mois'),
    };
    const keys = Object.keys(requests);
    const results = await Promise.allSettled(Object.values(requests));
    const nextErrors = {};

    setData((current) => {
      const next = { ...current };
      results.forEach((result, index) => {
        const key = keys[index];
        if (result.status === 'fulfilled') next[key] = result.value ?? (key === 'earnings' ? null : []);
        else {
          nextErrors[key] = result.reason?.message || 'Ces informations sont temporairement indisponibles.';
          next[key] = key === 'earnings' ? null : [];
        }
      });
      return next;
    });
    setErrors(nextErrors);
    setLoading(false);
    setRefreshing(false);
  }, [currentUser?.id]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard, refreshKey]);

  useEffect(() => {
    data.financials.forEach((financial) => {
      if (['succeeded', 'cancelled', 'refunded'].includes(financial.rental_payment?.status)) {
        const bookingId = normalizeId(financial.booking_id);
        paymentKeysRef.current.delete(bookingId);
        clearPaymentAttempt(bookingId);
      }
    });
  }, [data.financials]);

  const actions = useMemo(() => buildOverviewActions({ ...data, user: currentUser }), [data, currentUser]);
  const nextBooking = useMemo(() => nextRenterBooking(data.bookings, currentUser?.id), [data.bookings, currentUser?.id]);
  const selectedConversation = data.conversations.find((conversation) => normalizeId(conversation.id) === normalizeId(selectedConversationId)) || null;
  const unreadMessages = totalUnreadMessages(data.conversations);
  const unreadNotifications = unreadNotificationCount(data.notifications);
  const pendingOwnerRequests = data.bookings.filter((booking) => (
    roleForBooking(booking, currentUser?.id) === 'owner' && booking.statut_reservation === 'en_attente_approbation'
  )).length;
  const equipmentAttention = data.equipment.filter((item) => item.statut !== 'actif' || item.is_available === false).length;
  const activeDisputes = data.disputes.filter((item) => item.status !== 'resolved').length;
  const sectionCounts = {
    bookings: pendingOwnerRequests,
    equipment: equipmentAttention,
    messages: unreadMessages,
    verification: currentUser?.statut_verification === 'verified' ? 0 : 1,
    notifications: unreadNotifications,
    disputes: activeDisputes,
  };

  const goToSection = (section, options = {}) => {
    if (options.bookingFilter) setBookingFilter(options.bookingFilter);
    setActiveSection(section);
    window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}${accountSectionHash(section)}`);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  useEffect(() => {
    const syncSectionFromHash = () => setActiveSection(accountSectionFromHash(window.location.hash));
    window.addEventListener('hashchange', syncSectionFromHash);
    return () => window.removeEventListener('hashchange', syncSectionFromHash);
  }, []);

  const openDispute = (booking) => {
    setDisputeBookingId(booking.id);
    goToSection('disputes');
  };

  const handleBookingAction = async (booking, action) => {
    if (action === 'owner_reject' && !window.confirm('Refuser cette demande de réservation ?')) return;
    const actionKey = `${booking.id}:${action}`;
    setActing(actionKey);
    try {
      await performBookingAction(booking.id, action);
      toast({
        title: action === 'owner_accept' ? 'Demande acceptée' : 'Demande refusée',
        description: 'Le statut a été validé par le backend Lokiini.',
        variant: action === 'owner_accept' ? 'success' : 'info',
      });
      await loadDashboard({ quiet: true });
    } catch (error) {
      toast({ title: 'Action impossible', description: error.message, variant: 'error' });
    } finally {
      setActing(null);
    }
  };

  const handlePaymentInitiation = async (financial, booking) => {
    const bookingId = normalizeId(financial?.booking_id);
    if (!bookingId || !booking || paymentInFlightRef.current.has(bookingId)) return;
    paymentInFlightRef.current.add(bookingId);
    const sourceStatus = financial.rental_payment?.status || 'not_started';
    let keyEntry = paymentKeysRef.current.get(bookingId);
    if (!keyEntry || (sourceStatus === 'failed' && keyEntry.sourceStatus !== 'failed')) {
      keyEntry = getOrCreatePaymentAttempt(bookingId, sourceStatus);
      paymentKeysRef.current.set(bookingId, keyEntry);
    }
    setPaymentAttempts((current) => ({ ...current, [bookingId]: { loading: true, error: null } }));
    try {
      await initiateBookingPayment(bookingId, keyEntry.key);
      setPaymentAttempts((current) => ({ ...current, [bookingId]: { loading: false, error: null } }));
      toast({
        title: 'Tentative transmise',
        description: 'Le statut sera affiché comme payé uniquement après confirmation du backend.',
        variant: 'info',
      });
      await loadDashboard({ quiet: true });
    } catch (error) {
      if (['PAYMENT_FAILED', 'PAYMENT_DECLINED'].includes(error.code)) {
        paymentKeysRef.current.delete(bookingId);
        clearPaymentAttempt(bookingId);
      }
      setPaymentAttempts((current) => ({
        ...current,
        [bookingId]: { loading: false, error: paymentAttemptMessage(error) },
      }));
    } finally {
      paymentInFlightRef.current.delete(bookingId);
    }
  };

  const refreshConversations = useCallback(async ({ quiet = true } = {}) => {
    if (!quiet) setMessagesRefreshing(true);
    try {
      const conversations = await getUserConversations();
      setData((current) => ({ ...current, conversations: conversations || [] }));
      setErrors((current) => {
        if (!current.conversations) return current;
        const next = { ...current };
        delete next.conversations;
        return next;
      });
      setMessagesUpdatedAt(new Date());
    } catch (error) {
      setErrors((current) => ({
        ...current,
        conversations: messagingErrorMessage(error, 'Les conversations n’ont pas pu être actualisées.'),
      }));
    } finally {
      if (!quiet) setMessagesRefreshing(false);
    }
  }, []);

  const loadConversation = useCallback(async (conversationId, { quiet = false } = {}) => {
    if (!conversationId) return;
    if (!quiet) setMessagesLoading(true);
    setMessagesError(null);
    try {
      const history = await getConversationMessages(conversationId);
      setMessages((current) => (
        quiet ? mergeConversationMessages(current, history || []) : mergeConversationMessages([], history || [])
      ));
      setData((current) => ({
        ...current,
        conversations: current.conversations.map((item) => (
          normalizeId(item.id) === normalizeId(conversationId) ? { ...item, messages_non_lus: 0 } : item
        )),
      }));
      setMessagesUpdatedAt(new Date());
    } catch (error) {
      setMessagesError(messagingErrorMessage(error, 'L’historique de la conversation n’a pas pu être chargé.'));
      if (!quiet) setMessages([]);
    } finally {
      if (!quiet) setMessagesLoading(false);
    }
  }, []);

  const openConversation = (conversation) => {
    setSelectedConversationId(conversation.id);
    setMessageDraft('');
    loadConversation(conversation.id);
  };

  useEffect(() => {
    if (activeSection !== 'messages') return undefined;
    const poll = async () => {
      if (messagingPollInFlightRef.current) return;
      messagingPollInFlightRef.current = true;
      try {
        await refreshConversations({ quiet: true });
        if (selectedConversationId) await loadConversation(selectedConversationId, { quiet: true });
      } finally {
        messagingPollInFlightRef.current = false;
      }
    };
    const messageTimer = window.setInterval(poll, MESSAGE_POLL_INTERVAL_MS);
    return () => window.clearInterval(messageTimer);
  }, [activeSection, loadConversation, refreshConversations, selectedConversationId]);

  useEffect(() => {
    if (activeSection === 'messages') return undefined;
    const conversationTimer = window.setInterval(
      () => refreshConversations({ quiet: true }),
      CONVERSATION_POLL_INTERVAL_MS,
    );
    return () => window.clearInterval(conversationTimer);
  }, [activeSection, refreshConversations]);

  const submitMessage = async (event) => {
    event.preventDefault();
    const content = messageDraft.trim();
    if (!content || !selectedConversation || sendingMessage) return;
    setSendingMessage(true);
    setMessagesError(null);
    try {
      const message = await sendConversationMessage(selectedConversation.id, content);
      setMessages((current) => mergeConversationMessages(current, [message]));
      setMessageDraft('');
      setData((current) => ({
        ...current,
        conversations: current.conversations.map((item) => (
          normalizeId(item.id) === normalizeId(selectedConversation.id)
            ? { ...item, dernier_message: message.contenu, modifie_le: message.cree_le }
            : item
        )),
      }));
    } catch (error) {
      setMessagesError(messagingErrorMessage(error, 'Le message n’a pas pu être envoyé.'));
    } finally {
      setSendingMessage(false);
    }
  };

  const refreshNotifications = useCallback(async ({ quiet = false } = {}) => {
    if (!quiet) setNotificationsRefreshing(true);
    try {
      const notifications = await getNotifications();
      setData((current) => ({ ...current, notifications: notifications || [] }));
      setErrors((current) => {
        if (!current.notifications) return current;
        const next = { ...current };
        delete next.notifications;
        return next;
      });
    } catch (error) {
      setErrors((current) => ({ ...current, notifications: notificationErrorMessage(error) }));
    } finally {
      if (!quiet) setNotificationsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => refreshNotifications({ quiet: true }), 30_000);
    return () => window.clearInterval(timer);
  }, [refreshNotifications]);

  const setNotificationReadState = async (notification, isRead) => {
    const actionKey = `${notification.id}:${isRead ? 'read' : 'unread'}`;
    setNotificationAction(actionKey);
    try {
      const result = await updateNotificationRead(notification.id, isRead);
      setData((current) => ({
        ...current,
        notifications: current.notifications.map((item) => (
          normalizeId(item.id) === normalizeId(notification.id)
            ? { ...item, est_lu: result.est_lu, lu_le: result.lu_le }
            : item
        )),
      }));
      return true;
    } catch (error) {
      toast({ title: 'Notification non mise à jour', description: notificationErrorMessage(error), variant: 'error' });
      return false;
    } finally {
      setNotificationAction(null);
    }
  };

  const openNotification = async (notification) => {
    if (!notification.est_lu) await setNotificationReadState(notification, true);
    const target = notificationTarget(notification);
    goToSection(target.section);
    if (target.section === 'messages' && target.resourceId) {
      const conversation = data.conversations.find((item) => normalizeId(item.id) === normalizeId(target.resourceId));
      if (conversation) openConversation(conversation);
    }
  };

  const readAllNotifications = async () => {
    if (!unreadNotifications) return;
    setNotificationAction('all');
    try {
      await markAllNotificationsRead();
      const readAt = new Date().toISOString();
      setData((current) => ({
        ...current,
        notifications: current.notifications.map((item) => ({ ...item, est_lu: true, lu_le: item.lu_le || readAt })),
      }));
    } catch (error) {
      toast({ title: 'Notifications non mises à jour', description: notificationErrorMessage(error), variant: 'error' });
    } finally {
      setNotificationAction(null);
    }
  };

  const saveProfile = async (event) => {
    event.preventDefault();
    setSavingProfile(true);
    try {
      const updated = await updateCurrentUser(profile);
      onUserUpdated?.(updated);
      toast({ title: 'Profil mis à jour', description: 'Vos informations de compte ont été enregistrées.', variant: 'success' });
    } catch (error) {
      toast({ title: 'Profil non enregistré', description: error.message, variant: 'error' });
    } finally {
      setSavingProfile(false);
    }
  };

  const renderOverview = () => {
    if (loading) return <SectionSkeleton />;
    const partialFailureCount = Object.keys(errors).length;
    return (
      <div className="space-y-6">
        {partialFailureCount > 0 && (
          <InlineError message={`${partialFailureCount} source${partialFailureCount > 1 ? 's' : ''} de votre compte n’a pas pu être chargée. Les autres informations restent disponibles.`} onRetry={() => loadDashboard({ quiet: true })} />
        )}

        <section aria-labelledby="actions-title">
          <SectionIntro title="À faire maintenant" description="Uniquement les actions détectées dans vos réservations, messages et informations de compte." />
          {actions.length ? (
            <div className="grid gap-3 sm:grid-cols-2">
              {actions.map((action) => {
                const Icon = ACTION_ICONS[action.icon] || ChevronRight;
                return (
                  <button
                    key={action.id}
                    type="button"
                    onClick={() => goToSection(action.section, { bookingFilter: action.bookingFilter })}
                    className="group flex min-h-28 items-start gap-4 rounded-card border border-border bg-surface p-4 text-start shadow-subtle transition hover:border-primary/25 hover:shadow-card"
                  >
                    <span className={`flex size-10 shrink-0 items-center justify-center rounded-xl border ${ACTION_TONES[action.tone] || ACTION_TONES.neutral}`}>
                      <Icon aria-hidden="true" className="size-5" />
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-sm font-bold text-ink">{action.title}</span>
                      <span className="mt-1 block text-xs leading-5 text-muted">{action.description}</span>
                    </span>
                    <ChevronRight aria-hidden="true" className="mt-1 size-4 shrink-0 text-slate-400 transition group-hover:translate-x-0.5 group-hover:text-primary" />
                  </button>
                );
              })}
            </div>
          ) : (
            <Card><EmptyState icon={Check} title="Rien d’urgent" description="Aucune action prioritaire n’est remontée par vos données Lokiini pour le moment." /></Card>
          )}
        </section>

        <div className="grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(280px,0.7fr)]">
          <section aria-labelledby="next-rental-title">
            <SectionIntro title="Prochaine location" />
            {nextBooking ? (
              <Card className="p-5">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <Badge variant={bookingStatus(nextBooking.statut_reservation).tone}>{bookingStatus(nextBooking.statut_reservation).label}</Badge>
                    <h3 className="mt-3 truncate font-display text-xl font-bold text-ink">{nextBooking.article_titre}</h3>
                    <p className="mt-2 flex items-center gap-2 text-sm text-muted"><CalendarDays aria-hidden="true" className="size-4" />{formatDate(nextBooking.date_debut)} — {formatDate(nextBooking.date_fin)}</p>
                  </div>
                  <Button variant="secondary" size="sm" onClick={() => goToSection('bookings', { bookingFilter: 'renter' })}>Voir la réservation <ArrowRight aria-hidden="true" className="size-4" /></Button>
                </div>
              </Card>
            ) : (
              <Card><EmptyState icon={CalendarDays} title="Aucune location à venir" description="Vos prochaines réservations confirmées ou en cours apparaîtront ici." action={<Button size="sm" onClick={() => onNavigate?.('catalog')}>Parcourir le matériel</Button>} /></Card>
            )}
          </section>

          <section aria-labelledby="account-uses-title">
            <SectionIntro title="Votre compte, deux usages" />
            <Card className="divide-y divide-border">
              <button type="button" onClick={() => goToSection('bookings', { bookingFilter: 'renter' })} className="flex w-full items-center gap-3 p-4 text-start hover:bg-stone-50">
                <CalendarDays aria-hidden="true" className="size-5 text-primary" />
                <span className="flex-1"><span className="block text-sm font-bold text-ink">Louer du matériel</span><span className="text-xs text-muted">Suivre mes réservations</span></span>
                <ChevronRight aria-hidden="true" className="size-4 text-muted" />
              </button>
              <button type="button" onClick={() => goToSection('equipment')} className="flex w-full items-center gap-3 p-4 text-start hover:bg-stone-50">
                <Package aria-hidden="true" className="size-5 text-action" />
                <span className="flex-1"><span className="block text-sm font-bold text-ink">Proposer du matériel</span><span className="text-xs text-muted">Gérer mes annonces</span></span>
                <ChevronRight aria-hidden="true" className="size-4 text-muted" />
              </button>
            </Card>
          </section>
        </div>
      </div>
    );
  };

  const renderBookings = () => {
    const filtered = filterBookings(data.bookings, bookingFilter, currentUser?.id);
    const filters = [
      ['all', 'Toutes'], ['renter', 'Mes locations'], ['owner', 'Demandes reçues'],
    ];
    return (
      <section>
        <SectionIntro title="Toutes mes réservations" description="Le même compte regroupe les locations que vous réservez et les demandes reçues pour votre matériel." />
        <InlineError message={errors.bookings && `Réservations indisponibles : ${errors.bookings}`} onRetry={() => loadDashboard({ quiet: true })} />
        <div className="mb-5 flex gap-1 overflow-x-auto rounded-control bg-stone-100 p-1" role="tablist" aria-label="Filtrer les réservations" aria-orientation="horizontal">
          {filters.map(([value, label], index) => (
            <button key={value} id={`booking-filter-${value}`} type="button" role="tab" tabIndex={bookingFilter === value ? 0 : -1} aria-selected={bookingFilter === value} aria-controls="booking-filter-panel" onClick={() => setBookingFilter(value)} onKeyDown={(event) => handleRovingTabKey(event, index, filters.map(([filterValue]) => filterValue), setBookingFilter)} className={`min-h-10 flex-1 whitespace-nowrap rounded-lg px-3 text-sm font-bold ${bookingFilter === value ? 'bg-white text-primary shadow-subtle' : 'text-muted'}`}>{label}</button>
          ))}
        </div>
        <div id="booking-filter-panel" role="tabpanel" aria-labelledby={`booking-filter-${bookingFilter}`} tabIndex={0} className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30">
          {loading ? <SectionSkeleton /> : filtered.length ? (
            <div className="space-y-4">
              {filtered.map((booking) => <BookingCard key={booking.id} booking={booking} disputes={errors.disputes ? null : data.disputes} financial={data.financials.find((item) => normalizeId(item.booking_id) === normalizeId(booking.id))} userId={currentUser?.id} onOpenContract={onOpenContract} onOpenInspection={onOpenInspection} onOpenDispute={openDispute} onAction={handleBookingAction} acting={acting} />)}
            </div>
          ) : (
            <Card><EmptyState icon={CalendarDays} title="Aucune réservation dans cette vue" description="Les nouvelles demandes et vos locations apparaîtront ici avec leur statut réel." action={bookingFilter !== 'owner' && <Button size="sm" onClick={() => onNavigate?.('catalog')}>Parcourir le catalogue</Button>} /></Card>
          )}
        </div>
      </section>
    );
  };

  const renderEquipment = () => (
    <section>
      <SectionIntro title="Mon matériel" description="Toutes les annonces publiées avec ce compte." action={<Button size="sm" variant="action" onClick={onNewEquipment}>Publier du matériel</Button>} />
      <InlineError message={errors.equipment && `Matériel indisponible : ${errors.equipment}`} onRetry={() => loadDashboard({ quiet: true })} />
      {loading ? <SectionSkeleton /> : data.equipment.length ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {data.equipment.map((item) => {
            const photo = Array.isArray(item.photos) ? item.photos[0] : null;
            const needsAttention = item.statut !== 'actif' || item.is_available === false;
            return (
              <Card key={item.id} className="overflow-hidden">
                <div className="flex aspect-[16/10] items-center justify-center bg-stone-100">
                  {photo ? <img src={photo} alt="" className="size-full object-cover" /> : <Package aria-hidden="true" className="size-9 text-slate-400" />}
                </div>
                <div className="p-4">
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant={needsAttention ? 'warning' : 'success'}>{needsAttention ? (item.is_available === false ? 'Indisponible' : item.statut) : 'En ligne'}</Badge>
                    <span className="text-sm font-bold text-ink">{formatMoney(item.prix_par_jour)}<span className="font-normal text-muted">/jour</span></span>
                  </div>
                  <h3 className="mt-3 line-clamp-2 font-display text-lg font-bold text-ink">{item.titre}</h3>
                  <p className="mt-2 flex items-center gap-1.5 text-xs text-muted"><MapPin aria-hidden="true" className="size-3.5" />{item.city || 'Localisation indisponible'}</p>
                </div>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card><EmptyState icon={Package} title="Aucun matériel publié" description="Vous pouvez louer et proposer du matériel avec le même compte." action={<Button size="sm" variant="action" onClick={onNewEquipment}>Publier mon premier matériel</Button>} /></Card>
      )}
    </section>
  );

  const renderMessages = () => {
    const context = conversationContext(selectedConversation);
    return (
      <section>
        <SectionIntro
          title="Messages"
          description="Échanges privés liés à un équipement ou à une réservation Lokiini."
          action={<Button size="sm" variant="secondary" loading={messagesRefreshing} onClick={() => refreshConversations({ quiet: false })}><RotateCcw aria-hidden="true" className="size-4" />Actualiser</Button>}
        />
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs text-muted">
          <p>Actualisation automatique par interrogation du serveur, toutes les 8 secondes.</p>
          {messagesUpdatedAt && <p>Dernière vérification : {formatDateTime(messagesUpdatedAt, { hour: '2-digit', minute: '2-digit' })}</p>}
        </div>
        <InlineError message={errors.conversations && `Conversations indisponibles : ${errors.conversations}`} onRetry={() => refreshConversations({ quiet: false })} />
        {loading ? <SectionSkeleton /> : data.conversations.length ? (
          <Card className="grid min-h-[520px] overflow-hidden sm:min-h-[560px] md:grid-cols-[320px_minmax(0,1fr)]">
            <div className={`${selectedConversation ? 'hidden md:block' : 'block'} border-b border-border bg-white md:border-b-0 md:border-e`}>
              <div className="flex items-center justify-between border-b border-border px-4 py-3">
                <p className="text-sm font-bold text-ink">Conversations</p>
                {unreadMessages > 0 && <Badge variant="primary">{unreadMessages} non lu{unreadMessages > 1 ? 's' : ''}</Badge>}
              </div>
              <div className="max-h-72 overflow-y-auto md:max-h-[510px]">
                {data.conversations.map((conversation) => {
                  const itemContext = conversationContext(conversation);
                  const selected = normalizeId(selectedConversationId) === normalizeId(conversation.id);
                  return (
                    <button
                      key={conversation.id}
                      type="button"
                      onClick={() => openConversation(conversation)}
                      aria-current={selected ? 'true' : undefined}
                      className={`flex w-full items-start gap-3 border-b border-border p-4 text-start transition-colors hover:bg-stone-50 ${selected ? 'bg-primary-subtle' : ''}`}
                    >
                      <Avatar src={conversation.autre_utilisateur_avatar} name={conversation.autre_utilisateur_nom} size="sm" />
                      <span className="min-w-0 flex-1">
                        <span className="flex items-start justify-between gap-2">
                          <span className={`truncate text-sm ${conversation.messages_non_lus > 0 ? 'font-extrabold' : 'font-bold'} text-ink`}>{conversation.autre_utilisateur_nom}</span>
                          {conversation.messages_non_lus > 0 && <Badge variant="primary" aria-label={`${conversation.messages_non_lus} messages non lus`}>{conversation.messages_non_lus}</Badge>}
                        </span>
                        {itemContext?.title && <span className="mt-1 block truncate text-[11px] font-semibold text-primary">{itemContext.eyebrow} · {itemContext.title}</span>}
                        <span className={`mt-1 block truncate text-xs ${conversation.messages_non_lus > 0 ? 'font-semibold text-ink' : 'text-muted'}`}>{conversation.dernier_message || 'Aucun message'}</span>
                        {conversation.modifie_le && <span className="mt-1 block text-[10px] text-muted">{formatDateTime(conversation.modifie_le, { dateStyle: 'short', timeStyle: 'short' })}</span>}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
            <div className={`${selectedConversation ? 'flex' : 'hidden md:flex'} min-h-[420px] min-w-0 flex-col bg-stone-50/60`}>
              {selectedConversation ? (
                <>
                  <div className="border-b border-border bg-white p-4">
                    <div className="flex items-center gap-3">
                      <Button variant="ghost" size="icon" className="-ms-2 md:hidden" onClick={() => setSelectedConversationId(null)} aria-label="Retour aux conversations"><ArrowLeft aria-hidden="true" className="rtl-flip size-5" /></Button>
                      <Avatar src={selectedConversation.autre_utilisateur_avatar} name={selectedConversation.autre_utilisateur_nom} size="sm" />
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-bold text-ink">{selectedConversation.autre_utilisateur_nom}</p>
                        {context?.title && <p className="truncate text-xs font-semibold text-primary">{context.eyebrow} · {context.title}</p>}
                      </div>
                      {context?.reference && <Badge variant="neutral">{context.reference}</Badge>}
                    </div>
                    {selectedConversation.reservation_id && (
                      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 rounded-control bg-stone-50 px-3 py-2 text-[11px] text-muted">
                        {selectedConversation.reservation_statut && <span>Statut : <strong className="text-ink">{bookingStatus(selectedConversation.reservation_statut).label}</strong></span>}
                        {selectedConversation.reservation_date_debut && <span>Du {formatDate(selectedConversation.reservation_date_debut)} au {formatDate(selectedConversation.reservation_date_fin)}</span>}
                      </div>
                    )}
                  </div>
                  {messagesError && messages.length > 0 && <div className="border-b border-error/20 bg-error-subtle p-3 text-xs text-error"><div className="flex items-center justify-between gap-3"><span>{messagesError}</span><Button size="sm" variant="ghost" onClick={() => loadConversation(selectedConversation.id)}>Réessayer</Button></div></div>}
                  <div className="flex max-h-[440px] min-h-72 flex-1 flex-col gap-3 overflow-y-auto p-4" aria-live="polite">
                    {messagesLoading ? <SectionSkeleton /> : messagesError && !messages.length ? <ErrorState title="Conversation indisponible" description={messagesError} onRetry={() => loadConversation(selectedConversation.id)} /> : messages.length ? messages.map((message) => {
                      const mine = normalizeId(message.expediteur_id) === normalizeId(currentUser?.id);
                      return <div key={message.id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}><div className={`max-w-[88%] whitespace-pre-wrap break-words rounded-2xl px-4 py-3 text-sm leading-6 sm:max-w-[76%] ${mine ? 'rounded-ee-md bg-primary text-white' : 'rounded-es-md border border-border bg-white text-ink'}`}><p>{message.contenu}</p><p className={`mt-1 text-[10px] ${mine ? 'text-white/70' : 'text-muted'}`}>{message.cree_le ? formatDateTime(message.cree_le, { dateStyle: 'short', timeStyle: 'short' }) : ''}</p></div></div>;
                    }) : <EmptyState icon={MessageSquare} title="Aucun message" description="Envoyez le premier message dans ce contexte." />}
                  </div>
                  <form onSubmit={submitMessage} className="border-t border-border bg-white p-3">
                    <div className="flex gap-2"><Input aria-label="Votre message" value={messageDraft} maxLength={2000} onChange={(event) => setMessageDraft(event.target.value)} placeholder="Écrire un message…" className="flex-1" /><Button type="submit" size="icon" loading={sendingMessage} disabled={!messageDraft.trim() || messagesLoading} aria-label="Envoyer"><Send aria-hidden="true" className="size-4" /></Button></div>
                    <p className="mt-2 text-[10px] text-muted">{messageDraft.length}/2000 · En cas d’erreur réseau, Lokiini ne renvoie jamais automatiquement votre message.</p>
                  </form>
                </>
              ) : <EmptyState icon={MessageSquare} title="Choisissez une conversation" description="Sélectionnez un échange pour consulter son utilisateur, son équipement et sa réservation lorsqu’ils existent." />}
            </div>
          </Card>
        ) : <Card><EmptyState icon={MessageSquare} title="Aucune conversation" description="Vos échanges réels avec les propriétaires et locataires apparaîtront ici après un premier message lié à une annonce ou une réservation." /></Card>}
      </section>
    );
  };

  const renderDisputes = () => (
    <DisputeCenter
      bookings={data.bookings}
      disputes={data.disputes}
      currentUser={currentUser}
      initialBookingId={disputeBookingId}
      loading={loading}
      error={errors.disputes}
      onRefresh={() => loadDashboard({ quiet: true })}
    />
  );

  const renderPayments = () => (
    <section>
      <SectionIntro title="Paiements et dépôts" description="Le paiement règle la location. Le dépôt est une autorisation remboursable distincte, suivie séparément par le backend." />
      <InlineError message={errors.financials && `Paiements indisponibles : ${errors.financials}`} onRetry={() => loadDashboard({ quiet: true })} />
      {loading ? <SectionSkeleton /> : data.financials.length ? <div className="space-y-4">{data.financials.map((financial) => {
        const booking = data.bookings.find((item) => normalizeId(item.id) === normalizeId(financial.booking_id));
        return <PaymentStatusPanel key={financial.booking_id} financial={financial} booking={booking} userId={currentUser?.id} formatMoney={formatMoney} formatDate={formatDate} attempt={paymentAttempts[normalizeId(financial.booking_id)]} onInitiate={() => handlePaymentInitiation(financial, booking)} onRefresh={() => loadDashboard({ quiet: true })} />;
      })}</div> : <Card><EmptyState icon={WalletCards} title="Aucun paiement à afficher" description="Les informations financières apparaîtront après une demande de réservation." /></Card>}
    </section>
  );

  const renderEarnings = () => {
    const earnings = data.earnings;
    const hasActivity = earnings && (Number(earnings.total_gains_bruts_mad) > 0 || Number(earnings.nombre_locations_terminees) > 0);
    return (
      <section>
        <SectionIntro title="Revenus propriétaire" description="Uniquement calculés à partir des versements confirmés dans le registre financier." />
        <InlineError message={errors.earnings && `Revenus indisponibles : ${errors.earnings}`} onRetry={() => loadDashboard({ quiet: true })} />
        {loading ? <SectionSkeleton /> : earnings ? <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Card className="p-5"><p className="text-xs font-bold text-muted">Locations liées aux versements confirmés</p><p className="mt-2 font-display text-2xl font-bold text-ink">{formatMoney(earnings.total_gains_bruts_mad)}</p></Card>
            <Card className="p-5"><p className="text-xs font-bold text-muted">Frais de plateforme confirmés</p><p className="mt-2 font-display text-2xl font-bold text-ink">{formatMoney(earnings.total_commissions_plateforme_mad)}</p></Card>
            <Card className="p-5"><p className="text-xs font-bold text-muted">Versements nets confirmés</p><p className="mt-2 font-display text-2xl font-bold text-primary">{formatMoney(earnings.total_gains_nets_mad)}</p></Card>
          </div>
          <Card className="mt-5 p-5">
            <div className="flex items-start gap-3"><CircleDollarSign aria-hidden="true" className="mt-0.5 size-5 text-primary" /><div><h3 className="text-sm font-bold text-ink">Statut des versements</h3><p className="mt-1 text-sm text-muted">{financialStatus(earnings.payout_status).label}</p>{Number(earnings.payout_pending_mad) > 0 && <p className="mt-1 text-sm font-semibold text-ink">En attente : {formatMoney(earnings.payout_pending_mad)}</p>}</div></div>
          </Card>
          {hasActivity && Array.isArray(earnings.top_articles_rentables) && earnings.top_articles_rentables.length > 0 && <Card className="mt-5 p-5"><h3 className="text-sm font-bold text-ink">Matériel ayant généré une activité</h3><div className="mt-3 divide-y divide-border">{earnings.top_articles_rentables.map((item) => <div key={item.titre} className="flex items-center justify-between gap-4 py-3 text-sm"><span className="font-semibold text-ink">{item.titre}</span><span className="font-bold text-primary">{formatMoney(item.revenus_generes_mad)}</span></div>)}</div></Card>}
        </> : <Card><EmptyState icon={CircleDollarSign} title="Aucune donnée de revenus" description="Les revenus calculés à partir de vos locations apparaîtront ici." /></Card>}
      </section>
    );
  };

  const renderDocuments = () => {
    const documentBookings = data.bookings.filter((booking) => DOCUMENT_STATUSES.has(booking.statut_reservation));
    return <section><SectionIntro title="Documents" description="Contrats générés à partir de vos réservations confirmées, que vous soyez locataire ou propriétaire." /><InlineError message={errors.bookings && `Documents indisponibles : ${errors.bookings}`} onRetry={() => loadDashboard({ quiet: true })} />{loading ? <SectionSkeleton /> : documentBookings.length ? <div className="space-y-3">{documentBookings.map((booking) => <Card key={booking.id} className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between"><div className="flex items-start gap-3"><span className="flex size-10 items-center justify-center rounded-xl bg-primary-subtle text-primary"><FileText aria-hidden="true" className="size-5" /></span><div><h3 className="text-sm font-bold text-ink">Contrat — {booking.article_titre}</h3><p className="mt-1 text-xs text-muted">Réservation LK-{String(booking.id).slice(0, 8).toUpperCase()} · {formatDate(booking.date_debut)}</p><p className="mt-1 text-xs text-muted">Version générée disponible pour relecture. La signature dépend du prestataire configuré.</p></div></div><Button size="sm" variant="secondary" onClick={() => onOpenContract?.(booking.id, booking)}>Relire le contrat</Button></Card>)}</div> : <Card><EmptyState icon={FileText} title="Aucun contrat disponible" description="Un contrat apparaîtra lorsqu’une réservation sera confirmée." /></Card>}</section>;
  };

  const renderVerification = () => {
    const status = getKycStatus(currentUser?.statut_verification);
    return <section><SectionIntro title="Vérification d’identité" description="Une étape commune à votre activité de locataire et de propriétaire." /><Card className="p-6"><div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between"><div className="flex items-start gap-4"><span className={`flex size-12 shrink-0 items-center justify-center rounded-xl border ${ACTION_TONES[status.tone] || ACTION_TONES.neutral}`}><ShieldCheck aria-hidden="true" className="size-6" /></span><div><Badge variant={status.tone}>{status.label}</Badge><p className="mt-3 max-w-xl text-sm leading-6 text-ink">{status.description}</p><p className="mt-1 max-w-xl text-sm leading-6 text-muted">{status.guidance}</p><p className="mt-3 text-xs leading-5 text-muted">La vérification contribue à réduire la fraude, à protéger les deux parties et à soutenir les contrats et le traitement des litiges.</p></div></div>{status.key !== 'verified' && <Button onClick={onOpenKYC}>{status.actionLabel || 'Consulter le statut'}</Button>}</div></Card></section>;
  };

  const renderReviews = () => {
    const validRatings = data.reviews.map((review) => Number(review.note)).filter(Number.isFinite);
    const average = validRatings.length ? validRatings.reduce((sum, rating) => sum + rating, 0) / validRatings.length : null;
    return <section><SectionIntro title="Avis reçus" description="Uniquement les avis enregistrés pour votre identité Lokiini." /><InlineError message={errors.reviews && `Avis indisponibles : ${errors.reviews}`} onRetry={() => loadDashboard({ quiet: true })} />{loading ? <SectionSkeleton /> : data.reviews.length ? <><Card className="mb-4 flex items-center gap-4 p-5"><span className="font-display text-3xl font-bold text-ink">{average?.toFixed(1)}</span><div><div className="flex gap-0.5 text-warning" aria-label={`${average?.toFixed(1)} sur 5`}>{[1,2,3,4,5].map((value) => <Star key={value} aria-hidden="true" className={`size-4 ${value <= Math.round(average) ? 'fill-current' : ''}`} />)}</div><p className="mt-1 text-xs text-muted">{data.reviews.length} avis enregistré{data.reviews.length > 1 ? 's' : ''}</p></div></Card><div className="space-y-3">{data.reviews.map((review) => <Card key={review.id} className="p-5"><div className="flex items-center justify-between gap-3"><div className="flex items-center gap-3"><Avatar name={review.avisateur_nom} size="sm" /><div><p className="text-sm font-bold text-ink">{review.avisateur_nom}</p><p className="text-xs text-muted">{review.cree_le ? formatDate(review.cree_le) : ''}</p></div></div><Badge variant="warning" icon={Star}>{review.note}/5</Badge></div>{review.commentaire && <p className="mt-4 text-sm leading-6 text-muted">{review.commentaire}</p>}</Card>)}</div></> : <Card><EmptyState icon={Star} title="Aucun avis reçu" description="Les avis laissés après une location terminée apparaîtront ici." /></Card>}</section>;
  };

  const renderNotifications = () => {
    const visibleNotifications = filterNotifications(data.notifications, notificationFilter);
    const filters = [['all', `Toutes (${data.notifications.length})`], ['unread', `Non lues (${unreadNotifications})`]];
    return (
      <section>
        <SectionIntro
          title="Centre de notifications"
          description="Uniquement les événements réellement enregistrés pour votre compte Lokiini."
          action={<div className="flex flex-wrap gap-2"><Button size="sm" variant="secondary" loading={notificationsRefreshing} onClick={() => refreshNotifications()}><RotateCcw aria-hidden="true" className="size-4" />Actualiser</Button>{unreadNotifications > 0 && <Button size="sm" variant="ghost" loading={notificationAction === 'all'} onClick={readAllNotifications}>Tout marquer comme lu</Button>}</div>}
        />
        <InlineError message={errors.notifications && `Notifications indisponibles : ${errors.notifications}`} onRetry={() => refreshNotifications()} />
        <div role="tablist" aria-label="Filtrer les notifications" aria-orientation="horizontal" className="mb-4 flex max-w-sm rounded-xl bg-stone-100 p-1">
          {filters.map(([value, label], index) => <button key={value} id={`notification-filter-${value}`} type="button" role="tab" tabIndex={notificationFilter === value ? 0 : -1} aria-selected={notificationFilter === value} aria-controls="notification-filter-panel" onClick={() => setNotificationFilter(value)} onKeyDown={(event) => handleRovingTabKey(event, index, filters.map(([filterValue]) => filterValue), setNotificationFilter)} className={`min-h-10 flex-1 rounded-lg px-3 text-sm font-bold ${notificationFilter === value ? 'bg-white text-primary shadow-subtle' : 'text-muted'}`}>{label}</button>)}
        </div>
        <div id="notification-filter-panel" role="tabpanel" aria-labelledby={`notification-filter-${notificationFilter}`} tabIndex={0} className="focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30">
        {loading ? <SectionSkeleton /> : visibleNotifications.length ? (
          <Card className="divide-y divide-border overflow-hidden">
            {visibleNotifications.map((notification) => {
              const event = notificationEvent(notification.event_type);
              const Icon = NOTIFICATION_ICONS[notification.event_type] || Bell;
              const busy = notificationAction?.startsWith(`${notification.id}:`);
              return (
                <article key={notification.id} className={`flex items-start gap-3 p-4 sm:gap-4 sm:p-5 ${notification.est_lu ? 'bg-white' : 'bg-primary-subtle/40'}`}>
                  <span className={`mt-0.5 flex size-10 shrink-0 items-center justify-center rounded-full ${notification.est_lu ? 'bg-stone-100 text-muted' : 'bg-primary-subtle text-primary'}`}><Icon aria-hidden="true" className="size-4" /></span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2"><Badge variant={event.tone}>{event.label}</Badge>{!notification.est_lu && <Badge variant="primary">Non lue</Badge>}</div>
                    <button type="button" onClick={() => openNotification(notification)} className="mt-2 block w-full text-start">
                      <span className="block text-sm font-bold text-ink">{notification.titre}</span>
                      <span className="mt-1 block text-sm leading-6 text-muted">{notification.message}</span>
                      <span className="mt-2 block text-xs text-muted">{notification.cree_le ? formatDateTime(notification.cree_le, { dateStyle: 'medium', timeStyle: 'short' }) : ''}</span>
                    </button>
                  </div>
                  <Button size="sm" variant="ghost" loading={busy} onClick={() => setNotificationReadState(notification, !notification.est_lu)}>{notification.est_lu ? 'Marquer non lue' : 'Marquer lue'}</Button>
                </article>
              );
            })}
          </Card>
        ) : (
          <Card><EmptyState icon={Bell} title={notificationFilter === 'unread' ? 'Aucune notification non lue' : 'Aucune notification'} description={notificationFilter === 'unread' ? 'Toutes vos notifications enregistrées ont été consultées.' : 'Les événements réels de votre compte apparaîtront ici lorsqu’ils se produiront.'} /></Card>
        )}
        </div>
      </section>
    );
  };

  const renderSettings = () => <section><SectionIntro title="Paramètres du compte" description="Ces informations appartiennent à la même identité, que vous louiez ou proposiez du matériel." /><Card className="p-5 sm:p-6"><form onSubmit={saveProfile} className="space-y-5"><div className="grid gap-4 sm:grid-cols-2"><Input label="Nom complet" value={profile.nom_complet} onChange={(event) => setProfile((current) => ({ ...current, nom_complet: event.target.value }))} leadingIcon={UserRound} required /><Input type="tel" label={t('form.phone')} value={profile.telephone} onChange={(event) => setProfile((current) => ({ ...current, telephone: event.target.value }))} onBlur={() => setProfile((current) => ({ ...current, telephone: normalizePhone(current.telephone) }))} placeholder="+212 6 12 34 56 78" /><Input label={t('form.city')} value={profile.city} onChange={(event) => setProfile((current) => ({ ...current, city: event.target.value }))} leadingIcon={MapPin} /><Input label="Société (optionnel)" value={profile.company_name} onChange={(event) => setProfile((current) => ({ ...current, company_name: event.target.value }))} leadingIcon={Building2} /><Input label="ICE (optionnel)" value={profile.company_ice} onChange={(event) => setProfile((current) => ({ ...current, company_ice: event.target.value }))} hint="Utilisé uniquement lorsque la facturation professionnelle l’exige." /></div><div className="rounded-xl bg-stone-50 p-4"><p className="text-xs font-bold text-ink">{t('form.email')}</p><p className="mt-1 text-sm text-muted">{currentUser?.email || 'Gérée par votre fournisseur de connexion'}</p></div><Button type="submit" loading={savingProfile} loadingLabel="Enregistrement…">Enregistrer les modifications</Button></form></Card></section>;

  const sectionRenderers = {
    overview: renderOverview,
    bookings: renderBookings,
    equipment: renderEquipment,
    messages: renderMessages,
    disputes: renderDisputes,
    payments: renderPayments,
    earnings: renderEarnings,
    documents: renderDocuments,
    verification: renderVerification,
    reviews: renderReviews,
    notifications: renderNotifications,
    settings: renderSettings,
  };

  return (
    <DashboardShell
      currentUser={currentUser}
      onNavigate={onNavigate}
      onNewEquipment={onNewEquipment}
      onRefresh={() => loadDashboard({ quiet: true })}
      refreshing={refreshing}
      sections={ACCOUNT_SECTIONS}
      activeSection={activeSection}
      onSectionChange={goToSection}
      sectionCounts={sectionCounts}
    >
      {sectionRenderers[activeSection]?.()}
    </DashboardShell>
  );
}
