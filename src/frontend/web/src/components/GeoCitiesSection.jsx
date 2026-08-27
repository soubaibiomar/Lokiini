import React from 'react';
import { MapPin, ArrowRight, ShieldCheck, Truck, Globe, Banknote } from 'lucide-react';

const MOROCCAN_REGIONS = [
  {
    city: 'Casablanca',
    region: 'Casablanca-Settat',
    desc: 'Grand Casablanca, Ain Sebaa, Maârif, Bourgogne, Bouskoura & Sidi Maarouf',
    count: '420+ articles disponibles',
    tag: 'Hub National'
  },
  {
    city: 'Rabat',
    region: 'Rabat-Salé-Kénitra',
    desc: 'Rabat Agdal, Souissi, Salé, Temara, Tamesna & Technopolis',
    count: '280+ articles disponibles',
    tag: 'Capitale & Services'
  },
  {
    city: 'Marrakech',
    region: 'Marrakech-Safi',
    desc: 'Guéliz, Hivernage, Sidi Ghanem, Palmeraie & Tamansourt',
    count: '195+ articles disponibles',
    tag: 'Événementiel & Audiovisuel'
  },
  {
    city: 'Tanger',
    region: 'Tanger-Tétouan-Al Hoceïma',
    desc: 'Tanger Ville, TFZ, Malabata, Gzenaya & Tétouan',
    count: '310+ articles disponibles',
    tag: 'Nord & Industrie'
  },
  {
    city: 'Agadir',
    region: 'Souss-Massa',
    desc: 'Agadir Baie, Dcheira, Inezgane, Taghazout & Aït Melloul',
    count: '145+ articles disponibles',
    tag: 'Souss & Outdoor'
  },
  {
    city: 'Fès',
    region: 'Fès-Meknès',
    desc: 'Fès Saïss, Sidi Brahim, Narjiss & Meknès Centre',
    count: '130+ articles disponibles',
    tag: 'Artisanat & Matériel'
  }
];

export default function GeoCitiesSection({ selectedCity, onSelectCity }) {
  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 border-t border-stone-200">
      
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold mb-3">
          <MapPin className="w-3.5 h-3.5" />
          <span>Couverture Géographique Nationale | Royaume du Maroc</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-black text-stone-900 font-['Outfit'] tracking-tight">
          Location Particuliers & Pros dans Toutes les Villes du Maroc
        </h2>
        <p className="text-stone-600 text-sm mt-3 leading-relaxed">
          Trouvez du matériel et des équipements vérifiés près de chez vous à Casablanca, Rabat, Marrakech, Tanger et dans tout le Maroc.
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
                  ? 'bg-emerald-50/80 border-emerald-700 shadow-md ring-2 ring-emerald-700/20'
                  : 'bg-white border-stone-200 hover:border-emerald-700 hover:shadow-lg'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-bold text-stone-900 group-hover:text-emerald-800 transition-colors flex items-center gap-1.5">
                    <span>{item.city}</span>
                    <span className="text-xs font-semibold text-stone-400 font-mono">({item.region})</span>
                  </h3>
                  <span className="text-[11px] font-semibold text-stone-500">{item.count}</span>
                </div>
                <span className="px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider rounded-lg bg-stone-100 text-stone-700 group-hover:bg-emerald-100 group-hover:text-emerald-800 transition-colors">
                  {item.tag}
                </span>
              </div>

              <p className="text-xs text-stone-600 mb-4 leading-relaxed line-clamp-2">
                {item.desc}
              </p>

              <div className="flex items-center justify-between pt-3 border-t border-stone-100 text-xs font-bold text-emerald-800">
                <span className="flex items-center gap-1">
                  <Truck className="w-3.5 h-3.5" />
                  Option Livraison Partenaire
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
          <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-800 font-bold mb-2">
            <Globe className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-stone-900">Ancrage 100% Marocain</h4>
          <p className="text-xs text-stone-500 mt-1">Conforme au Dahir des Obligations et Contrats (D.O.C) et Loi 53-05.</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-800 font-bold mb-2">
            <Banknote className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-stone-900">Paiement Cash on Delivery (COD)</h4>
          <p className="text-xs text-stone-500 mt-1">Paiement du montant et caution en espèces directement à la remise du matériel.</p>
        </div>

        <div className="flex flex-col items-center">
          <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-800 font-bold mb-2">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h4 className="text-sm font-bold text-stone-900">Protection CNDP (Loi 09-08)</h4>
          <p className="text-xs text-stone-500 mt-1">Identités vérifiées par Didit avec politique Zero-Knowledge et purge immédiate.</p>
        </div>
      </div>

    </section>
  );
}
