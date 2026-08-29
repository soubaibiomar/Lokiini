import React from 'react';
import { ShieldCheck, UserCheck, PlusCircle, LayoutDashboard, User, LogOut, CreditCard, Sparkles } from 'lucide-react';

export default function Navbar({ 
  onOpenKYC, 
  onOpenAuth, 
  onOpenAddEquipment,
  isKYCVerified, 
  currentView, 
  setCurrentView,
  currentUser,
  onLogout
}) {
  const handlePricingClick = () => {
    setCurrentView('pricing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-stone-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div 
          onClick={() => setCurrentView('catalog')}
          className="flex items-center cursor-pointer group py-1"
        >
          <img 
            src="/logo.png" 
            alt="Lokiini Logo" 
            className="h-11 sm:h-13 md:h-14 w-auto object-contain group-hover:scale-105 transition-transform" 
          />
        </div>

        {/* Navigation Links (Desktop & Tablet) */}
        <nav className="hidden lg:flex items-center gap-6 text-sm font-semibold text-stone-700">
          <button 
            onClick={() => {
              setCurrentView('catalog');
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
            className={`hover:text-lokiini-teal transition-colors ${currentView === 'catalog' ? 'text-lokiini-teal font-bold' : ''}`}
          >
            Accueil & Catalogue
          </button>

          {/* Grille Tarifaire (Price Grid) */}
          <button 
            onClick={handlePricingClick}
            className={`flex items-center gap-2 px-3.5 py-2 rounded-xl transition-all ${
              currentView === 'pricing' 
                ? 'bg-emerald-50 text-lokiini-teal font-bold border border-emerald-200 shadow-sm' 
                : 'hover:text-lokiini-teal text-stone-700 hover:bg-stone-50'
            }`}
          >
            <CreditCard className="w-4 h-4 text-lokiini-teal" />
            <span>Grille Tarifaire</span>
            <span className="bg-amber-100 text-amber-800 text-[10px] px-2 py-0.5 rounded-full font-extrabold flex items-center gap-0.5">
              <Sparkles className="w-2.5 h-2.5" />
              Pro dès 7%
            </span>
          </button>
        </nav>

        {/* Actions & KYC Status */}
        <div className="flex items-center gap-2 sm:gap-2.5">
          
          {/* Quick Grille Tarifaire Link for Mobile/Tablet */}
          <button
            onClick={handlePricingClick}
            className="flex lg:hidden items-center gap-1 px-2.5 py-2 rounded-xl text-xs font-bold bg-stone-100 text-stone-800 hover:bg-stone-200 border border-stone-300 transition-all"
            title="Grille Tarifaire & Formules"
          >
            <CreditCard className="w-3.5 h-3.5 text-lokiini-teal" />
            <span>Tarifs</span>
          </button>

          {/* KYC Status Button */}
          <button
            onClick={onOpenKYC}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all border ${
              isKYCVerified
                ? 'bg-emerald-50 text-emerald-700 border-emerald-300'
                : 'bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100'
            }`}
          >
            {isKYCVerified ? (
              <>
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span className="hidden sm:inline">CIN Vérifiée (CNDP)</span>
                <span className="sm:hidden">CNDP OK</span>
              </>
            ) : (
              <>
                <UserCheck className="w-4 h-4 text-amber-600" />
                <span>Vérifier CIN</span>
              </>
            )}
          </button>

          {/* Publier une Annonce Button */}
          <button
            onClick={() => {
              if (currentUser) {
                onOpenAddEquipment();
              } else {
                onOpenAuth();
              }
            }}
            className="hidden sm:flex items-center gap-1.5 bg-lokiini-terracotta hover:bg-lokiini-terracotta-dark text-white px-3.5 py-2 rounded-xl text-xs font-bold shadow-sm hover:shadow transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Déposer une annonce</span>
          </button>

          {/* User Auth Profile Button */}
          {currentUser ? (
            <div className="flex items-center gap-1 bg-stone-100 p-1 rounded-xl">
              <button
                onClick={() => setCurrentView('dashboard')}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold text-stone-800 hover:text-lokiini-teal"
              >
                {currentUser.avatar_url || currentUser.photoURL ? (
                  <img
                    src={currentUser.avatar_url || currentUser.photoURL}
                    alt={currentUser.full_name || 'Utilisateur'}
                    className="w-5 h-5 rounded-full object-cover border border-stone-300"
                  />
                ) : (
                  <User className="w-3.5 h-3.5" />
                )}
                <span className="max-w-[110px] truncate">
                  {currentUser.full_name ? currentUser.full_name.split(' ')[0] : currentUser.email ? currentUser.email.split('@')[0] : 'Profil'}
                </span>
              </button>
              <button
                onClick={onLogout}
                className="p-1 text-stone-400 hover:text-stone-700 rounded-lg hover:bg-stone-200 transition-colors"
                title="Se déconnecter"
              >
                <LogOut className="w-3.5 h-3.5" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center gap-1.5 border border-stone-300 hover:bg-stone-50 text-stone-700 px-3 py-2 rounded-xl text-xs font-bold transition-colors"
            >
              <User className="w-4 h-4" />
              <span>Connexion</span>
            </button>
          )}

        </div>

      </div>
    </header>
  );
}
