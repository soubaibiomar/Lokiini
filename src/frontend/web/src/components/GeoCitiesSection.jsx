import React from 'react';
import { MapPin, ArrowRight, ShieldCheck, Truck } from 'lucide-react';

const MOROCCAN_REGIONS = [
  {
    city: 'Casablanca',
    region: 'Casablanca-Settat',
    desc: 'Grand Casablanca, Ain Sebaa, Anfa, Maârif, Mohammedia & Bouskoura',
    count: '540+ matériels & équipements',
    tag: 'Hub National Universel'
  },
  {
    city: 'Rabat',
    region: 'Rabat-Salé-Kénitra',
    desc: 'Agdal, Souissi, Technopolis, Salé, Temara & Tamesna',
    count: '380+ matériels & équipements',
    tag: 'Événements & High-Tech'
  },
  {
    city: 'Marrakech',
    region: 'Marrakech-Safi',
    desc: 'Guéliz, Hivernage, Palmeraie, Sidi Ghanem & Désert d\'Agafay',
    count: '320+ matériels & équipements',
    tag: 'Tournages, Fêtes & Loisirs'
  },
  {
    city: 'Tanger',
    region: 'Tanger-Tétouan-Al Hoceïma',
    desc: 'Tanger Ville, TFZ, Malabata, Gzenaya & Tétouan',
    count: '360+ matériels & équipements',
    tag: 'Industrie, Drones & Pro'
  },
  {
    city: 'Agadir',
    region: 'Souss-Massa',
    desc: 'Agadir Baie, Taghazout, Dcheira, Inezgane & Aït Melloul',
    count: '210+ matériels & équipements',
    tag: 'Loisirs, Sport & Outillage'
  },
  {
    city: 'Fès',
    region: 'Fès-Meknès',
    desc: 'Fès Ville Nouvelle, Sidi Brahim, Narjiss & Meknès',
    count: '180+ matériels & équipements',
    tag: 'Artisanat, Fêtes & Matériel'
  }
];

export default function GeoCitiesSection({ selectedCity, onSelectCity }) {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-stone-200">
      
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-50 border border-teal-200 text-lokiini-teal text-xs font-bold mb-3">
          <MapPin className="w-3.5 h-3.5" />
          <span>Couverture Géographique Nationale — Royaume du Maroc</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-black text-lokiini-charcoal font-['Outfit'] tracking-tight">
          Location de Matériel & Équipements dans Toutes les Régions
        </h2>
        <p className="text-stone-600 text-sm mt-3 leading-relaxed">
          Trouvez des équipements vérifiés près de chez vous à Casablanca, Rabat, Marrakech, Tanger et dans plus de 30 villes marocaines avec livraison rapide ou retrait direct en main propre.
        </p>
      </div>

      {/* Grid of Moroccan Hubs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {MOROCCAN_REGIONS.map((item) => {
          const isSelected = selectedCity === item.city;
          return (
            <div
              key={item.city}
              onClick={() => onSelectCity(item.city)}
              className={`group cursor-pointer rounded-2xl p-6 transition-all border ${
                isSelected
                  ? 'bg-emerald-50/80 border-lokiini-teal shadow-md ring-2 ring-lokiini-teal/20'
                  : 'bg-white border-stone-200 hover:border-lokiini-teal hover:shadow-lg'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-black text-stone-900 group-hover:text-lokiini-teal transition-colors flex items-center gap-1.5">
                    <span>{item.city}</span>
                    <span className="text-xs font-bold text-stone-400 font-mono">({item.region})</span>
                  </h3>
                  <span className="text-[11px] font-semibold text-stone-500">{item.count}</span>
                </div>
                <span className="px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wider rounded-lg bg-stone-100 text-stone-700 group-hover:bg-teal-100 group-hover:text-teal-800 transition-colors">
                  {item.tag}
                </span>
              </div>

              <p className="text-xs text-stone-600 mb-4 leading-relaxed line-clamp-2">
                {item.desc}
              </p>

              <div className="flex items-center justify-between pt-3 border-t border-stone-100 text-xs font-bold text-lokiini-teal">
                <span className="flex items-center gap-1">
                  <Truck className="w-3.5 h-3.5" />
                  Livraison & Retrait Disponibles
                </span>
                <span className="flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                  Explorer
                  <ArrowRight className="w-3.5 h-3.5" />
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Moroccan Legal & Guarantee Trust Bar */}
      <div className="mt-12 bg-white rounded-2xl p-6 border border-stone-200 shadow-sm grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
        <div className="flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center text-lokiini-teal font-bold mb-2">
            🇲🇦
          </div>
          <h4 className="text-sm font-bold text-stone-900">Ancrage 100% Marocain</h4>
          <p className="text-xs text-stone-500 mt-1">Conforme au D.O.C (Dahir des Obligations et Contrats) et Loi 53-05.</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-amber-700 font-bold mb-2">
            💳
          </div>
          <h4 className="text-sm font-bold text-stone-900">Séquestre CMI Sans Débit</h4>
          <p className="text-xs text-stone-500 mt-1">Cautions retenues sur empreinte bancaire marocaine sans impacter votre trésorerie.</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-700 font-bold mb-2">
            🛡️
          </div>
          <h4 className="text-sm font-bold text-stone-900">Protection CNDP (Loi 09-08)</h4>
          <p className="text-xs text-stone-500 mt-1">Identités vérifiées par biométrie vivante avec purge immédiate des flux.</p>
        </div>
      </div>

    </section>
  );
}
