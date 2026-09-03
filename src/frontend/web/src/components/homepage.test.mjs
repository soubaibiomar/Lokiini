import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('homepage source contains no fabricated social proof or stock catalogue fallback', async () => {
  const files = await Promise.all([
    read('../App.jsx'),
    read('./Hero.jsx'),
    read('./GeoCitiesSection.jsx'),
    read('./EquipmentGrid.jsx'),
    read('./EquipmentModal.jsx'),
    read('../../index.html'),
  ]);
  const source = files.join('\n');
  for (const forbidden of ['N°1', '4.95', '34 avis', '540+ matériels', 'images.unsplash.com', 'Atlas Location BTP Maroc']) {
    const escaped = forbidden.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    assert.doesNotMatch(source, new RegExp(escaped, 'i'));
  }
});

test('homepage facets are derived from the FastAPI equipment response', async () => {
  const app = await read('../App.jsx');
  assert.match(app, /getEquipmentCategories/);
  assert.match(app, /mapped\.map\(\(item\) => item\.city\)/);
  assert.match(app, /item\.loueur_statut_kyc === 'verified'/);
});

test('structured homepage metadata remains valid JSON', async () => {
  const html = await read('../../index.html');
  const match = html.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/);
  assert.ok(match, 'JSON-LD block must exist');
  assert.doesNotThrow(() => JSON.parse(match[1]));
});
