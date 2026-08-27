import React, { useState, useEffect } from 'react';
import { 
  MapPin, Search, ShieldCheck, FileCheck, Banknote, Sparkles, 
  X, CheckCircle2, TrendingUp, Wrench, Camera, Music, Compass, Bike, Layers, ArrowRight
} from 'lucide-react';
import { MOROCCAN_CITIES, CATEGORIES } from '../data/mockData';

const ROTATING_EQUIPMENT = [
  { text: 'Perforateurs & Outillage Pro', color: 'text-emerald-700', tag: 'Bricolage & Travaux' },
  { text: 'Caméras FX3 & Matériel 4K', color: 'text-amber-700', tag: 'Audiovisuel & Cinéma' },
  { text: 'Guitares & Sonorisation', color: 'text-blue-700', tag: 'Musique & Événements' },
  { text: 'Tentes de Toit & Camping', color: 'text-emerald-800', tag: 'Bivouac & Aventure' },
  { text: 'Remorques & Vélos Électriques', color: 'text-cyan-800', tag: 'Transport & Mobilité' },
];

const TRENDING_SEARCHES = [
  'Perforateur Bosch',
  'Sony FX3',
  'Guitare Fender',
  'JBL PartyBox 710',
  'Tente de Toit Hussarde',
  'Remorque 500kg'
];

export default function Hero({ selectedCity, setSelectedCity, selectedCategory, setSelectedCategory, searchTerm, setSearchTerm }) {
  const [rotatingIndex, setRotatingIndex] = useState(0);
  const [isFading, setIsFading] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsFading(true);
      setTimeout(() => {
        setRotatingIndex((prev) => (prev + 1) % ROTATING_EQUIPMENT.length);
        setIsFading(false);
      }, 250);
    }, 3400);
    return () => clearInterval(interval);
  }, []);

  const getCategoryIcon = (id) => {
    switch (id) {
      case 'outils': return Wrench;
      case 'electronique': return Camera;
      case 'musique': return Music;
      case 'evenementiel': return Sparkles;
      case 'outdoor': return Compass;
      case 'velos': return Bike;
      default: return Layers;
    }
  };

  return (
    <section className="relative pt-10 pb-14 px-4 sm:px-6 lg:px-8 overflow-hidden bg-gradient-to-b from-stone-100 via-stone-50 to-stone-100/60 border-b border-stone-200">
      
      {/* Decorative Ambient Background */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-200/20 rounded-full blur-3xl pointer-events-none -translate-y-1/2" />
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-amber-200/20 rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-6xl mx-auto text-center relative z-10">
        
        {/* Top Trust Capsule */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white border border-stone-200 shadow-sm mb-6 animate-fade-in">
          <span className="flex h-2 w-2 rounded-full bg-emerald-600 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-stone-700">
            Marketplace Nationale Sécurisée | Maroc
          </span>
          <span className="text-stone-300">|</span>
          <span className="text-xs font-medium text-emerald-800 flex items-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" />
            Vérification Didit
          </span>
        </div>

        {/* Main Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-stone-900 tracking-tight leading-[1.15] mb-5">
          Louez tout, à n'importe qui, <br />
          <span className="text-emerald-800">près de chez vous au Maroc</span>
        </h1>

        {/* Animated Subtitle */}
        <div className="flex items-center justify-center gap-2 text-base sm:text-xl text-stone-600 mb-8 min-h-[36px]">
          <span>Trouvez en quelques secondes :</span>
          <div className="inline-block relative overflow-hidden text-left font-bold">
            <span 
              className={`inline-block transition-all duration-300 transform ${
                isFading ? 'opacity-0 translate-y-3' : 'opacity-100 translate-y-0'
              } ${ROTATING_EQUIPMENT[rotatingIndex].color}`}
            >
              {ROTATING_EQUIPMENT[rotatingIndex].text}
            </span>
          </div>
        </div>

        {/* Unified Search Engine Panel */}
        <div className="bg-white p-3 sm:p-4 rounded-2xl shadow-xl border border-stone-200/80 max-w-4xl mx-auto mb-8 transition-all hover:shadow-2xl">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
            
            {/* Search Input */}
            <div className="md:col-span-5 relative flex items-center">
              <Search className="w-5 h-5 text-stone-400 absolute left-3.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Perforateur, Sony FX3, Tente de toit..."
                className="w-full pl-11 pr-8 py-3.5 bg-stone-50 hover:bg-stone-100/70 focus:bg-white border border-stone-200 rounded-xl text-stone-900 placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-emerald-700/30 focus:border-emerald-700 text-sm font-medium transition-all"
              />
              {searchTerm && (
                <button 
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 p-1 rounded-full text-stone-400 hover:text-stone-600 hover:bg-stone-200 transition-colors"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* City Selector */}
            <div className="md:col-span-3 relative flex items-center">
              <MapPin className="w-5 h-5 text-stone-400 absolute left-3.5 pointer-events-none" />
              <select
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="w-full pl-11 pr-8 py-3.5 bg-stone-50 hover:bg-stone-100/70 focus:bg-white border border-stone-200 rounded-xl text-stone-900 focus:outline-none focus:ring-2 focus:ring-emerald-700/30 focus:border-emerald-700 text-sm font-medium transition-all appearance-none cursor-pointer"
              >
                {MOROCCAN_CITIES.map((city) => (
                  <option key={city} value={city}>{city}</option>
                ))}
              </select>
            </div>

            {/* Category Selector */}
            <div className="md:col-span-4 flex items-center gap-2">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3.5 py-3.5 bg-stone-50 hover:bg-stone-100/70 focus:bg-white border border-stone-200 rounded-xl text-stone-900 focus:outline-none focus:ring-2 focus:ring-emerald-700/30 focus:border-emerald-700 text-sm font-medium transition-all appearance-none cursor-pointer"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.id} value={cat.id}>{cat.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Trending Searches Row */}
          <div className="mt-3 pt-3 border-t border-stone-100 flex flex-wrap items-center justify-between text-xs text-stone-500 px-1 gap-2">
            <div className="flex items-center gap-1.5 font-semibold text-stone-700">
              <TrendingUp className="w-3.5 h-3.5 text-emerald-700" />
              <span>Recherches fréquentes :</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {TRENDING_SEARCHES.map((query) => (
                <button
                  key={query}
                  onClick={() => setSearchTerm(query)}
                  className="px-2.5 py-1 rounded-md bg-stone-100 hover:bg-stone-200 text-stone-700 transition-colors font-medium"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 6 Key Categories Quick Navigation */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-10">
          {CATEGORIES.filter(c => c.id !== 'all').map((cat) => {
            const Icon = getCategoryIcon(cat.id);
            const isSelected = selectedCategory === cat.id;
            return (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(isSelected ? 'all' : cat.id)}
                className={`p-3.5 rounded-xl border text-left transition-all duration-200 group ${
                  isSelected
                    ? 'bg-emerald-800 text-white border-emerald-800 shadow-md transform -translate-y-0.5'
                    : 'bg-white hover:bg-stone-50 text-stone-800 border-stone-200 hover:border-stone-300 hover:shadow-sm'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-2 rounded-lg ${isSelected ? 'bg-emerald-700 text-white' : 'bg-stone-100 text-stone-700 group-hover:bg-emerald-50 group-hover:text-emerald-800'}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                </div>
                <div className="text-xs font-bold leading-snug">{cat.label}</div>
              </button>
            );
          })}
        </div>

        {/* 3 Pillars Value Proposition Banner */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-4xl mx-auto pt-2">
          
          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-white/90 border border-stone-200/80 shadow-xs text-left">
            <div className="p-2 rounded-lg bg-emerald-50 text-emerald-800 shrink-0">
              <Banknote className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-stone-900">Paiement Cash (COD)</div>
              <div className="text-[11px] text-stone-500 leading-tight">Réglez le montant et la caution en cash à la remise</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-white/90 border border-stone-200/80 shadow-xs text-left">
            <div className="p-2 rounded-lg bg-blue-50 text-blue-800 shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-stone-900">Vérification Didit</div>
              <div className="text-[11px] text-stone-500 leading-tight">Contrôle CIN et liveness anti-deepfake certifié</div>
            </div>
          </div>

          <div className="flex items-center gap-3 p-3.5 rounded-xl bg-white/90 border border-stone-200/80 shadow-xs text-left">
            <div className="p-2 rounded-lg bg-amber-50 text-amber-800 shrink-0">
              <FileCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-stone-900">État des Lieux Numérique</div>
              <div className="text-[11px] text-stone-500 leading-tight">Photos/vidéos scellées sous le Dahir des Contrats</div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
