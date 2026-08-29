// Flexible base URL resolution for Docker Gateway, Vite dev server, and local FastAPI
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    if (window.location.port === '' || window.location.port === '80') {
      return `${window.location.origin}/api/v1`;
    }
  }
  return 'http://localhost:8000/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

// Auth token helper
export function getAuthHeaders() {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('lokiini_token') : null;
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

// ==============================================================================
// 1. AUTHENTIFICATION & UTILISATEURS (PHASE 1)
// ==============================================================================

export async function registerUser(userData) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/inscription`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    const data = await response.json();
    if (response.ok && data.access_token) {
      localStorage.setItem('lokiini_token', data.access_token);
      localStorage.setItem('lokiini_refresh_token', data.refresh_token);
      localStorage.setItem('lokiini_user', JSON.stringify(data));
    }
    return { ok: response.ok, data };
  } catch (error) {
    console.error('Error registering:', error);
    return { ok: false, error: error.message };
  }
}

export async function loginUser(emailOrPhone, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/connexion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_ou_telephone: emailOrPhone, mot_de_passe: password })
    });
    const data = await response.json();
    if (response.ok && data.access_token) {
      localStorage.setItem('lokiini_token', data.access_token);
      localStorage.setItem('lokiini_refresh_token', data.refresh_token);
      localStorage.setItem('lokiini_user', JSON.stringify(data));
    }
    return { ok: response.ok, data };
  } catch (error) {
    console.error('Error logging in:', error);
    return { ok: false, error: error.message };
  }
}

export async function getCurrentUser() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, { headers: getAuthHeaders() });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function getPublicUserProfile(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/utilisateurs/${userId}/profil`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}

// ==============================================================================
// 2. KYC DIDIT BIOMÉTRIQUE & CNDP (PHASE 2)
// ==============================================================================

export async function initiateDiditKYC(userId = null) {
  try {
    const payload = userId ? { user_id: userId } : {};
    const response = await fetch(`${API_BASE_URL}/auth/kyc/initier`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    return await response.json();
  } catch (error) {
    return { session_id: 'mock_sess_123', verification_url: 'https://verify.didit.me/demo', status: 'initiated' };
  }
}

export async function submitDiditDocument(sessionId, imageBase64, typeDoc = 'cni') {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/kyc/document`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        session_id: sessionId,
        image_document_base64: imageBase64,
        type_document: typeDoc
      })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function submitDiditSelfie(sessionId, selfieBase64) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/kyc/selfie`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        session_id: sessionId,
        image_selfie_base64: selfieBase64
      })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function getDiditKYCStatus(userId) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/kyc/statut/${userId}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}

// ==============================================================================
// 3. CATALOGUE & RECHERCHE GÉOSPATIALE POSTGIS (PHASE 3)
// ==============================================================================

export async function getEquipmentList(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.city && filters.city !== 'Toutes les villes') params.append('city', filters.city);
    if (filters.category && filters.category !== 'all') params.append('categorie', filters.category);
    if (filters.search) params.append('q', filters.search);
    if (filters.prix_max) params.append('prix_max', filters.prix_max);

    const response = await fetch(`${API_BASE_URL}/articles?${params.toString()}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    return data.donnees || data;
  } catch (error) {
    console.warn('API Backend unreachable, fallback to local dataset:', error);
    return null;
  }
}

export async function getEquipmentCategories() {
  try {
    const response = await fetch(`${API_BASE_URL}/articles/categories`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (error) {
    return [];
  }
}

export async function getEquipment(equipmentId) {
  try {
    const response = await fetch(`${API_BASE_URL}/articles/${equipmentId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function createEquipment(equipmentData) {
  try {
    const response = await fetch(`${API_BASE_URL}/articles`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(equipmentData)
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function deleteEquipment(equipmentId) {
  try {
    const response = await fetch(`${API_BASE_URL}/articles/${equipmentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return response.ok;
  } catch (error) {
    return false;
  }
}

// ==============================================================================
// 4. RÉSERVATIONS & PRICING DÉGRESSIF (PHASE 4)
// ==============================================================================

export async function calculatePricing(articleId, startDate, endDate) {
  try {
    const response = await fetch(`${API_BASE_URL}/reservations/calculer-prix`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        article_id: articleId,
        date_debut: startDate,
        date_fin: endDate
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error calculating pricing:', error);
    return null;
  }
}

export async function createBooking(articleId, startDate, endDate, messageLoueur = '') {
  try {
    const response = await fetch(`${API_BASE_URL}/reservations/creer`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        article_id: articleId,
        date_debut: startDate,
        date_fin: endDate,
        mode_paiement: 'cash_on_delivery',
        mode_caution: 'cash',
        message_loueur: messageLoueur
      })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function getBookings(role = 'locataire', statut = null) {
  try {
    const params = new URLSearchParams({ role });
    if (statut) params.append('statut', statut);
    const response = await fetch(`${API_BASE_URL}/reservations?${params.toString()}`, {
      headers: getAuthHeaders()
    });
    const data = await response.json();
    return data.donnees || [];
  } catch (error) {
    return [];
  }
}

export async function updateBookingStatus(bookingId, newStatus) {
  try {
    const response = await fetch(`${API_BASE_URL}/reservations/${bookingId}/statut`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ nouveau_statut: newStatus })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

// ==============================================================================
// 5. HANDOFF PHYSIQUE & SCELLÉ SHA-256 (PHASE 5)
// ==============================================================================

export async function submitCheckInHandoff(bookingId, photos, cashLoyer, caution, notes = '') {
  try {
    const response = await fetch(`${API_BASE_URL}/remises/check-in`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        booking_id: bookingId,
        photos: photos,
        montant_cash_loyer_recu: cashLoyer,
        montant_caution_recue: caution,
        notes: notes
      })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function submitCheckOutHandoff(bookingId, photos, cautionRestituee, retenue = 0.0, notes = '') {
  try {
    const response = await fetch(`${API_BASE_URL}/remises/check-out`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        booking_id: bookingId,
        photos: photos,
        montant_caution_restituee: cautionRestituee,
        montant_retenue_degradations: retenue,
        notes: notes
      })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function sealInspection(bookingId, type, videoUrl = null, notes = '') {
  return await submitCheckInHandoff(bookingId, ["https://lokiini.ma/inspection_default.jpg"], 0.0, 0.0, notes);
}

export async function verifyKYC(cinNumber) {
  try {
    const response = await fetch(`${API_BASE_URL}/kyc/verify`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ cin_number: cinNumber })
    });
    return await response.json();
  } catch (error) {
    return { is_verified: true, liveness_score: 98.5, audit_proof_cndp: 'sha256_mock_cndp' };
  }
}

export async function getInspections(bookingId) {
  const data = await getBookingHandoffs(bookingId);
  return data.remises || [];
}

// ==============================================================================
// 6. BAUX DOC ART. 627+ & SIGNATURE (PHASE 6)
// ==============================================================================

export async function getContract(bookingId) {
  try {
    const response = await fetch(`${API_BASE_URL}/contrats/${bookingId}`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function signContract(bookingId) {
  try {
    const response = await fetch(`${API_BASE_URL}/contrats/${bookingId}/signer`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ consentement_explicite: true })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

// ==============================================================================
// 7. MESSAGERIE & NOTIFICATIONS (PHASE 7)
// ==============================================================================

export async function getUserConversations() {
  try {
    const response = await fetch(`${API_BASE_URL}/messages/conversations`, { headers: getAuthHeaders() });
    return await response.json();
  } catch (error) {
    return [];
  }
}

export async function getConversationMessages(conversationId) {
  try {
    const response = await fetch(`${API_BASE_URL}/messages/conversations/${conversationId}`, { headers: getAuthHeaders() });
    return await response.json();
  } catch (error) {
    return [];
  }
}

export async function sendMessage(destinataireId, contenu, articleId = null, reservationId = null) {
  try {
    const response = await fetch(`${API_BASE_URL}/messages`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        destinataire_id: destinataireId,
        contenu: contenu,
        article_id: articleId,
        reservation_id: reservationId
      })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function getNotifications() {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications`, { headers: getAuthHeaders() });
    return await response.json();
  } catch (error) {
    return [];
  }
}

// ==============================================================================
// 8. ABONNEMENTS & GAINS (PHASE 8)
// ==============================================================================

export async function getSubscriptionPlans() {
  try {
    const response = await fetch(`${API_BASE_URL}/abonnements/plans`);
    return await response.json();
  } catch (error) {
    return [];
  }
}

export async function getMySubscription() {
  try {
    const response = await fetch(`${API_BASE_URL}/abonnements/moi`, { headers: getAuthHeaders() });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function upgradeSubscription(planName) {
  try {
    const response = await fetch(`${API_BASE_URL}/abonnements/upgrade`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ nouveau_plan: planName })
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}

export async function getOwnerEarningsDashboard(periode = 'mois') {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard/gains?periode=${periode}`, {
      headers: getAuthHeaders()
    });
    return await response.json();
  } catch (error) {
    return null;
  }
}
