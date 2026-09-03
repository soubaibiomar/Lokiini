import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

const requestedComponents = [
  'Button', 'Input', 'Textarea', 'Select', 'Checkbox', 'Radio', 'Switch',
  'Badge', 'Avatar', 'Card', 'Modal', 'Drawer', 'Tabs', 'Dropdown', 'Tooltip',
  'ToastProvider', 'Skeleton', 'EmptyState', 'ErrorState', 'Stepper', 'Breadcrumb',
  'PriceDisplay', 'EquipmentCard', 'Rating', 'TrustBadge',
];

test('the shared entry point exports every design-system component', async () => {
  const entry = await readFile(new URL('./index.js', import.meta.url), 'utf8');
  for (const component of requestedComponents) {
    assert.match(entry, new RegExp(`\\b${component}\\b`), `${component} must be exported`);
  }
});

test('the design system defines all required semantic state tokens', async () => {
  const styles = await readFile(new URL('../../index.css', import.meta.url), 'utf8');
  for (const token of ['primary', 'action', 'success', 'warning', 'error', 'info', 'border', 'canvas', 'surface', 'ink']) {
    assert.match(styles, new RegExp(`--color-${token}:`), `--color-${token} must be defined`);
  }
  assert.match(styles, /:focus-visible/);
  assert.match(styles, /prefers-reduced-motion/);
});

test('shared controls expose keyboard and screen-reader behavior', async () => {
  const [forms, overlays, navigation, marketplace, surfaces] = await Promise.all([
    readFile(new URL('./FormControls.jsx', import.meta.url), 'utf8'),
    readFile(new URL('./Overlays.jsx', import.meta.url), 'utf8'),
    readFile(new URL('./Navigation.jsx', import.meta.url), 'utf8'),
    readFile(new URL('./Marketplace.jsx', import.meta.url), 'utf8'),
    readFile(new URL('./Surfaces.jsx', import.meta.url), 'utf8'),
  ]);
  assert.match(forms, /aria-errormessage/);
  assert.match(forms, /aria-labelledby=\{labelId\}/);
  assert.match(overlays, /event\.key === 'Escape'/);
  assert.match(overlays, /event\.key !== 'Tab'/);
  assert.match(overlays, /ArrowDown/);
  assert.match(navigation, /aria-orientation="horizontal"/);
  assert.match(navigation, /tabIndex=\{selected === item\.value \? 0 : -1\}/);
  assert.match(marketplace, /aria-label=\{`\$\{t\('equipment\.details'\)\}/);
  assert.match(surfaces, /role=\{name \? 'img'/);
  assert.match(surfaces, /role="img"/);
});

test('single-choice language and billing controls use keyboard-operable radio semantics', async () => {
  const [languageSwitcher, pricing] = await Promise.all([
    readFile(new URL('../LanguageSwitcher.jsx', import.meta.url), 'utf8'),
    readFile(new URL('../PricingSection.jsx', import.meta.url), 'utf8'),
  ]);
  for (const source of [languageSwitcher, pricing]) {
    assert.match(source, /role="radiogroup"/);
    assert.match(source, /role="radio"/);
    assert.match(source, /aria-checked/);
    assert.match(source, /ArrowRight/);
    assert.match(source, /tabIndex=/);
  }
});
