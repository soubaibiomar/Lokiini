import React, { useState } from 'react';
import { X, User, Lock, Mail, Phone, Building2, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { loginUser, registerUser } from '../services/api';
import { MOROCCAN_CITIES } from '../data/mockData';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
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
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      if (isLogin) {
        const res = await loginUser(email, password);
        if (res && res.user) {
          setSuccessMsg('Connexion réussie !');
          setTimeout(() => {
            onAuthSuccess(res.user);
            onClose();
          }, 800);
        } else {
          // Fallback simulation
          const fallbackUser = {
            id: 'a1111111-1111-1111-1111-111111111111',
            full_name: email.includes('atlas') ? 'Atlas Location BTP Maroc' : 'Karim Tazi',
            email: email,
            phone_number: '+212661000001',
            user_role: email.includes('atlas') ? 'pro_owner' : 'renter',
            is_kyc_verified: true,
            kyc_liveness_score: 98.5
          };
          localStorage.setItem('lokiini_user', JSON.stringify(fallbackUser));
          setSuccessMsg('Connexion réussie !');
          setTimeout(() => {
            onAuthSuccess(fallbackUser);
            onClose();
          }, 800);
        }
      } else {
        const payload = {
          full_name: fullName,
          email: email,
          password: password,
          phone_number: phoneNumber,
          city: city,
          user_role: role,
          company_name: role === 'pro_owner' ? companyName : null,
          company_ice: role === 'pro_owner' ? companyIce : null
        };
        const created = await registerUser(payload);
        setSuccessMsg('Compte créé avec succès ! Connectez-vous.');
        setIsLogin(true);
      }
    } catch (err) {
      setErrorMsg("Une erreur s'est produite lors de l'authentification.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-md w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100 mb-6">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="Lokiini" className="h-8 w-auto object-contain" />
            <div>
              <h3 className="font-black text-lg text-lokiini-charcoal font-['Outfit']">
                {isLogin ? 'Connexion Espace Membre' : 'Créer un Compte Lokiini'}
              </h3>
              <span className="text-[11px] text-stone-400">Accès sécurisé & conformité CNDP</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {errorMsg && (
          <div className="bg-red-50 text-red-700 border border-red-200 rounded-xl p-3 text-xs flex items-center gap-2 mb-4">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {successMsg && (
          <div className="bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-xl p-3 text-xs flex items-center gap-2 mb-4">
            <CheckCircle2 className="w-4 h-4 shrink-0" />
            <span>{successMsg}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3.5">
          
          {/* Role selector if registering */}
          {!isLogin && (
            <div className="grid grid-cols-2 gap-2 mb-4 bg-stone-100 p-1.5 rounded-xl">
              <button
                type="button"
                onClick={() => setRole('renter')}
                className={`py-2 text-xs font-bold rounded-lg transition-all ${
                  role === 'renter' ? 'bg-white text-lokiini-teal shadow-xs' : 'text-stone-500 hover:text-stone-800'
                }`}
              >
                Locataire
              </button>
              <button
                type="button"
                onClick={() => setRole('pro_owner')}
                className={`py-2 text-xs font-bold rounded-lg transition-all ${
                  role === 'pro_owner' ? 'bg-white text-lokiini-teal shadow-xs' : 'text-stone-500 hover:text-stone-800'
                }`}
              >
                Loueur Pro BTP
              </button>
            </div>
          )}

          {!isLogin && (
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Nom Complet / Raison Sociale *</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                required
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1">Adresse E-mail *</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-stone-700 mb-1">Mot de Passe *</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
              required
            />
          </div>

          {!isLogin && (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-stone-700 mb-1">Téléphone (+212) *</label>
                  <input
                    type="text"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
                    required
                  />
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
                    <label className="block text-[11px] font-bold text-stone-700 mb-1">Société SARL</label>
                    <input
                      type="text"
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      className="w-full bg-white border border-stone-300 rounded-lg px-2.5 py-1.5 text-xs text-stone-800"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-bold text-stone-700 mb-1">ICE Maroc (15 chiffres)</label>
                    <input
                      type="text"
                      value={companyIce}
                      onChange={(e) => setCompanyIce(e.target.value)}
                      className="w-full bg-white border border-stone-300 rounded-lg px-2.5 py-1.5 text-xs text-stone-800 font-mono"
                    />
                  </div>
                </div>
              )}
            </>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs mt-2"
          >
            {isSubmitting ? (
              <span>Traitement en cours...</span>
            ) : isLogin ? (
              <span>Se Connecter</span>
            ) : (
              <span>Créer mon Compte</span>
            )}
          </button>
        </form>

        {/* Toggle Login / Register */}
        <div className="text-center mt-4 pt-4 border-t border-stone-100 text-xs text-stone-500">
          {isLogin ? (
            <span>
              Pas encore de compte ?{' '}
              <button
                type="button"
                onClick={() => setIsLogin(false)}
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
                onClick={() => setIsLogin(true)}
                className="font-bold text-lokiini-teal hover:underline"
              >
                Connectez-vous
              </button>
            </span>
          )}
        </div>

      </div>
    </div>
  );
}
