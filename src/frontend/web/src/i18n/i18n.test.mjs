import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import {
  cityLabel, formatDate, formatMAD, formatMoroccanAddress, formatMoroccanPhone,
  isMoroccanPhone, localeTag, normalizeMoroccanPhone,
} from './formatters.js';
import { translations, translate } from './translations.js';

test('French and Arabic dictionaries expose the same contract', () => {
  assert.deepEqual(Object.keys(translations.ar).sort(), Object.keys(translations.fr).sort());
  assert.equal(translate('ar', 'booking.submit', { price: '100 MAD' }), 'إرسال الطلب · 100 MAD');
  assert.equal(translate('fr', 'missing.key', {}, 'Texte de secours'), 'Texte de secours');
});

test('locale metadata and Moroccan formatting are locale-aware', () => {
  assert.equal(localeTag('fr'), 'fr-MA');
  assert.equal(localeTag('ar'), 'ar-MA');
  assert.match(formatMAD(1250, 'fr'), /MAD/);
  assert.match(formatMAD(1250, 'ar'), /MAD/);
  assert.notEqual(formatDate('2026-09-02', 'fr'), formatDate('2026-09-02', 'ar'));
  assert.equal(cityLabel('Casablanca', 'ar'), 'الدار البيضاء');
  assert.equal(formatMoroccanAddress({ address: 'Maarif', city: 'Casablanca' }, 'ar'), 'Maarif، الدار البيضاء');
});

test('Moroccan phone numbers are normalized, validated and displayed consistently', () => {
  assert.equal(normalizeMoroccanPhone('06 12 34 56 78'), '+212612345678');
  assert.equal(normalizeMoroccanPhone('212 5 22 33 44 55'), '+212522334455');
  assert.equal(formatMoroccanPhone('+212612345678'), '+212 6 12 34 56 78');
  assert.equal(isMoroccanPhone('06 12 34 56 78'), true);
  assert.equal(isMoroccanPhone('1234'), false);
});

test('requested web surfaces consume the shared locale layer', async () => {
  const files = [
    '../components/Navbar.jsx',
    '../components/Hero.jsx',
    '../components/CatalogueExperience.jsx',
    '../components/EquipmentModal.jsx',
    '../components/ReservationJourney.jsx',
    '../components/AccountDashboard.jsx',
    '../components/KYCVerificationModal.jsx',
    '../components/payments/PaymentStatusPanel.jsx',
    '../components/AuthModal.jsx',
    '../components/AddEquipmentModal.jsx',
  ];
  for (const file of files) {
    const source = await readFile(new URL(file, import.meta.url), 'utf8');
    assert.match(source, /useI18n/, `${file} must use the shared locale layer`);
  }
});

test('global document direction is controlled by the provider', async () => {
  const provider = await readFile(new URL('./I18nProvider.jsx', import.meta.url), 'utf8');
  const styles = await readFile(new URL('../index.css', import.meta.url), 'utf8');
  assert.match(provider, /document\.documentElement\.dir = direction/);
  assert.match(provider, /document\.documentElement\.lang = localeTag\(locale\)/);
  assert.match(styles, /html\[dir='rtl'\]/);
  assert.match(styles, /Noto Sans Arabic/);
});
