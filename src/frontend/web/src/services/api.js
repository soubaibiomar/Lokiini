// Flexible base URL resolution for Docker Gateway, Vite dev server, and local FastAPI
const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  if (typeof window !== 'undefined') {
    if (window.location.port === '' || window.location.port === '80') {
      return `${window.location.origin}/api/v1`;
    }
  }
  return 'http://localhost:8001/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

// Auth token helper
function getAuthHeaders() {
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('lokiini_token') : null;
  const headers = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Fetch equipment catalogue from FastAPI backend with filters
 */
export async function getEquipmentList(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.city && filters.city !== 'Toutes les villes') params.append('city', filters.city);
    if (filters.category && filters.category !== 'all') params.append('category', filters.category);
    if (filters.search) params.append('search', filters.search);
    if (filters.max_price) params.append('max_price', filters.max_price);

    const response = await fetch(`${API_BASE_URL}/equipment?${params.toString()}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn('API Backend unreachable, falling back to local dataset:', error);
    return null;
  }
}

/**
 * Fetch single equipment by ID
 */
export async function getEquipment(equipmentId) {
  try {
    const response = await fetch(`${API_BASE_URL}/equipment/${equipmentId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching equipment from API:', error);
    return null;
  }
}

/**
 * Create a new equipment listing (Pro Loueur)
 */
export async function createEquipment(equipmentData) {
  try {
    const response = await fetch(`${API_BASE_URL}/equipment`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(equipmentData)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error creating equipment via API:', error);
    return null;
  }
}

/**
 * Delete an equipment listing
 */
export async function deleteEquipment(equipmentId) {
  try {
    const response = await fetch(`${API_BASE_URL}/equipment/${equipmentId}`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    return response.ok;
  } catch (error) {
    console.error('Error deleting equipment via API:', error);
    return false;
  }
}

/**
 * Calculate dynamic degressive pricing and CMI caution hold
 */
export async function calculatePricing(equipmentId, startDate, endDate) {
  try {
    const response = await fetch(`${API_BASE_URL}/bookings/calculate-pricing`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        equipment_id: equipmentId,
        start_date: startDate,
        end_date: endDate
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error calculating pricing from API:', error);
    return null;
  }
}

/**
 * Create confirmed booking and generate CMI caution token
 */
export async function createBooking(equipmentId, startDate, endDate, renterId = null) {
  try {
    const payload = {
      equipment_id: equipmentId,
      start_date: startDate,
      end_date: endDate,
      payment_method: 'cmi_card'
    };
    if (renterId) payload.renter_id = renterId;

    const response = await fetch(`${API_BASE_URL}/bookings/create`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error creating booking via API:', error);
    return null;
  }
}

/**
 * Fetch list of bookings (for Owner Dashboard and Renter Tracking)
 */
export async function getBookings(filters = {}) {
  try {
    const params = new URLSearchParams();
    if (filters.status) params.append('status_filter', filters.status);
    if (filters.owner_id) params.append('owner_id', filters.owner_id);
    if (filters.renter_id) params.append('renter_id', filters.renter_id);

    const response = await fetch(`${API_BASE_URL}/bookings?${params.toString()}`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.warn('Error fetching bookings from API:', error);
    return null;
  }
}

/**
 * Update booking status and CMI escrow (e.g. check-in, release caution, capture)
 */
export async function updateBookingStatus(bookingId, bookingStatus, cmiStatus = null) {
  try {
    const payload = {};
    if (bookingStatus) payload.booking_status = bookingStatus;
    if (cmiStatus) payload.cmi_status = cmiStatus;

    const response = await fetch(`${API_BASE_URL}/bookings/${bookingId}/status`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error updating booking status via API:', error);
    return null;
  }
}

/**
 * Fetch signed DOC rental contract
 */
export async function getContract(bookingId) {
  try {
    const response = await fetch(`${API_BASE_URL}/contracts/${bookingId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching contract from API:', error);
    return null;
  }
}

/**
 * Seal an inspection report with SHA-256 hash
 */
export async function sealInspection(bookingId, type, videoUrl, notes = '') {
  try {
    const response = await fetch(`${API_BASE_URL}/inspections/seal`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        booking_id: bookingId,
        type: type,
        video_url: videoUrl,
        notes: notes
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error sealing inspection via API:', error);
    return null;
  }
}

/**
 * Get inspection reports for a booking
 */
export async function getInspections(bookingId) {
  try {
    const response = await fetch(`${API_BASE_URL}/inspections/booking/${bookingId}`);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error fetching inspections via API:', error);
    return [];
  }
}

/**
 * Submit KYC verification with CNDP Zero-Knowledge audit
 */
export async function verifyKYC(cinNumber) {
  try {
    const response = await fetch(`${API_BASE_URL}/kyc/verify`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        cin_number: cinNumber
      })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error verifying KYC via API:', error);
    return null;
  }
}

/**
 * User login
 */
export async function loginUser(email, password) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const data = await response.json();
    if (data.access_token) {
      localStorage.setItem('lokiini_token', data.access_token);
      localStorage.setItem('lokiini_user', JSON.stringify(data.user));
    }
    return data;
  } catch (error) {
    console.error('Error logging in:', error);
    return null;
  }
}

/**
 * User registration
 */
export async function registerUser(userData) {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Error registering:', error);
    return null;
  }
}

/**
 * Get current user profile
 */
export async function getCurrentUser() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: getAuthHeaders()
    });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    return await response.json();
  } catch (error) {
    return null;
  }
}
