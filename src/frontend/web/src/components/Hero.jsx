import React, { useState, useEffect } from 'react';
import { 
  MapPin, Search, Shield, FileCheck, CreditCard, Sparkles, 
  X, CheckCircle2, TrendingUp, Hammer, Wrench, Zap, Camera, 
  Truck, Laptop, HeartPulse, Layers
} from 'lucide-react';
import { MOROCCAN_CITIES, CATEGORIES } from '../data/mockData';

const ROTATING_EQUIPMENT = [
  { text: 'Tentes & Matériel Événementiel', color: 'text-lokiini-teal', tag: 'Mariages & Soirées' },
  { text: 'Caméras Cinéma & Drones 4K', color: 'text-amber-700', tag: 'Tournage & Créateurs' },
  { text: 'Outillage, Bricolage & Jardin', color: 'text-emerald-700', tag: 'Maison & Pro' },
  { text: 'Véhicules, Quads & Loisirs', color: 'text-lokiini-terracotta', tag: 'Transport & Aventure' },
  { text: 'High-Tech, PC Gamer & Casques VR', color: 'text-blue-700', tag: 'Tech & Gaming' },
  { text: 'Fauteuils & Matériel Médical', color: 'text-rose-700', tag: 'Santé à Domicile' },
  { text: 'Bétonnières, Mini-Pelles & BTP', color: 'text-stone-700', tag: 'Chantier & Travaux' },
];

const TRENDING_SEARCHES = [
  'Tente Caïdale',
  'Sony FX3',
  'Drone DJI',
  'Fourgon 12m³',
  'Meta Quest 3',
  'Kärcher Pro',
  'Bobcat E19',
  'Fauteuil Roulant'
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
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const getCategoryIcon = (id) => {
    switch (id) {
      case 'event': return Sparkles;
      case 'audiovisual': return Camera;
      case 'tools': return Wrench;
      case 'btp': return Hammer;
      case 'energy': return Zap;
      case 'vehicles': return Truck;
      case 'hightech': return Laptop;
      case 'medical': return HeartPulse;
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
            N°1 de la Location Universelle de Tout Matériel au Maroc
          </span>
        </div>

        {/* Dynamic Hero Animated Heading */}
        <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black text-lokiini-charcoal tracking-tight font-['Outfit'] mb-3">
          Louez tout ce dont vous avez besoin :{' '}
          <br className="hidden sm:inline" />
          <span 
            className={`inline-block transition-all duration-300 transform ${
              isFading ? 'opacity-0 -translate-y-2' : 'opacity-100 translate-y-0'
            } ${ROTATING_EQUIPMENT[rotatingIndex].color}`}
          >
            {ROTATING_EQUIPMENT[rotatingIndex].text}
          </span>
        </h1>

        <p className="text-base sm:text-lg text-stone-600 max-w-2xl mx-auto mb-8 font-normal">
          Particuliers, artisans, créateurs et entreprises : louez et rentabilisez <span className="font-bold text-lokiini-charcoal">n'importe quel équipement</span> en toute sérénité avec <span className="font-bold text-lokiini-charcoal">caution CMI sécurisée</span> et <span className="font-bold text-lokiini-charcoal">baux DOC légaux</span>.
        </p>

        {/* Dynamic Category Quick-Filter Bar with Icons */}
        <div className="flex items-center justify-center gap-2 flex-wrap max-w-5xl mx-auto mb-6">
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
              placeholder="Que souhaitez-vous louer ? (ex: Tente, Caméra, Drone, Kärcher, Fourgon, Quad...)"
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
            <TrendingUp className="w-3 h-3 text-lokiini-terracotta" /> Tendances au Maroc :
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

        {/* 3 Interactive Trust Pillars */}
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
                <p className="text-[11px] text-stone-500 mt-0.5 leading-snug">
                  Pré-autorisation bancaire bloquée temporairement, libérée dès restitution.
                </p>
              </div>
            </div>
          </div>

          {/* Pillar 2 : DOC Contracts */}
          <div className="bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-stone-200/90 shadow-sm hover:shadow-md hover:border-lokiini-teal/50 transition-all group">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-orange-50 flex items-center justify-center text-lokiini-terracotta shrink-0 group-hover:scale-110 transition-transform">
                <FileCheck className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-lokiini-charcoal flex items-center gap-1">
                  <span>Contrats DOC (Art. 627+)</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-lokiini-terracotta" />
                </div>
                <p className="text-[11px] text-stone-500 mt-0.5 leading-snug">
                  Baux conformes au droit marocain avec signature électronique légale (Loi 53-05).
                </p>
              </div>
            </div>
          </div>

          {/* Pillar 3 : CNDP Verification */}
          <div className="bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-stone-200/90 shadow-sm hover:shadow-md hover:border-lokiini-teal/50 transition-all group">
            <div className="flex items-center gap-3.5">
              <div className="w-11 h-11 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0 group-hover:scale-110 transition-transform">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <div className="text-xs font-bold text-lokiini-charcoal flex items-center gap-1">
                  <span>Vérification CNDP</span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                </div>
                <p className="text-[11px] text-stone-500 mt-0.5 leading-snug">
                  Identité vérifiée (CIN / ICE) et données protégées sous la Loi n° 09-08.
                </p>
              </div>
            </div>
          </div>

        </div>

      </div>
    </section>
  );
}
