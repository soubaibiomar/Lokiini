import React from 'react';
import { FileCheck2, Fingerprint, ShieldCheck } from 'lucide-react';
import { Container } from './Container';
import LanguageSwitcher from '../LanguageSwitcher';
import { useI18n } from '../../i18n';

function FooterButton({ children, onClick }) {
  return <button type="button" onClick={onClick} className="min-h-11 min-w-11 text-start text-sm text-slate-300 transition-colors hover:text-white hover:underline sm:min-h-0 sm:min-w-0">{children}</button>;
}

export default function Footer({ onNavigate, onRentOut, onOpenAuth, currentUser }) {
  const { t } = useI18n();
  return (
    <footer className="border-t border-slate-800 bg-ink text-slate-300">
      <Container className="py-10 sm:py-12">
        <div className="grid gap-9 sm:grid-cols-2 lg:grid-cols-[1.35fr_1fr_1fr_1.2fr]">
          <div>
            <button type="button" onClick={() => onNavigate('catalog')} className="min-h-11 rounded-lg focus-visible:ring-2 focus-visible:ring-white/70" aria-label={t('nav.homeAria')}>
              <span className="inline-flex rounded-xl bg-white p-2">
                <img src="/logo.png" alt="Lokiini" className="h-8 w-auto object-contain" />
              </span>
            </button>
            <p className="mt-4 max-w-sm text-sm leading-6 text-slate-400">
              {t('footer.description')}
            </p>
          </div>

          <div>
            <h2 className="text-sm font-bold text-white">{t('footer.explore')}</h2>
            <div className="mt-4 flex flex-col items-start gap-3">
              <FooterButton onClick={() => onNavigate('catalog')}>{t('nav.browse')}</FooterButton>
              <FooterButton onClick={onRentOut}>{t('nav.rentOut')}</FooterButton>
              <FooterButton onClick={() => onNavigate('pricing')}>{t('nav.pricing')}</FooterButton>
            </div>
          </div>

          <div>
            <h2 className="text-sm font-bold text-white">{t('footer.account')}</h2>
            <div className="mt-4 flex flex-col items-start gap-3">
              <FooterButton onClick={currentUser ? () => onNavigate('dashboard') : onOpenAuth}>{currentUser ? t('nav.dashboard') : t('footer.signIn')}</FooterButton>
              {currentUser && <FooterButton onClick={() => onNavigate('dashboard')}>{t('footer.myRentals')}</FooterButton>}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-bold text-white">{t('footer.trust')}</h2>
            <ul className="mt-4 space-y-3 text-sm text-slate-400">
              <li className="flex items-center gap-2"><Fingerprint aria-hidden="true" className="size-4 text-emerald-400" /> {t('footer.identity')}</li>
              <li className="flex items-center gap-2"><ShieldCheck aria-hidden="true" className="size-4 text-emerald-400" /> {t('footer.payment')}</li>
              <li className="flex items-center gap-2"><FileCheck2 aria-hidden="true" className="size-4 text-emerald-400" /> {t('footer.evidence')}</li>
            </ul>
          </div>
        </div>

        <div className="mt-10 flex flex-col gap-2 border-t border-slate-700 pt-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <span>{t('footer.rights', { year: new Date().getFullYear() })}</span>
          <span>{t('footer.madeFor')}</span>
          <LanguageSwitcher inverse />
        </div>
      </Container>
    </footer>
  );
}
