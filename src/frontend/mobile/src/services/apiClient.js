import { auth } from './auth';

const API_BASE = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000/api/v1';

export class ApiError extends Error {
  constructor(message, status, code = null, details = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function getAuthToken() {
  const user = auth?.currentUser;
  if (!user) return null;
  try {
    return await user.getIdToken();
  } catch {
    return null;
  }
}

function buildUrl(endpoint, query = {}) {
  const url = endpoint.startsWith('http') ? new URL(endpoint) : new URL(`${API_BASE.replace(/\/+$/, '')}/${endpoint.replace(/^\/+/, '')}`);
  Object.entries(query).forEach(([key, val]) => {
    if (val !== undefined && val !== null && val !== '') {
      url.searchParams.append(key, String(val));
    }
  });
  return url.toString();
}

async function request(endpoint, options = {}) {
  const {
    method = 'GET',
    query = {},
    body = null,
    headers = {},
    isMultipart = false,
  } = options;

  const token = await getAuthToken();
  const requestHeaders = {
    Accept: 'application/json',
    ...headers,
  };

  if (token) {
    requestHeaders.Authorization = `Bearer ${token}`;
  }

  let requestBody = body;
  if (body && !isMultipart && typeof body === 'object') {
    requestHeaders['Content-Type'] = 'application/json';
    requestBody = JSON.stringify(body);
  }

  const url = buildUrl(endpoint, query);
  let response;
  try {
    response = await fetch(url, {
      method,
      headers: requestHeaders,
      body: requestBody,
    });
  } catch (netErr) {
    throw new ApiError(
      'Impossible de contacter le serveur. Vérifiez votre connexion.',
      0,
      'NETWORK_ERROR',
      netErr.message,
    );
  }

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json().catch(() => null)
    : await response.text().catch(() => null);

  if (!response.ok) {
    const errorPayload = data?.erreur || data?.detail || {};
    const message = typeof errorPayload === 'string'
      ? errorPayload
      : errorPayload?.message || data?.message || `Erreur serveur (${response.status})`;
    const code = errorPayload?.code || data?.code || `HTTP_${response.status}`;
    throw new ApiError(message, response.status, code, errorPayload?.details || null);
  }

  return data;
}

export const apiClient = {
  get: (endpoint, query = {}, options = {}) => request(endpoint, { ...options, method: 'GET', query }),
  post: (endpoint, body = null, options = {}) => request(endpoint, { ...options, method: 'POST', body }),
  put: (endpoint, body = null, options = {}) => request(endpoint, { ...options, method: 'PUT', body }),
  patch: (endpoint, body = null, options = {}) => request(endpoint, { ...options, method: 'PATCH', body }),
  delete: (endpoint, options = {}) => request(endpoint, { ...options, method: 'DELETE' }),
  upload: (endpoint, formData, options = {}) => request(endpoint, { ...options, method: 'POST', body: formData, isMultipart: true }),
};
