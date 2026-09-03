export const LOCALE_TAGS = Object.freeze({ fr: 'fr-MA', ar: 'ar-MA' });

const CITY_LABELS = Object.freeze({
  Casablanca: { fr: 'Casablanca', ar: 'الدار البيضاء' },
  Rabat: { fr: 'Rabat', ar: 'الرباط' },
  Marrakech: { fr: 'Marrakech', ar: 'مراكش' },
  Tanger: { fr: 'Tanger', ar: 'طنجة' },
  Fès: { fr: 'Fès', ar: 'فاس' },
  Fes: { fr: 'Fès', ar: 'فاس' },
  Agadir: { fr: 'Agadir', ar: 'أكادير' },
  Oujda: { fr: 'Oujda', ar: 'وجدة' },
  Meknès: { fr: 'Meknès', ar: 'مكناس' },
  Meknes: { fr: 'Meknès', ar: 'مكناس' },
  Kénitra: { fr: 'Kénitra', ar: 'القنيطرة' },
  Kenitra: { fr: 'Kénitra', ar: 'القنيطرة' },
  'El Jadida': { fr: 'El Jadida', ar: 'الجديدة' },
  Tétouan: { fr: 'Tétouan', ar: 'تطوان' },
  Tetouan: { fr: 'Tétouan', ar: 'تطوان' },
});

export function localeTag(locale = 'fr') {
  return LOCALE_TAGS[locale] || LOCALE_TAGS.fr;
}

export function formatMAD(value, locale = 'fr', options = {}) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return '';
  return new Intl.NumberFormat(localeTag(locale), {
    style: 'currency',
    currency: 'MAD',
    currencyDisplay: 'code',
    minimumFractionDigits: Number.isInteger(amount) ? 0 : 2,
    maximumFractionDigits: 2,
    ...options,
  }).format(amount);
}

export function formatNumber(value, locale = 'fr', options = {}) {
  const number = Number(value);
  if (!Number.isFinite(number)) return '';
  return new Intl.NumberFormat(localeTag(locale), options).format(number);
}

function toDate(value) {
  if (value instanceof Date) return Number.isNaN(value.getTime()) ? null : value;
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    const [year, month, day] = value.split('-').map(Number);
    const localDate = new Date(year, month - 1, day, 12);
    return Number.isNaN(localDate.getTime()) ? null : localDate;
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(value, locale = 'fr', options = {}) {
  const date = toDate(value);
  if (!date) return '';
  return new Intl.DateTimeFormat(localeTag(locale), {
    day: 'numeric', month: 'long', year: 'numeric', ...options,
  }).format(date);
}

export function formatDateTime(value, locale = 'fr', options = {}) {
  const date = toDate(value);
  if (!date) return '';
  return new Intl.DateTimeFormat(localeTag(locale), {
    day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', ...options,
  }).format(date);
}

export function normalizeMoroccanPhone(value) {
  const compact = String(value || '').trim().replace(/[^\d+]/g, '');
  if (!compact) return '';
  const digits = compact.replace(/\D/g, '');
  if (/^0[5-8]\d{8}$/.test(digits)) return `+212${digits.slice(1)}`;
  if (/^212[5-8]\d{8}$/.test(digits)) return `+${digits}`;
  if (/^[5-8]\d{8}$/.test(digits)) return `+212${digits}`;
  return compact.startsWith('+') ? `+${digits}` : digits;
}

export function isMoroccanPhone(value) {
  return /^\+212[5-8]\d{8}$/.test(normalizeMoroccanPhone(value));
}

export function formatMoroccanPhone(value) {
  const normalized = normalizeMoroccanPhone(value);
  const match = normalized.match(/^\+212([5-8])(\d{2})(\d{2})(\d{2})(\d{2})$/);
  return match ? `+212 ${match[1]} ${match[2]} ${match[3]} ${match[4]} ${match[5]}` : normalized;
}

export function cityLabel(city, locale = 'fr') {
  if (!city) return '';
  return CITY_LABELS[city]?.[locale] || CITY_LABELS[city]?.fr || city;
}

export function formatMoroccanAddress({ address, city } = {}, locale = 'fr') {
  return [address, cityLabel(city, locale)].filter(Boolean).join(locale === 'ar' ? '، ' : ', ');
}

export const MOROCCAN_CITIES = Object.freeze(
  [...new Set(Object.keys(CITY_LABELS).filter((city) => !['Fes', 'Meknes', 'Kenitra', 'Tetouan'].includes(city)))],
);
