import React, { useRef, useState } from 'react';
import { 
  X, 
  User, 
  Lock, 
  Mail, 
  Phone, 
  Building2, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  ArrowLeft,
  KeyRound,
  Sparkles
} from 'lucide-react';
import { 
  loginWithEmailPassword, 
  registerWithEmailPassword, 
  loginWithGoogle, 
  resetPassword,
  isFirebaseConfigured
} from '../services/firebase';
import { MOROCCAN_CITIES } from '../data/mockData';
import { useI18n } from '../i18n';
import { useDialogLayer } from './ui';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const { t, cityLabel, normalizePhone, isValidPhone } = useI18n();
  // Modes: 'login' | 'register' | 'forgot_password'
  const [authMode, setAuthMode] = useState('login');
  const [role, setRole] = useState('renter'); // 'renter' | 'pro_owner'
  
  // Form fields
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [city, setCity] = useState('Casablanca');
  const [companyName, setCompanyName] = useState('');
  const [companyIce, setCompanyIce] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGoogleSubmitting, setIsGoogleSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);
  const panelRef = useRef(null);
  useDialogLayer(isOpen, onClose, panelRef);

  const handleRoleKeyDown = (event) => {
    const roles = ['renter', 'pro_owner'];
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const nextIndex = event.key === 'ArrowLeft' || event.key === 'ArrowUp' || event.key === 'Home' ? 0 : roles.length - 1;
    setRole(roles[nextIndex]);
    event.currentTarget.parentElement?.querySelectorAll('[role="radio"]')[nextIndex]?.focus();
  };

  if (!isOpen) return null;

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      if (authMode === 'login') {
        const res = await loginWithEmailPassword(email, password);
        if (res.ok && res.user) {
          setSuccessMsg(t('auth.loginSuccess'));
          setTimeout(() => {
            onAuthSuccess(res.user);
            onClose();
          }, 600);
        } else {
          setErrorMsg(res.error || t('auth.loginFailed'));
        }
      } else if (authMode === 'register') {
        if (!isValidPhone(phoneNumber)) {
          setErrorMsg(t('auth.phoneInvalid'));
          return;
        }
        const res = await registerWithEmailPassword({
          email,
          password,
          fullName,
          phoneNumber: normalizePhone(phoneNumber),
          city,
          role,
          companyName: role === 'pro_owner' ? companyName : null,
          companyIce: role === 'pro_owner' ? companyIce : null
        });

        if (res.ok && res.user) {
          setSuccessMsg(t('auth.registerSuccess'));
          setTimeout(() => {
            onAuthSuccess(res.user);
            onClose();
          }, 600);
        } else {
          setErrorMsg(res.error || t('auth.registerFailed'));
        }
      } else if (authMode === 'forgot_password') {
        const res = await resetPassword(email);
        if (res.ok) {
          setSuccessMsg(res.message || "Lien de réinitialisation envoyé par e-mail.");
        } else {
          setErrorMsg(res.error || "Erreur lors de l'envoi de l'e-mail.");
        }
      }
    } catch (err) {
      setErrorMsg(err.message || t('auth.unexpected'));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsGoogleSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await loginWithGoogle();
      if (res.ok && res.user) {
        setSuccessMsg('Connexion Google Firebase réussie !');
        setTimeout(() => {
          onAuthSuccess(res.user);
          onClose();
        }, 600);
      } else {
        setErrorMsg(res.error || "Erreur de connexion Google.");
      }
    } catch (err) {
      setErrorMsg(err.message || "Erreur lors de l'authentification Google.");
    } finally {
      setIsGoogleSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center overflow-hidden bg-black/60 backdrop-blur-sm sm:items-center sm:overflow-y-auto sm:p-4" onMouseDown={(event) => event.target === event.currentTarget && onClose()}>
      <div ref={panelRef} role="dialog" aria-modal="true" aria-labelledby="auth-dialog-title" tabIndex="-1" className="max-h-[calc(100dvh-env(safe-area-inset-top))] w-full max-w-md overflow-y-auto rounded-t-3xl border border-stone-200 bg-white p-5 pb-[max(1.25rem,env(safe-area-inset-bottom))] shadow-2xl sm:my-8 sm:rounded-3xl sm:p-8">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100 mb-5">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Lokiini" className="h-8 w-auto object-contain" />
            <div>
              <h2 id="auth-dialog-title" className="font-black text-lg text-lokiini-charcoal font-['Outfit']">
                {authMode === 'login' && t('auth.loginTitle')}
                {authMode === 'register' && t('auth.registerTitle')}
                {authMode === 'forgot_password' && t('auth.recoverTitle')}
              </h2>
              <span className="text-[11px] text-stone-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                {t('auth.secure')}
              </span>
            </div>
          </div>
          <button
            type="button"
            data-autofocus
            onClick={onClose}
            aria-label={t('modal.closeAria')}
            className="flex size-11 items-center justify-center rounded-full bg-stone-100 text-stone-600 transition-colors hover:bg-stone-200 sm:size-9"
          >
            <X aria-hidden="true" className="w-4 h-4" />
          </button>
        </div>

        {/* Notifications & Error messages */}
        {errorMsg && (
          <div role="alert" className="bg-red-50 text-red-700 border border-red-200 rounded-xl p-3 text-xs flex items-center gap-2 mb-4 animate-in fade-in">
            <AlertCircle aria-hidden="true" className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div role="status" className="bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl p-3 text-xs flex items-center gap-2 mb-4 animate-in fade-in">
            <CheckCircle2 aria-hidden="true" className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* FORGOT PASSWORD VIEW */}
        {authMode === 'forgot_password' ? (
          <div className="space-y-4">
            <div className="p-3 bg-stone-50 rounded-2xl border border-stone-200 text-xs text-stone-600 leading-relaxed">
              {t('auth.resetIntro')}
            </div>

            <form onSubmit={handleEmailSubmit} className="space-y-3">
              <div>
                <label htmlFor="auth-reset-email" className="block text-xs font-bold text-stone-700 mb-1">{t('form.email')} <span aria-hidden="true">*</span></label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                  <input
                    id="auth-reset-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="min-h-12 w-full rounded-xl border border-stone-300 bg-stone-50 py-2.5 pe-3.5 ps-10 text-base text-stone-800 focus:border-lokiini-teal focus:outline-none sm:text-sm"
                    placeholder="votre.email@domaine.ma"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs mt-2"
              >
                {isSubmitting ? t('auth.sending') : t('auth.sendReset')}
              </button>
            </form>

            <button
              type="button"
              onClick={() => setAuthMode('login')}
              className="w-full text-center text-xs font-bold text-stone-500 hover:text-stone-800 flex items-center justify-center gap-1.5 pt-2"
            >
              <ArrowLeft className="rtl-flip w-3.5 h-3.5" />
              {t('auth.backToLogin')}
            </button>
          </div>
        ) : (
          /* LOGIN & REGISTER VIEWS */
          <>
            {/* Google 1-Click Auth */}
            <button
              type="button"
              onClick={handleGoogleSignIn}
              disabled={isGoogleSubmitting}
              className="w-full mb-4 flex items-center justify-center gap-3 bg-white border border-stone-300 hover:border-stone-400 hover:bg-stone-50 text-stone-700 font-bold py-2.5 px-4 rounded-xl text-xs transition-all shadow-xs"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.87c2.26-2.09 3.675-5.17 3.675-9.15z"
                />
                <path
                  fill="#34A853"
                  d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.87-3.05c-1.08.72-2.45 1.16-4.06 1.16-3.13 0-5.78-2.11-6.73-4.96H1.27v3.15C3.25 21.31 7.31 24 12 24z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.27 14.24c-.25-.72-.38-1.49-.38-2.24s.13-1.52.38-2.24V6.61H1.27C.46 8.23 0 10.06 0 12s.46 3.77 1.27 5.39l4-3.15z"
                />
                <path
                  fill="#EA4335"
                  d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.25 2.69 1.27 6.61l4 3.15c.95-2.85 3.6-4.96 6.73-4.96z"
                />
              </svg>
              <span>{isGoogleSubmitting ? t('auth.googleLoading') : t('auth.google')}</span>
            </button>

            <div className="flex items-center my-4">
              <div className="flex-1 border-t border-stone-200"></div>
              <span className="px-3 text-[11px] text-stone-400 uppercase tracking-wider font-semibold">{t('auth.orEmail')}</span>
              <div className="flex-1 border-t border-stone-200"></div>
            </div>

            <form onSubmit={handleEmailSubmit} className="space-y-3.5">
              
              {/* Role selector if registering */}
              {authMode === 'register' && (
                <div role="radiogroup" aria-label={t('auth.accountType')} className="grid grid-cols-2 gap-2 mb-3 bg-stone-100 p-1.5 rounded-xl">
                  <button
                    type="button"
                    role="radio"
                    aria-checked={role === 'renter'}
                    tabIndex={role === 'renter' ? 0 : -1}
                    onClick={() => setRole('renter')}
                    onKeyDown={handleRoleKeyDown}
                    className={`py-2 text-xs font-bold rounded-lg transition-all ${
                      role === 'renter' ? 'bg-white text-lokiini-teal shadow-xs' : 'text-stone-500 hover:text-stone-800'
                    }`}
                  >
                    {t('auth.renterRole')}
                  </button>
                  <button
                    type="button"
                    role="radio"
                    aria-checked={role === 'pro_owner'}
                    tabIndex={role === 'pro_owner' ? 0 : -1}
                    onClick={() => setRole('pro_owner')}
                    onKeyDown={handleRoleKeyDown}
                    className={`py-2 text-xs font-bold rounded-lg transition-all ${
                      role === 'pro_owner' ? 'bg-white text-lokiini-teal shadow-xs' : 'text-stone-500 hover:text-stone-800'
                    }`}
                  >
                    {t('auth.ownerRole')}
                  </button>
                </div>
              )}

              {/* Full Name for Register */}
              {authMode === 'register' && (
                <div>
                  <label htmlFor="auth-full-name" className="block text-xs font-bold text-stone-700 mb-1">{t('auth.fullName')} <span aria-hidden="true">*</span></label>
                  <div className="relative">
                    <User className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                    <input
                      id="auth-full-name"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="min-h-12 w-full rounded-xl border border-stone-300 bg-stone-50 py-2 pe-3.5 ps-10 text-base text-stone-800 focus:border-lokiini-teal focus:outline-none sm:text-sm"
                      placeholder="Ex: Samir El Fassi ou Société BTP"
                      required
                    />
                  </div>
                </div>
              )}

              {/* Email */}
              <div>
                <label htmlFor="auth-email" className="block text-xs font-bold text-stone-700 mb-1">{t('form.email')} <span aria-hidden="true">*</span></label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                  <input
                    id="auth-email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="min-h-12 w-full rounded-xl border border-stone-300 bg-stone-50 py-2 pe-3.5 ps-10 text-base text-stone-800 focus:border-lokiini-teal focus:outline-none sm:text-sm"
                    placeholder="contact@exemple.ma"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label htmlFor="auth-password" className="block text-xs font-bold text-stone-700">{t('auth.password')} <span aria-hidden="true">*</span></label>
                  {authMode === 'login' && (
                    <button
                      type="button"
                      onClick={() => setAuthMode('forgot_password')}
                      className="text-[11px] text-lokiini-teal hover:underline font-semibold"
                    >
                      {t('auth.forgotPassword')}
                    </button>
                  )}
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                  <input
                    id="auth-password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="min-h-12 w-full rounded-xl border border-stone-300 bg-stone-50 py-2 pe-3.5 ps-10 text-base text-stone-800 focus:border-lokiini-teal focus:outline-none sm:text-sm"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              {/* Extra register fields */}
              {authMode === 'register' && (
                <>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div>
                      <label htmlFor="auth-phone" className="block text-xs font-bold text-stone-700 mb-1">{t('form.phone')} <span aria-hidden="true">*</span></label>
                      <div className="relative">
                        <Phone className="w-3.5 h-3.5 absolute start-3 top-1/2 -translate-y-1/2 text-stone-400" />
                        <input
                          id="auth-phone"
                          type="tel"
                          value={phoneNumber}
                          onChange={(e) => setPhoneNumber(e.target.value)}
                          className="min-h-12 w-full rounded-xl border border-stone-300 bg-stone-50 py-2 pe-3 ps-8 text-base text-stone-800 focus:border-lokiini-teal focus:outline-none sm:text-sm"
                          placeholder="+212 6 12 34 56 78"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label htmlFor="auth-city" className="block text-xs font-bold text-stone-700 mb-1">{t('form.city')} <span aria-hidden="true">*</span></label>
                      <select
                        id="auth-city"
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="min-h-12 w-full rounded-xl border border-stone-300 bg-stone-50 px-3 py-2 text-base text-stone-800 focus:border-lokiini-teal focus:outline-none sm:text-sm"
                      >
                        {MOROCCAN_CITIES.filter(c => c !== 'Toutes les villes').map(c => (
                          <option key={c} value={c}>{cityLabel(c)}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {role === 'pro_owner' && (
                    <div className="grid gap-3 rounded-xl border border-stone-200 bg-stone-50 p-3 sm:grid-cols-2">
                      <div>
                        <label htmlFor="auth-company" className="block text-[11px] font-bold text-stone-700 mb-1 flex items-center gap-1">
                          <Building2 className="w-3 h-3 text-stone-500" />
                          {t('auth.company')}
                        </label>
                        <input
                          id="auth-company"
                          type="text"
                          value={companyName}
                          onChange={(e) => setCompanyName(e.target.value)}
                          placeholder="Nom légal SARL"
                          className="min-h-12 w-full rounded-lg border border-stone-300 bg-white px-2.5 py-1.5 text-base text-stone-800 sm:text-sm"
                        />
                      </div>
                      <div>
                        <label htmlFor="auth-ice" className="block text-[11px] font-bold text-stone-700 mb-1">{t('auth.ice')}</label>
                        <input
                          id="auth-ice"
                          type="text"
                          value={companyIce}
                          onChange={(e) => setCompanyIce(e.target.value)}
                          placeholder="000000000000000"
                          maxLength={15}
                          className="min-h-12 w-full rounded-lg border border-stone-300 bg-white px-2.5 py-1.5 font-mono text-base text-stone-800 sm:text-sm"
                        />
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs mt-2"
              >
                {isSubmitting ? (
                  <span>{t('auth.processing')}</span>
                ) : authMode === 'login' ? (
                  <span>{t('auth.signIn')}</span>
                ) : (
                  <span>{t('auth.create')}</span>
                )}
              </button>
            </form>

            {/* Toggle Login / Register */}
            <div className="text-center mt-4 pt-4 border-t border-stone-100 text-xs text-stone-500">
              {authMode === 'login' ? (
                <span>
                  {t('auth.noAccount')}{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('register');
                      setErrorMsg(null);
                      setSuccessMsg(null);
                    }}
                    className="font-bold text-lokiini-teal hover:underline"
                  >
                    {t('auth.signUp')}
                  </button>
                </span>
              ) : (
                <span>
                  {t('auth.hasAccount')}{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setErrorMsg(null);
                      setSuccessMsg(null);
                    }}
                    className="font-bold text-lokiini-teal hover:underline"
                  >
                    {t('auth.signIn')}
                  </button>
                </span>
              )}
            </div>
          </>
        )}

      </div>
    </div>
  );
}
