import assert from 'node:assert/strict';
import { afterEach, test } from 'node:test';

import { ApiError, createHttpClient } from './httpClient.js';
import { createEquipment } from './api.js';


const originalFetch = globalThis.fetch;
afterEach(() => {
  globalThis.fetch = originalFetch;
});


test('preserves backend error code and request ID without retrying POST', async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return new Response(JSON.stringify({
      statut: 'erreur',
      erreur: { code: 'KYC_REQUIRED', message: 'Verification required', details: null },
      request_id: 'server-request-id',
    }), { status: 403, headers: { 'Content-Type': 'application/json', 'X-Request-ID': 'server-request-id' } });
  };
  const client = createHttpClient({ baseUrl: 'https://api.example.test/api/v1' });
  await assert.rejects(
    client.post('/reservations/creer', { article_id: 'x' }),
    (error) => error instanceof ApiError
      && error.code === 'KYC_REQUIRED'
      && error.status === 403
      && error.requestId === 'server-request-id',
  );
  assert.equal(calls, 1);
});


test('retries a safe GET once and keeps the logical request ID', async () => {
  const requestIds = [];
  globalThis.fetch = async (_url, options) => {
    requestIds.push(options.headers.get('X-Request-ID'));
    if (requestIds.length === 1) throw new TypeError('network unavailable');
    return new Response(JSON.stringify({ donnees: [] }), { status: 200 });
  };
  const client = createHttpClient({ baseUrl: 'https://api.example.test/api/v1' });
  assert.deepEqual(await client.get('/articles'), { donnees: [] });
  assert.equal(requestIds.length, 2);
  assert.equal(requestIds[0], requestIds[1]);
});


test('centralizes JSON serialization, cookies, query values and headers', async () => {
  let captured;
  globalThis.fetch = async (url, options) => {
    captured = { url, options };
    return new Response(JSON.stringify({ ok: true }), { status: 201 });
  };
  const client = createHttpClient({ baseUrl: 'https://api.example.test/api/v1' });
  await client.post('/messages', { contenu: 'bonjour' }, { query: { page: 2, ignored: null } });
  assert.equal(captured.url, 'https://api.example.test/api/v1/messages?page=2');
  assert.equal(captured.options.credentials, 'include');
  assert.equal(captured.options.headers.get('Content-Type'), 'application/json');
  assert.equal(captured.options.headers.get('Accept'), 'application/json');
  assert.deepEqual(JSON.parse(captured.options.body), { contenu: 'bonjour' });
});


test('returns a structured timeout error', async () => {
  globalThis.fetch = async (_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(options.signal.reason), { once: true });
  });
  const client = createHttpClient({ baseUrl: 'https://api.example.test/api/v1', timeoutMs: 5 });
  await assert.rejects(
    client.get('/health', { retries: 0 }),
    (error) => error instanceof ApiError && error.code === 'REQUEST_TIMEOUT',
  );
});


test('serializes the web equipment form to the FastAPI contract', async () => {
  let payload;
  globalThis.fetch = async (_url, options) => {
    payload = JSON.parse(options.body);
    return new Response(JSON.stringify({ statut: 'succes', article_id: 'article-1' }), { status: 201 });
  };
  await createEquipment({
    title: 'Perceuse',
    description: 'Perceuse professionnelle',
    category: 'tools',
    daily_price_mad: 100,
    deposit_amount_mad: 500,
    images_urls: ['https://example.test/perceuse.jpg'],
    specs_json: { puissance: '800W' },
    city: 'Rabat',
    address: 'Agdal',
  });
  assert.deepEqual(payload, {
    titre: 'Perceuse',
    description: 'Perceuse professionnelle',
    categorie: 'tools',
    prix_par_jour: 100,
    montant_caution: 500,
    photos: ['https://example.test/perceuse.jpg'],
    specs: { puissance: '800W' },
    city: 'Rabat',
    adresse_approximative: 'Agdal',
    is_available: true,
    calendrier_disponibilite: {},
  });
});
