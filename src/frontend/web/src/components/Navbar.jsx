import React from 'react';
import { ShieldCheck, UserCheck, PlusCircle, LayoutDashboard, User, LogOut, MessageSquare, HelpCircle, Tag } from 'lucide-react';

export default function Navbar({ 
  onOpenKYC, 
  onOpenAuth, 
  onOpenAddEquipment,
  onOpenPricing,
  onOpenHowItWorks,
  onOpenMessaging,
  isKYCVerified, 
  currentView, 
  setCurrentView,
  currentUser,
  onLogout
}) {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-stone-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div 
          onClick={() => setCurrentView('catalog')}
          className="flex items-center cursor-pointer group py-1"
        >
          <img 
            src="/logo.png" 
            alt="Lokiini Logo" 
            className="h-11 sm:h-12 w-auto object-contain group-hover:scale-105 transition-transform" 
          />
        </div>

        {/* Navigation Links */}
        <nav className="hidden lg:flex items-center gap-6 text-xs font-bold text-stone-700">
          <button 
            onClick={() => setCurrentView('catalog')}
            className={`hover:text-emerald-800 transition-colors ${currentView === 'catalog' ? 'text-emerald-800' : ''}`}
          >
            Accueil & Catalogue
          </button>
          
          <button 
            onClick={onOpenHowItWorks}
            className="flex items-center gap-1 hover:text-emerald-800 transition-colors text-stone-600"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            Comment ça marche
          </button>

          <button 
            onClick={onOpenPricing}
            className="flex items-center gap-1 hover:text-emerald-800 transition-colors text-stone-600"
          >
            <Tag className="w-3.5 h-3.5" />
            Tarifs & Formules
          </button>

          <button 
            onClick={() => setCurrentView('dashboard')}
            className={`flex items-center gap-1.5 hover:text-emerald-800 transition-colors ${currentView === 'dashboard' ? 'text-emerald-800' : ''}`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            Espace Loueur Pro
          </button>
        </nav>

        {/* Actions & KYC Status */}
        <div className="flex items-center gap-2">
          
          {/* Messaging Button */}
          <button
            onClick={onOpenMessaging}
            className="p-2 rounded-xl border border-stone-200 hover:bg-stone-50 text-stone-700 transition-colors relative"
            title="Messagerie instantanée"
          >
            <MessageSquare className="w-4 h-4" />
            <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-emerald-600 rounded-full"></span>
          </button>

          {/* KYC Status Button */}
          <button
            onClick={onOpenKYC}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all border ${
              isKYCVerified
                ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                : 'bg-amber-50 text-amber-900 border-amber-300 hover:bg-amber-100'
            }`}
          >
            {isKYCVerified ? (
              <>
                <ShieldCheck className="w-4 h-4 text-emerald-700" />
                <span className="hidden sm:inline">Vérifié Didit</span>
                <span className="sm:hidden">CNDP</span>
              </>
            ) : (
              <>
                <UserCheck className="w-4 h-4 text-amber-700" />
                <span>Vérifier CIN</span>
              </>
            )}
          </button>

          {/* Publier une Annonce Button */}
          <button
            onClick={onOpenAddEquipment}
            className="hidden sm:flex items-center gap-1.5 bg-emerald-800 hover:bg-emerald-900 text-white px-3.5 py-2 rounded-xl text-xs font-bold shadow-xs transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Déposer une annonce</span>
          </button>

          {/* User Auth Profile Button */}
          {currentUser ? (
            <div className="flex items-center gap-1 bg-stone-100 p-1 rounded-xl">
              <button
                onClick={() => setCurrentView('dashboard')}
                className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-bold text-stone-800 hover:text-emerald-800"
              >
                <User className="w-3.5 h-3.5" />
                <span className="max-w-[100px] truncate">{currentUser.full_name?.split(' ')[0] || 'Profil'}</span>
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
