import React from 'react';
import { ShieldCheck, UserCheck, PlusCircle, LayoutDashboard, User, LogOut } from 'lucide-react';

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
  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-stone-200 shadow-sm">
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

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-semibold text-stone-700">
          <button 
            onClick={() => setCurrentView('catalog')}
            className={`hover:text-lokiini-teal transition-colors ${currentView === 'catalog' ? 'text-lokiini-teal font-bold' : ''}`}
          >
            Accueil & Catalogue
          </button>
          
          <button 
            onClick={() => setCurrentView('dashboard')}
            className={`flex items-center gap-1.5 hover:text-lokiini-teal transition-colors ${currentView === 'dashboard' ? 'text-lokiini-teal font-bold' : ''}`}
          >
            <LayoutDashboard className="w-4 h-4" />
            Espace Loueur Pro
          </button>
        </nav>

        {/* Actions & KYC Status */}
        <div className="flex items-center gap-2.5">
          
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
            onClick={onOpenAddEquipment}
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
