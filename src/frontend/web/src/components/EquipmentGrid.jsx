import React from 'react';
import { MapPin, ShieldCheck, Star, Sparkles } from 'lucide-react';

export default function EquipmentGrid({ equipmentList, onSelectEquipment }) {
  if (equipmentList.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="w-16 h-16 bg-stone-200 rounded-full flex items-center justify-center mx-auto mb-4 text-stone-500">
          <MapPin className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-bold text-stone-700">Aucun matériel trouvé dans cette ville</h3>
        <p className="text-sm text-stone-500 mt-1">Essayez de sélectionner « Toutes les villes » ou une autre catégorie.</p>
      </div>
    );
  }

  return (
    <section id="catalogue-grid" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 scroll-mt-24">
      
      {/* Section Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl sm:text-3xl font-black text-lokiini-charcoal font-['Outfit']">
            Équipements Disponibles à la Location
          </h2>
          <p className="text-sm text-stone-500 mt-1">
            Matériel professionnel révisé, assuré et prêt pour vos chantiers et projets au Maroc.
          </p>
        </div>
        <div className="hidden sm:flex items-center gap-2 text-xs font-bold text-stone-500 bg-white px-3 py-1.5 rounded-lg border border-stone-200">
          <span>{equipmentList.length} machines listées</span>
        </div>
      </div>

      {/* Equipment Cards Grid (matching mockup cards) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {equipmentList.map((item) => (
          <div
            key={item.id}
            className="bg-white rounded-2xl overflow-hidden border border-stone-200/90 shadow-sm hover:shadow-md transition-all duration-300 flex flex-col group"
          >
            {/* Image Container with Badges */}
            <div className="relative h-48 bg-stone-100 overflow-hidden">
              <img
                src={item.image}
                alt={item.title}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              
              {/* Promo Badge */}
              {item.discount_pct > 0 && (
                <div className="absolute top-3 right-3 bg-amber-700/90 backdrop-blur-md text-amber-100 text-[11px] font-black px-2.5 py-1 rounded-lg shadow-sm flex items-center gap-1">
                  <Sparkles className="w-3 h-3" />
                  <span>PROMO -{item.discount_pct}%</span>
                </div>
              )}

              {/* City Tag */}
              <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md text-white text-[11px] font-medium px-2.5 py-0.5 rounded-md flex items-center gap-1">
                <MapPin className="w-3 h-3 text-lokiini-terracotta" />
                <span>{item.city}</span>
              </div>
            </div>

            {/* Content Body */}
            <div className="p-4 flex-1 flex flex-col justify-between">
              <div>
                {/* Title */}
                <h3 className="font-bold text-sm text-lokiini-charcoal line-clamp-2 leading-snug group-hover:text-lokiini-teal transition-colors">
                  {item.title}
                </h3>

                {/* Rating & Verified Badge */}
                <div className="flex items-center justify-between mt-2.5">
                  <div className="flex items-center gap-1 text-xs font-bold text-stone-700">
                    <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
                    <span>{item.rating}</span>
                    <span className="text-stone-400 font-normal">({item.reviews_count})</span>
                  </div>

                  {item.is_verified && (
                    <div className="flex items-center gap-1 text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                      <ShieldCheck className="w-3 h-3" />
                      <span>Vérifié</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Price & Actions */}
              <div className="mt-4 pt-3 border-t border-stone-100">
                <div className="flex items-baseline justify-between mb-3">
                  <div>
                    <span className="text-xs text-stone-400">À partir de</span>
                    <div className="text-lg font-black text-lokiini-charcoal font-['Outfit']">
                      {item.daily_price_mad} <span className="text-xs font-bold text-lokiini-teal">MAD / jour</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-[10px] text-stone-400 block">Caution CMI</span>
                    <span className="text-xs font-bold text-stone-600">{item.deposit_amount_mad} MAD</span>
                  </div>
                </div>

                {/* Card Buttons matching mockup */}
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => onSelectEquipment(item, 'details')}
                    className="w-full text-xs font-bold py-2 px-3 rounded-xl border border-stone-300 text-stone-700 hover:bg-stone-50 transition-colors"
                  >
                    Détails
                  </button>
                  <button
                    onClick={() => onSelectEquipment(item, 'book')}
                    className="w-full text-xs font-bold py-2 px-3 rounded-xl bg-lokiini-teal hover:bg-lokiini-teal-dark text-white shadow-sm hover:shadow transition-all"
                  >
                    Réserver
                  </button>
                </div>

              </div>
            </div>

          </div>
        ))}
      </div>

    </section>
  );
}
