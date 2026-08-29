import React, { useState } from 'react';
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

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  // Modes: 'login' | 'register' | 'forgot_password'
  const [authMode, setAuthMode] = useState('login');
  const [role, setRole] = useState('renter'); // 'renter' | 'pro_owner'
  
  // Form fields
  const [email, setEmail] = useState('contact@atlasbtp.ma');
  const [password, setPassword] = useState('password123');
  const [fullName, setFullName] = useState('Atlas Location BTP Maroc');
  const [phoneNumber, setPhoneNumber] = useState('+212661000001');
  const [city, setCity] = useState('Casablanca');
  const [companyName, setCompanyName] = useState('Atlas Location BTP SARL');
  const [companyIce, setCompanyIce] = useState('002345678000045');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGoogleSubmitting, setIsGoogleSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

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
          setSuccessMsg('Connexion Firebase réussie !');
          setTimeout(() => {
            onAuthSuccess(res.user);
            onClose();
          }, 600);
        } else {
          setErrorMsg(res.error || "Impossible de se connecter.");
        }
      } else if (authMode === 'register') {
        const res = await registerWithEmailPassword({
          email,
          password,
          fullName,
          phoneNumber,
          city,
          role,
          companyName: role === 'pro_owner' ? companyName : null,
          companyIce: role === 'pro_owner' ? companyIce : null
        });

        if (res.ok && res.user) {
          setSuccessMsg('Compte Firebase créé avec succès !');
          setTimeout(() => {
            onAuthSuccess(res.user);
            onClose();
          }, 600);
        } else {
          setErrorMsg(res.error || "Échec de l'inscription.");
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
      setErrorMsg("Une erreur imprévue est survenue.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setIsGoogleSubmitting(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    try {
      const res = await loginWithGoogle(role);
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
      setErrorMsg("Erreur lors de l'authentification Google.");
    } finally {
      setIsGoogleSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100 mb-5">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Lokiini" className="h-8 w-auto object-contain" />
            <div>
              <h3 className="font-black text-lg text-lokiini-charcoal font-['Outfit']">
                {authMode === 'login' && 'Connexion Espace Membre'}
                {authMode === 'register' && 'Créer un Compte Lokiini'}
                {authMode === 'forgot_password' && 'Récupération du Compte'}
              </h3>
              <span className="text-[11px] text-stone-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                Firebase Auth & Conformité CNDP Maroc
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Notifications & Error messages */}
        {errorMsg && (
          <div className="bg-red-50 text-red-700 border border-red-200 rounded-xl p-3 text-xs flex items-center gap-2 mb-4 animate-in fade-in">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl p-3 text-xs flex items-center gap-2 mb-4 animate-in fade-in">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        {/* FORGOT PASSWORD VIEW */}
        {authMode === 'forgot_password' ? (
          <div className="space-y-4">
            <div className="p-3 bg-stone-50 rounded-2xl border border-stone-200 text-xs text-stone-600 leading-relaxed">
              Saisissez votre adresse e-mail. Un lien sécurisé vous sera envoyé via <strong>Firebase Authentication</strong> pour réinitialiser votre mot de passe.
            </div>

            <form onSubmit={handleEmailSubmit} className="space-y-3">
              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Adresse E-mail *</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl pl-10 pr-3.5 py-2.5 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
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
                {isSubmitting ? 'Envoi en cours...' : 'Envoyer le lien de réinitialisation'}
              </button>
            </form>

            <button
              type="button"
              onClick={() => setAuthMode('login')}
              className="w-full text-center text-xs font-bold text-stone-500 hover:text-stone-800 flex items-center justify-center gap-1.5 pt-2"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Retour à la connexion
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
              <span>{isGoogleSubmitting ? 'Connexion Google...' : 'Continuer avec Google'}</span>
            </button>

            <div className="flex items-center my-4">
              <div className="flex-1 border-t border-stone-200"></div>
              <span className="px-3 text-[11px] text-stone-400 uppercase tracking-wider font-semibold">ou avec e-mail</span>
              <div className="flex-1 border-t border-stone-200"></div>
            </div>

            <form onSubmit={handleEmailSubmit} className="space-y-3.5">
              
              {/* Role selector if registering */}
              {authMode === 'register' && (
                <div className="grid grid-cols-2 gap-2 mb-3 bg-stone-100 p-1.5 rounded-xl">
                  <button
                    type="button"
                    onClick={() => setRole('renter')}
                    className={`py-2 text-xs font-bold rounded-lg transition-all ${
                      role === 'renter' ? 'bg-white text-lokiini-teal shadow-xs' : 'text-stone-500 hover:text-stone-800'
                    }`}
                  >
                    Locataire / Particulier
                  </button>
                  <button
                    type="button"
                    onClick={() => setRole('pro_owner')}
                    className={`py-2 text-xs font-bold rounded-lg transition-all ${
                      role === 'pro_owner' ? 'bg-white text-lokiini-teal shadow-xs' : 'text-stone-500 hover:text-stone-800'
                    }`}
                  >
                    Loueur Pro / Entreprise
                  </button>
                </div>
              )}

              {/* Full Name for Register */}
              {authMode === 'register' && (
                <div>
                  <label className="block text-xs font-bold text-stone-700 mb-1">Nom Complet / Raison Sociale *</label>
                  <div className="relative">
                    <User className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                    <input
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full bg-stone-50 border border-stone-300 rounded-xl pl-10 pr-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                      placeholder="Ex: Samir El Fassi ou Société BTP"
                      required
                    />
                  </div>
                </div>
              )}

              {/* Email */}
              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Adresse E-mail *</label>
                <div className="relative">
                  <Mail className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl pl-10 pr-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                    placeholder="contact@exemple.ma"
                    required
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="block text-xs font-bold text-stone-700">Mot de Passe *</label>
                  {authMode === 'login' && (
                    <button
                      type="button"
                      onClick={() => setAuthMode('forgot_password')}
                      className="text-[11px] text-lokiini-teal hover:underline font-semibold"
                    >
                      Mot de passe oublié ?
                    </button>
                  )}
                </div>
                <div className="relative">
                  <Lock className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl pl-10 pr-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>

              {/* Extra register fields */}
              {authMode === 'register' && (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-stone-700 mb-1">Téléphone (+212) *</label>
                      <div className="relative">
                        <Phone className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-stone-400" />
                        <input
                          type="text"
                          value={phoneNumber}
                          onChange={(e) => setPhoneNumber(e.target.value)}
                          className="w-full bg-stone-50 border border-stone-300 rounded-xl pl-8 pr-3 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                          placeholder="+2126XXXXXXXX"
                          required
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-stone-700 mb-1">Ville *</label>
                      <select
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                      >
                        {MOROCCAN_CITIES.filter(c => c !== 'Toutes les villes').map(c => (
                          <option key={c} value={c}>{c}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {role === 'pro_owner' && (
                    <div className="grid grid-cols-2 gap-3 bg-stone-50 p-3 rounded-xl border border-stone-200">
                      <div>
                        <label className="block text-[11px] font-bold text-stone-700 mb-1 flex items-center gap-1">
                          <Building2 className="w-3 h-3 text-stone-500" />
                          Société SARL
                        </label>
                        <input
                          type="text"
                          value={companyName}
                          onChange={(e) => setCompanyName(e.target.value)}
                          placeholder="Nom légal SARL"
                          className="w-full bg-white border border-stone-300 rounded-lg px-2.5 py-1.5 text-xs text-stone-800"
                        />
                      </div>
                      <div>
                        <label className="block text-[11px] font-bold text-stone-700 mb-1">ICE Maroc (15 ch.)</label>
                        <input
                          type="text"
                          value={companyIce}
                          onChange={(e) => setCompanyIce(e.target.value)}
                          placeholder="000000000000000"
                          maxLength={15}
                          className="w-full bg-white border border-stone-300 rounded-lg px-2.5 py-1.5 text-xs text-stone-800 font-mono"
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
                  <span>Traitement Firebase en cours...</span>
                ) : authMode === 'login' ? (
                  <span>Se Connecter avec Firebase</span>
                ) : (
                  <span>Créer mon Compte avec Firebase</span>
                )}
              </button>
            </form>

            {/* Toggle Login / Register */}
            <div className="text-center mt-4 pt-4 border-t border-stone-100 text-xs text-stone-500">
              {authMode === 'login' ? (
                <span>
                  Pas encore de compte ?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('register');
                      setErrorMsg(null);
                      setSuccessMsg(null);
                    }}
                    className="font-bold text-lokiini-teal hover:underline"
                  >
                    Inscrivez-vous gratuitement
                  </button>
                </span>
              ) : (
                <span>
                  Vous avez déjà un compte ?{' '}
                  <button
                    type="button"
                    onClick={() => {
                      setAuthMode('login');
                      setErrorMsg(null);
                      setSuccessMsg(null);
                    }}
                    className="font-bold text-lokiini-teal hover:underline"
                  >
                    Connectez-vous
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
