import React, { useState, useEffect } from 'react';
import { 
  MapPin, Search, Shield, FileCheck, CreditCard, Sparkles, 
  X, CheckCircle2, TrendingUp, Hammer, Wrench, Droplets, Zap, Camera, Flame, Layers
} from 'lucide-react';
import { MOROCCAN_CITIES, CATEGORIES } from '../data/mockData';

const ROTATING_EQUIPMENT = [
  { text: 'Bétonnières & Engins BTP', color: 'text-lokiini-teal', tag: 'Chantier & Gros Œuvre' },
  { text: 'Mini-Pelles & Bobcats', color: 'text-lokiini-terracotta', tag: 'Terrassement' },
  { text: 'Caméras FX3 & Audiovisuel', color: 'text-amber-700', tag: 'Cinéma & Vidéo' },
  { text: 'Groupes Électrogènes 10kVA', color: 'text-emerald-700', tag: 'Énergie & Secours' },
  { text: 'Nettoyeurs Haute Pression', color: 'text-blue-700', tag: 'Nettoyage Pro' },
];

const TRENDING_SEARCHES = [
  'Bétonnière 160L',
  'Bobcat E19',
  'Sony FX3',
  'Nettoyeur 180 Bar',
  'Groupe 10kVA'
];

export default function Hero({ selectedCity, setSelectedCity, selectedCategory, setSelectedCategory, searchTerm, setSearchTerm }) {
  const [rotatingIndex, setRotatingIndex] = useState(0);
  const [isFading, setIsFading] = useState(false);

  // Rotate tagline item every 3 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setIsFading(true);
      setTimeout(() => {
        setRotatingIndex((prev) => (prev + 1) % ROTATING_EQUIPMENT.length);
        setIsFading(false);
      }, 250);
    }, 3200);
    return () => clearInterval(interval);
  }, []);

  const getCategoryIcon = (id) => {
    switch (id) {
      case 'btp': return Hammer;
      case 'tools': return Wrench;
      case 'cleaning': return Droplets;
      case 'energy': return Zap;
      case 'audiovisual': return Camera;
      case 'heating': return Flame;
      default: return Layers;
    }
  };

  return (
    <section className="relative pt-10 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden bg-gradient-to-b from-stone-100/80 via-stone-50/50 to-lokiini-sand">
      
      {/* Decorative Ambient Background Glows */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-teal-200/30 rounded-full blur-3xl pointer-events-none -translate-y-1/2 animate-pulse" />
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-orange-200/30 rounded-full blur-3xl pointer-events-none animate-pulse" style={{ animationDelay: '1.5s' }} />

      <div className="max-w-6xl mx-auto text-center relative z-10">
        
        {/* Dynamic Live Moroccan Badge */}
        <div className="inline-flex items-center gap-2.5 bg-white/95 border border-stone-200/90 px-4 py-1.5 rounded-full shadow-sm mb-6 backdrop-blur-md hover:shadow-md hover:border-stone-300 transition-all cursor-default">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-bold text-stone-800">
            Le Tiers de Confiance de la Location de Matériel au Maroc
          </span>
        </div>

        {/* Dynamic Hero Animated Heading */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-lokiini-charcoal tracking-tight font-['Outfit'] mb-3">
          Empruntez vos{' '}
          <span 
            className={`inline-block transition-all duration-300 transform ${
              isFading ? 'opacity-0 -translate-y-2' : 'opacity-100 translate-y-0'
            } ${ROTATING_EQUIPMENT[rotatingIndex].color}`}
          >
            {ROTATING_EQUIPMENT[rotatingIndex].text}
          </span>
        </h1>

        <p className="text-base sm:text-lg text-stone-600 max-w-2xl mx-auto mb-8 font-normal">
          Achetez moins, rentabilisez plus. Louez en toute confiance avec{' '}
          <span className="font-bold text-lokiini-charcoal">caution non débitée CMI</span> et{' '}
          <span className="font-bold text-lokiini-charcoal">baux légaux DOC horodatés</span>.
        </p>

        {/* Dynamic Category Quick-Filter Bar with Icons */}
        <div className="flex items-center justify-center gap-2 flex-wrap max-w-4xl mx-auto mb-6">
          {CATEGORIES.map((cat) => {
            const Icon = getCategoryIcon(cat.id);
            const isSelected = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all ${
                  isSelected
                    ? 'bg-lokiini-teal text-white shadow-md scale-105'
                    : 'bg-white/80 hover:bg-white text-stone-600 border border-stone-200 shadow-xs hover:border-stone-300'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-stone-500'}`} />
                <span>{cat.label}</span>
              </button>
            );
          })}
        </div>

        {/* Floating Interactive Search Pill Bar */}
        <div className="max-w-4xl mx-auto bg-white p-3 rounded-2xl sm:rounded-full shadow-xl border border-stone-200 flex flex-col sm:flex-row items-center gap-3 relative transition-all focus-within:ring-2 focus-within:ring-lokiini-teal/30">
          
          {/* City Selector */}
          <div className="flex items-center gap-2 px-4 py-2.5 w-full sm:w-auto flex-1 border-b sm:border-b-0 sm:border-r border-stone-200">
            <MapPin className="w-5 h-5 text-lokiini-terracotta shrink-0" />
            <select
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="bg-transparent font-bold text-stone-800 text-sm focus:outline-none w-full cursor-pointer"
            >
              {MOROCCAN_CITIES.map((city) => (
                <option key={city} value={city}>{city}</option>
              ))}
            </select>
          </div>

          {/* Search Input with Clear Button */}
          <div className="flex items-center gap-2 px-4 py-2.5 w-full sm:w-auto flex-2">
            <Search className="w-4 h-4 text-stone-400 shrink-0" />
            <input
              type="text"
              placeholder="Ex: Bétonnière, Mini-pelle Bobcat, Caméra FX3, Groupe..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-transparent text-sm font-medium focus:outline-none w-full text-stone-800 placeholder:text-stone-400"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="text-stone-400 hover:text-stone-600 p-1 rounded-full hover:bg-stone-100 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Search Action Button */}
          <button 
            onClick={() => {
              const el = document.getElementById('catalogue-grid');
              if (el) el.scrollIntoView({ behavior: 'smooth' });
            }}
            className="w-full sm:w-auto bg-lokiini-terracotta hover:bg-lokiini-terracotta-dark text-white font-bold text-sm px-8 py-3.5 rounded-xl sm:rounded-full transition-all shadow-md shrink-0 flex items-center justify-center gap-2 hover:scale-[1.02]"
          >
            <Sparkles className="w-4 h-4" />
            <span>Rechercher</span>
          </button>
        </div>

        {/* Dynamic Trending Suggestions Chips */}
        <div className="flex items-center justify-center gap-2 flex-wrap mt-4 text-xs">
          <span className="text-stone-400 flex items-center gap-1 font-semibold">
            <TrendingUp className="w-3 h-3 text-lokiini-terracotta" /> Tendances :
          </span>
          {TRENDING_SEARCHES.map((term) => (
            <button
              key={term}
              onClick={() => setSearchTerm(term)}
              className="bg-stone-200/60 hover:bg-stone-200 text-stone-700 font-medium px-2.5 py-1 rounded-lg transition-colors"
            >
              {term}
            </button>
          ))}
          {selectedCity !== 'Toutes les villes' && (
            <button
              onClick={() => setSelectedCity('Toutes les villes')}
              className="bg-teal-50 text-lokiini-teal font-bold px-2.5 py-1 rounded-lg border border-teal-200 hover:bg-teal-100 transition-colors flex items-center gap-1"
            >
              <span>Ville : {selectedCity}</span>
              <X className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* 3 Interactive Trust Pillars with Hover Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-5 max-w-4xl mx-auto mt-12 text-left">
          
          {/* Pillar 1 : CMI Caution */}
          <div className="bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-stone-200/90 shadow-sm hover:shadow-md hover:border-lokiini-teal/50 transition-all group">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-teal-50 flex items-center justify-center text-lokiini-teal shrink-0 group-hover:scale-110 transition-transform">
                <CreditCard className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-lokiini-charcoal flex items-center gap-1">
                  <span>Caution CMI Sans Débit</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-lokiini-teal" />
                </div>
                <div className="text-[11px] text-stone-500 mt-0.5 leading-snug">
                  Plafond bloqué temporairement, 0 DH prélevé de votre compte.
                </div>
              </div>
            </div>
          </div>

          {/* Pillar 2 : CNDP KYC */}
          <div className="bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-stone-200/90 shadow-sm hover:shadow-md hover:border-lokiini-terracotta/50 transition-all group">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-orange-50 flex items-center justify-center text-lokiini-terracotta shrink-0 group-hover:scale-110 transition-transform">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-lokiini-charcoal flex items-center gap-1">
                  <span>Conformité CNDP Loi 09-08</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-lokiini-terracotta" />
                </div>
                <div className="text-[11px] text-stone-500 mt-0.5 leading-snug">
                  Contrôle d'identité Zero-Knowledge : vidéos purgées de la RAM.
                </div>
              </div>
            </div>
          </div>

          {/* Pillar 3 : Contrat DOC */}
          <div className="bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-stone-200/90 shadow-sm hover:shadow-md hover:border-emerald-500/50 transition-all group">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0 group-hover:scale-110 transition-transform">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-lokiini-charcoal flex items-center gap-1">
                  <span>Bail DOC & Horodatage</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                </div>
                <div className="text-[11px] text-stone-500 mt-0.5 leading-snug">
                  Contrat certifié Loi 53-05 et état des lieux vidéo SHA-256.
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
