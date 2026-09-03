import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import {
  cityLabel, formatDate, formatDateTime, formatMAD, formatMoroccanAddress,
  formatMoroccanPhone, formatNumber, isMoroccanPhone, localeTag, normalizeMoroccanPhone,
} from './formatters';
import { SUPPORTED_LOCALES, translate } from './translations';

const STORAGE_KEY = 'lokiini.locale';
const I18nContext = createContext(null);

function getInitialLocale() {
  if (typeof window === 'undefined') return 'fr';
  const stored = window.localStorage.getItem(STORAGE_KEY);
  return SUPPORTED_LOCALES.includes(stored) ? stored : 'fr';
}

export function I18nProvider({ children }) {
  const [locale, setLocaleState] = useState(getInitialLocale);

  const setLocale = useCallback((nextLocale) => {
    if (SUPPORTED_LOCALES.includes(nextLocale)) setLocaleState(nextLocale);
  }, []);

  useEffect(() => {
    const direction = locale === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = localeTag(locale);
    document.documentElement.dir = direction;
    document.body.dir = direction;
    window.localStorage.setItem(STORAGE_KEY, locale);
  }, [locale]);

  const value = useMemo(() => ({
    locale,
    localeTag: localeTag(locale),
    direction: locale === 'ar' ? 'rtl' : 'ltr',
    isRTL: locale === 'ar',
    setLocale,
    t: (key, parameters, fallback) => translate(locale, key, parameters, fallback),
    formatMAD: (amount, options) => formatMAD(amount, locale, options),
    formatNumber: (number, options) => formatNumber(number, locale, options),
    formatDate: (date, options) => formatDate(date, locale, options),
    formatDateTime: (date, options) => formatDateTime(date, locale, options),
    formatPhone: formatMoroccanPhone,
    normalizePhone: normalizeMoroccanPhone,
    isValidPhone: isMoroccanPhone,
    cityLabel: (city) => cityLabel(city, locale),
    formatAddress: (address) => formatMoroccanAddress(address, locale),
  }), [locale, setLocale]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) throw new Error('useI18n must be used inside I18nProvider');
  return context;
}
