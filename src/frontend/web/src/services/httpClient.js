const DEFAULT_TIMEOUT_MS = 8_000;
const RETRYABLE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS']);
const RETRYABLE_STATUSES = new Set([408, 429, 502, 503, 504]);

const STATUS_CODES = {
  400: 'BAD_REQUEST',
  401: 'AUTH_REQUIRED',
  403: 'FORBIDDEN',
  404: 'NOT_FOUND',
  408: 'REQUEST_TIMEOUT',
  409: 'CONFLICT',
  422: 'VALIDATION_ERROR',
  429: 'RATE_LIMITED',
  500: 'INTERNAL_ERROR',
  502: 'BAD_GATEWAY',
  503: 'SERVICE_UNAVAILABLE',
  504: 'GATEWAY_TIMEOUT',
};


function resolveBaseUrl() {
  const configured = import.meta.env?.VITE_API_URL?.trim();
  if (configured) return configured.replace(/\/+$/, '');
  if (typeof window !== 'undefined') return `${window.location.origin}/api/v1`;
  return '/api/v1';
}


function createRequestId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  return `web-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}


function appendQuery(path, query) {
  if (!query) return path;
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (Array.isArray(value)) value.forEach((item) => params.append(key, String(item)));
    else params.set(key, String(value));
  });
  const serialized = params.toString();
  if (!serialized) return path;
  return `${path}${path.includes('?') ? '&' : '?'}${serialized}`;
}


function abortContext(externalSignal, timeoutMs) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(new DOMException('Request timed out', 'TimeoutError')), timeoutMs);
  const forwardAbort = () => controller.abort(externalSignal.reason);
  if (externalSignal?.aborted) forwardAbort();
  else externalSignal?.addEventListener('abort', forwardAbort, { once: true });
  return {
    signal: controller.signal,
    cleanup() {
      clearTimeout(timeout);
      externalSignal?.removeEventListener('abort', forwardAbort);
    },
  };
}


async function parsePayload(response) {
  if (response.status === 204) return null;
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}


function errorFields(payload, status) {
  const raw = payload?.erreur ?? payload?.detail ?? payload;
  if (typeof raw === 'string') {
    return { code: STATUS_CODES[status] || `HTTP_${status}`, message: raw, details: null };
  }
  return {
    code: raw?.code || STATUS_CODES[status] || `HTTP_${status}`,
    message: raw?.message || payload?.message || `La requête API a échoué (${status}).`,
    details: raw?.details ?? null,
  };
}


export class ApiError extends Error {
  constructor({ code, message, status = 0, details = null, requestId, method, url, cause }) {
    super(message, cause ? { cause } : undefined);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.details = details;
    this.requestId = requestId;
    this.method = method;
    this.url = url;
    this.retryable = status === 0 || RETRYABLE_STATUSES.has(status);
  }
}


export function isApiError(error) {
  return error instanceof ApiError;
}


export function createHttpClient({
  baseUrl = resolveBaseUrl(),
  credentials = 'include',
  timeoutMs = DEFAULT_TIMEOUT_MS,
  getAuthHeaders,
} = {}) {
  const normalizedBaseUrl = baseUrl.replace(/\/+$/, '');

  async function request(path, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const url = `${normalizedBaseUrl}${appendQuery(path, options.query)}`;
    const requestId = options.requestId || createRequestId();
    const safeRetries = RETRYABLE_METHODS.has(method) ? (options.retries ?? 1) : 0;

    for (let attempt = 0; ; attempt += 1) {
      const context = abortContext(options.signal, options.timeoutMs ?? timeoutMs);
      const authHeaders = getAuthHeaders ? await getAuthHeaders() : {};
      const headers = new Headers({
        Accept: 'application/json',
        'X-Request-ID': requestId,
        ...authHeaders,
        ...options.headers,
      });
      let body = options.body;
      const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;
      if (body !== undefined && body !== null && !isFormData && typeof body !== 'string') {
        headers.set('Content-Type', 'application/json');
        body = JSON.stringify(body);
      }

      try {
        const response = await fetch(url, {
          method,
          headers,
          body,
          credentials: options.credentials ?? credentials,
          signal: context.signal,
        });
        const payload = await parsePayload(response);
        if (response.ok) return payload;

        const fields = errorFields(payload, response.status);
        const error = new ApiError({
          ...fields,
          status: response.status,
          requestId: response.headers.get('X-Request-ID') || payload?.request_id || requestId,
          method,
          url,
        });
        if (attempt < safeRetries && error.retryable) continue;
        throw error;
      } catch (error) {
        if (error instanceof ApiError) throw error;
        const cancelled = Boolean(options.signal?.aborted);
        const apiError = new ApiError({
          code: cancelled ? 'REQUEST_CANCELLED' : context.signal.aborted ? 'REQUEST_TIMEOUT' : 'NETWORK_ERROR',
          message: cancelled
            ? 'La requête a été annulée.'
            : context.signal.aborted
              ? 'Le serveur a dépassé le délai de réponse.'
              : 'Impossible de joindre le serveur.',
          requestId,
          method,
          url,
          cause: error,
        });
        if (attempt < safeRetries && !cancelled) continue;
        throw apiError;
      } finally {
        context.cleanup();
      }
    }
  }

  return {
    baseUrl: normalizedBaseUrl,
    request,
    get: (path, options) => request(path, { ...options, method: 'GET' }),
    post: (path, body, options) => request(path, { ...options, method: 'POST', body }),
    put: (path, body, options) => request(path, { ...options, method: 'PUT', body }),
    patch: (path, body, options) => request(path, { ...options, method: 'PATCH', body }),
    delete: (path, options) => request(path, { ...options, method: 'DELETE' }),
  };
}


export const apiClient = createHttpClient();
export const API_BASE_URL = apiClient.baseUrl;
