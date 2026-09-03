import { API_BASE_URL, ApiError, apiClient, isApiError } from './httpClient.js';


export { API_BASE_URL, ApiError, isApiError };

const id = (value) => encodeURIComponent(String(value));

// Retained for incremental caller compatibility. Header ownership is now in httpClient.
export function getAuthHeaders() {
  return { 'Content-Type': 'application/json' };
}


// Identity and sessions
export const createWebSession = (idToken, options) =>
  apiClient.post('/auth/session', { id_token: idToken }, options);

export const deleteWebSession = (options) =>
  apiClient.delete('/auth/session', options);

export const getCurrentUser = (options) =>
  apiClient.get('/auth/me', options);

export const updateCurrentUser = (profile, options) =>
  apiClient.patch('/auth/me', profile, options);

export const getPublicUserProfile = (userId, options) =>
  apiClient.get(`/utilisateurs/${id(userId)}/profil`, options);

export const getUserReviews = (userId, options) =>
  apiClient.get(`/utilisateurs/${id(userId)}/avis`, options);


// KYC
export const initiateDiditKYC = (options) =>
  apiClient.post('/auth/kyc/initier', {}, options);

export const getDiditKYCStatus = (userId, options) =>
  apiClient.get(`/auth/kyc/statut/${id(userId)}`, options);


// Equipment catalogue
export async function getEquipmentPage(filters = {}, options) {
  const useGeo = Number.isFinite(filters.lat) && Number.isFinite(filters.lng);
  const data = await apiClient.get(useGeo ? '/articles/recherche/geo' : '/articles', {
    ...options,
    query: {
      lat: useGeo ? filters.lat : undefined,
      lng: useGeo ? filters.lng : undefined,
      radius_km: useGeo ? filters.radius_km : undefined,
      city: filters.city && filters.city !== 'Toutes les villes' ? filters.city : undefined,
      categorie: filters.category && filters.category !== 'all' ? filters.category : undefined,
      q: filters.search || undefined,
      prix_min: filters.prix_min ?? undefined,
      prix_max: filters.prix_max ?? undefined,
      disponible: filters.available ?? true,
      verifie: filters.verified ?? false,
      limit: filters.limit,
      offset: filters.offset,
    },
  });
  const items = data?.donnees ?? data ?? [];
  return { items, total: Number.isFinite(Number(data?.total)) ? Number(data.total) : null };
}

export async function getEquipmentList(filters = {}, options) {
  const page = await getEquipmentPage(filters, options);
  return page.items;
}

export const getEquipmentCategories = (options) =>
  apiClient.get('/articles/categories', options);

export const getEquipment = (equipmentId, options) =>
  apiClient.get(`/articles/${id(equipmentId)}`, options);

export const createEquipment = (equipmentData, options) =>
  apiClient.post('/articles', {
    titre: equipmentData.titre ?? equipmentData.title,
    description: equipmentData.description,
    categorie: equipmentData.categorie ?? equipmentData.category,
    prix_par_jour: equipmentData.prix_par_jour ?? equipmentData.daily_price_mad,
    montant_caution: equipmentData.montant_caution ?? equipmentData.deposit_amount_mad,
    photos: equipmentData.photos ?? equipmentData.images_urls ?? [],
    specs: equipmentData.specs ?? equipmentData.specs_json ?? {},
    city: equipmentData.city,
    adresse_approximative: equipmentData.adresse_approximative ?? equipmentData.address,
    lat: equipmentData.lat,
    lng: equipmentData.lng,
    is_available: equipmentData.is_available ?? true,
    calendrier_disponibilite: equipmentData.calendrier_disponibilite ?? {},
  }, options);

export function uploadEquipmentPhoto(file, { onProgress, signal } = {}) {
  return new Promise((resolve, reject) => {
    const requestId = globalThis.crypto?.randomUUID?.() || `equipment-photo-${Date.now()}`;
    const xhr = new XMLHttpRequest();
    const form = new FormData();
    form.append('photo', file, file.name || 'equipment-photo.webp');
    xhr.open('POST', `${API_BASE_URL}/articles/photos`);
    xhr.timeout = 30_000;
    xhr.withCredentials = true;
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('X-Request-ID', requestId);
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress?.(Math.round((event.loaded / event.total) * 100));
    };
    xhr.onload = () => {
      let payload = null;
      try { payload = xhr.responseText ? JSON.parse(xhr.responseText) : null; } catch { payload = null; }
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(payload);
        return;
      }
      const raw = payload?.erreur ?? payload?.detail ?? payload;
      reject(new ApiError({
        status: xhr.status,
        code: raw?.code || `HTTP_${xhr.status}`,
        message: raw?.message || (typeof raw === 'string' ? raw : 'La photo n’a pas pu être importée.'),
        requestId: xhr.getResponseHeader('X-Request-ID') || requestId,
        method: 'POST',
        url: `${API_BASE_URL}/articles/photos`,
      }));
    };
    xhr.onerror = () => reject(new ApiError({
      code: 'NETWORK_ERROR', message: 'Impossible de joindre le service d’images.',
      requestId, method: 'POST', url: `${API_BASE_URL}/articles/photos`,
    }));
    xhr.ontimeout = () => reject(new ApiError({
      code: 'REQUEST_TIMEOUT', message: 'L’importation de la photo a dépassé le délai autorisé.',
      requestId, method: 'POST', url: `${API_BASE_URL}/articles/photos`,
    }));
    xhr.onabort = () => reject(new ApiError({
      code: 'REQUEST_CANCELLED', message: 'Importation annulée.',
      requestId, method: 'POST', url: `${API_BASE_URL}/articles/photos`,
    }));
    if (signal?.aborted) {
      reject(new ApiError({
        code: 'REQUEST_CANCELLED', message: 'Importation annulée.',
        requestId, method: 'POST', url: `${API_BASE_URL}/articles/photos`,
      }));
      return;
    }
    signal?.addEventListener('abort', () => xhr.abort(), { once: true });
    xhr.send(form);
  });
}

export const deleteEquipmentPhoto = (filename, options) =>
  apiClient.delete(`/articles/photos/${id(filename)}`, options);

export const getMyEquipment = (options) =>
  apiClient.get('/articles/my-listings', options);

export async function deleteEquipment(equipmentId, options) {
  await apiClient.delete(`/articles/${id(equipmentId)}`, options);
  return true;
}


// Reservations
export const calculatePricing = (articleId, startDate, endDate, options) =>
  apiClient.post('/reservations/calculer-prix', {
    article_id: articleId,
    date_debut: startDate,
    date_fin: endDate,
  }, options);

export const createBooking = (articleId, startDate, endDate, messageLoueur = '', options) =>
  apiClient.post('/reservations/creer', {
    article_id: articleId,
    date_debut: startDate,
    date_fin: endDate,
    mode_paiement: 'cash_on_delivery',
    mode_caution: 'cash',
    message_loueur: messageLoueur,
  }, options);

export async function getBookings(role = 'locataire', statut = null, options) {
  const data = await apiClient.get('/reservations', {
    ...options,
    query: { role, statut },
  });
  return data?.donnees ?? data;
}

export const performBookingAction = (bookingId, action, options) =>
  apiClient.patch(`/reservations/${id(bookingId)}/statut`, { action }, options);

export const getFinancialSummaries = (options) =>
  apiClient.get('/payments', options);

export const getBookingFinancialSummary = (bookingId, options) =>
  apiClient.get(`/payments/bookings/${id(bookingId)}`, options);

export const initiateBookingPayment = (bookingId, idempotencyKey, options = {}) =>
  apiClient.post(`/payments/bookings/${id(bookingId)}/initiate`, {}, {
    ...options,
    headers: { ...options.headers, 'Idempotency-Key': idempotencyKey },
  });


// Check-in and check-out inspections
export const getInspectionRequirements = (bookingId, inspectionType, options) =>
  apiClient.get(`/inspections/bookings/${id(bookingId)}/requirements`, {
    ...options, query: { inspection_type: inspectionType },
  });

export function uploadInspectionEvidence(bookingId, inspectionType, file, { onProgress, signal } = {}) {
  return new Promise((resolve, reject) => {
    const requestId = globalThis.crypto?.randomUUID?.() || `inspection-evidence-${Date.now()}`;
    const xhr = new XMLHttpRequest();
    const form = new FormData();
    form.append('booking_id', String(bookingId));
    form.append('inspection_type', inspectionType);
    form.append('evidence_file', file, file.name || 'inspection-evidence');
    xhr.open('POST', `${API_BASE_URL}/inspections/evidence`);
    xhr.timeout = file.type.startsWith('video/') ? 120_000 : 30_000;
    xhr.withCredentials = true;
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('X-Request-ID', requestId);
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress?.(Math.round((event.loaded / event.total) * 100));
    };
    xhr.onload = () => {
      let payload = null;
      try { payload = xhr.responseText ? JSON.parse(xhr.responseText) : null; } catch { payload = null; }
      if (xhr.status >= 200 && xhr.status < 300) return resolve(payload);
      const raw = payload?.erreur ?? payload?.detail ?? payload;
      return reject(new ApiError({
        status: xhr.status, code: raw?.code || `HTTP_${xhr.status}`,
        message: raw?.message || 'La preuve n’a pas pu être importée.',
        requestId: xhr.getResponseHeader('X-Request-ID') || requestId,
        method: 'POST', url: `${API_BASE_URL}/inspections/evidence`,
      }));
    };
    xhr.onerror = () => reject(new ApiError({ code: 'NETWORK_ERROR', message: 'Impossible de joindre le stockage des preuves.', requestId, method: 'POST', url: `${API_BASE_URL}/inspections/evidence` }));
    xhr.ontimeout = () => reject(new ApiError({ code: 'REQUEST_TIMEOUT', message: 'L’importation a dépassé le délai autorisé.', requestId, method: 'POST', url: `${API_BASE_URL}/inspections/evidence` }));
    xhr.onabort = () => reject(new ApiError({ code: 'REQUEST_CANCELLED', message: 'Importation annulée.', requestId, method: 'POST', url: `${API_BASE_URL}/inspections/evidence` }));
    if (signal?.aborted) return xhr.onabort();
    signal?.addEventListener('abort', () => xhr.abort(), { once: true });
    xhr.send(form);
  });
}

export const deleteInspectionEvidence = (evidenceId, options) =>
  apiClient.delete(`/inspections/evidence/${id(evidenceId)}`, options);

export const createInspection = (payload, idempotencyKey, options = {}) =>
  apiClient.post('/inspections', payload, {
    ...options, headers: { ...options.headers, 'Idempotency-Key': idempotencyKey },
  });

export const confirmInspection = (inspectionId, options) =>
  apiClient.post(`/inspections/${id(inspectionId)}/confirm`, {}, options);

export async function getInspections(bookingId, options) {
  return apiClient.get(`/inspections/bookings/${id(bookingId)}`, options);
}


// Disputes
export const getDisputes = (options) => apiClient.get('/disputes', options);

export const getDispute = (disputeId, options) =>
  apiClient.get(`/disputes/${id(disputeId)}`, options);

export const getDisputeContext = (disputeId, options) =>
  apiClient.get(`/disputes/${id(disputeId)}/context`, options);

export const createDispute = (payload, idempotencyKey, options = {}) =>
  apiClient.post('/disputes', payload, {
    ...options, headers: { ...options.headers, 'Idempotency-Key': idempotencyKey },
  });

export const submitDisputeForReview = (disputeId, options) =>
  apiClient.post(`/disputes/${id(disputeId)}/submit`, {}, options);

export function uploadDisputeEvidence(disputeId, file, { onProgress, signal } = {}) {
  return new Promise((resolve, reject) => {
    const requestId = globalThis.crypto?.randomUUID?.() || `dispute-evidence-${Date.now()}`;
    const xhr = new XMLHttpRequest();
    const form = new FormData();
    form.append('evidence_file', file, file.name || 'dispute-evidence');
    const url = `${API_BASE_URL}/disputes/${id(disputeId)}/evidence`;
    xhr.open('POST', url);
    xhr.timeout = file.type.startsWith('video/') ? 120_000 : 45_000;
    xhr.withCredentials = true;
    xhr.setRequestHeader('Accept', 'application/json');
    xhr.setRequestHeader('X-Request-ID', requestId);
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress?.(Math.round((event.loaded / event.total) * 100));
    };
    xhr.onload = () => {
      let payload = null;
      try { payload = xhr.responseText ? JSON.parse(xhr.responseText) : null; } catch { payload = null; }
      if (xhr.status >= 200 && xhr.status < 300) return resolve(payload);
      const raw = payload?.erreur ?? payload?.detail ?? payload;
      return reject(new ApiError({
        status: xhr.status, code: raw?.code || `HTTP_${xhr.status}`,
        message: raw?.message || 'La pièce n’a pas pu être importée.',
        requestId: xhr.getResponseHeader('X-Request-ID') || requestId,
        method: 'POST', url,
      }));
    };
    xhr.onerror = () => reject(new ApiError({ code: 'NETWORK_ERROR', message: 'Impossible de joindre le stockage des pièces.', requestId, method: 'POST', url }));
    xhr.ontimeout = () => reject(new ApiError({ code: 'REQUEST_TIMEOUT', message: 'L’importation a dépassé le délai autorisé.', requestId, method: 'POST', url }));
    xhr.onabort = () => reject(new ApiError({ code: 'REQUEST_CANCELLED', message: 'Importation annulée.', requestId, method: 'POST', url }));
    if (signal?.aborted) return xhr.onabort();
    signal?.addEventListener('abort', () => xhr.abort(), { once: true });
    xhr.send(form);
  });
}

export const deleteDisputeEvidence = (evidenceId, options) =>
  apiClient.delete(`/disputes/evidence/${id(evidenceId)}`, options);


// Contracts
export const getContract = (bookingId, options) =>
  apiClient.get(`/contrats/${id(bookingId)}`, options);

export const signContract = (bookingId, payload, options) =>
  apiClient.post(`/contrats/${id(bookingId)}/signer`, payload, options);


// Messaging and notifications
export const getUserConversations = (options) =>
  apiClient.get('/messages/conversations', options);

export const getConversationMessages = (conversationId, options) =>
  apiClient.get(`/messages/conversations/${id(conversationId)}`, options);

export const sendConversationMessage = (conversationId, contenu, options) =>
  apiClient.post(`/messages/conversations/${id(conversationId)}`, { contenu }, options);

export const sendMessage = (
  destinataireId, contenu, articleId = null, reservationId = null, options,
) => apiClient.post('/messages', {
  destinataire_id: destinataireId,
  contenu,
  article_id: articleId,
  reservation_id: reservationId,
}, options);

export const getNotifications = (state = 'all', options) =>
  apiClient.get('/notifications', { ...options, query: { state } });

export const updateNotificationRead = (notificationId, estLu, options) =>
  apiClient.patch(`/notifications/${id(notificationId)}`, { est_lu: Boolean(estLu) }, options);

export const markAllNotificationsRead = (options) =>
  apiClient.patch('/notifications/tout-lire', {}, options);


// Subscriptions and earnings
export const getSubscriptionPlans = (options) =>
  apiClient.get('/abonnements/plans', options);

export const getMySubscription = (options) =>
  apiClient.get('/abonnements/moi', options);

export const upgradeSubscription = (planName, options) =>
  apiClient.post('/abonnements/upgrade', { nouveau_plan: planName }, options);

export const getOwnerEarningsDashboard = (periode = 'mois', options) =>
  apiClient.get('/dashboard/gains', { ...options, query: { periode } });
