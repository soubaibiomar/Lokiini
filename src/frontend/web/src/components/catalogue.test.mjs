import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const read = (path) => readFile(new URL(path, import.meta.url), 'utf8');

test('catalogue exposes only backend-supported filters', async () => {
  const source = await read('./CatalogueExperience.jsx');
  for (const supported of ['catalogue.category', 'catalogue.city', 'catalogue.price', 'catalogue.available', 'catalogue.verified', 'catalogue.nearMe']) {
    assert.match(source, new RegExp(supported));
  }
  for (const unsupported of ['Sous-catégorie', 'Note minimum', 'Livraison incluse', 'Date de début']) {
    assert.doesNotMatch(source, new RegExp(unsupported));
  }
});

test('catalogue state is shareable without exposing precise coordinates', async () => {
  const app = await read('../App.jsx');
  for (const parameter of ['q', 'category', 'city', 'min_price', 'max_price', 'verified', 'available', 'radius']) {
    assert.match(app, new RegExp(`params\\.set\\('${parameter}'`));
  }
  assert.doesNotMatch(app, /params\.set\('(lat|lng)'/);
});

test('catalogue includes real pagination and explicit result states', async () => {
  const [app, grid] = await Promise.all([read('../App.jsx'), read('./EquipmentGrid.jsx')]);
  assert.match(app, /getEquipmentPage/);
  assert.match(app, /offset: equipmentList\.length/);
  assert.match(grid, /catalogue\.loadError/);
  assert.match(grid, /catalogue\.noResults/);
  assert.match(grid, /catalogue\.loadMore/);
  assert.match(app, /Le catalogue est temporairement indisponible/);
});

test('catalogue contains no runtime listing mock fallback', async () => {
  const source = (await Promise.all([
    read('../App.jsx'),
    read('./CatalogueExperience.jsx'),
    read('./EquipmentGrid.jsx'),
    read('../services/api.js'),
  ])).join('\n');
  assert.doesNotMatch(source, /mockEquipment|fallbackListings|demoListings|mock catalogue/i);
});
