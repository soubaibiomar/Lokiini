import React, { useState, useMemo } from 'react';
import { 
  X, Calendar, ShieldCheck, Banknote, CheckCircle2, AlertCircle, 
  FileText, Truck, MapPin, User, Star, Clock, Check
} from 'lucide-react';
import { createBooking } from '../services/api';

export default function EquipmentModal({ 
  equipment, 
  onClose, 
  initialMode = 'details', 
  isKYCVerified, 
  onOpenKYC,
  onBookingSuccess,
  onOpenContract,
  onOpenInspection
}) {
  const [mode, setMode] = useState(initialMode); // 'details' or 'book'
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(
    new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  );
  const [deliveryOption, setDeliveryOption] = useState('retrait_sur_place'); // 'retrait_sur_place' | 'livraison_premium'
  const [contractAccepted, setContractAccepted] = useState(true);
  const [isBookingSuccess, setIsBookingSuccess] = useState(false);
  const [bookingRecord, setBookingRecord] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Price & Caution Calculations
  const calculations = useMemo(() => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.max(end - start, 0);
    const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    let discountPct = 0;
    if (days >= 30) discountPct = 30;
    else if (days >= 7) discountPct = 15;
    else if (days >= 3) discountPct = 5;

    const basePrice = equipment.daily_price_mad || equipment.prix_par_jour || 120;
    const discountedRate = basePrice * (1 - discountPct / 100);
    const subtotal = Math.round(discountedRate * days);
    const deposit = equipment.deposit_amount_mad || equipment.montant_caution || basePrice * 8;
    const deliveryFee = deliveryOption === 'livraison_premium' ? 49 : 0;

    return {
      days,
      discountPct,
      discountedRate,
      subtotal,
      deliveryFee,
      totalToPay: subtotal + deliveryFee,
      deposit
    };
  }, [startDate, endDate, equipment, deliveryOption]);

  const handleConfirmBooking = async () => {
    // If high-risk article and not verified, trigger KYC
    if (equipment.niveau_risque === 'eleve' && !isKYCVerified) {
      onOpenKYC();
      return;
    }

    setIsSubmitting(true);

    const apiBooking = await createBooking(equipment.id, startDate, endDate);
    
    const finalBooking = apiBooking || {
      id: `LK-${Date.now().toString().slice(-6)}`,
      equipment_id: equipment.id,
      equipment_title: equipment.title || equipment.titre,
      start_date: startDate,
      end_date: endDate,
      total_days: calculations.days,
      rental_total_mad: calculations.totalToPay,
      deposit_hold_mad: calculations.deposit,
      option_livraison: deliveryOption,
      statut: 'confirme_cod',
      contrat_signe: contractAccepted
    };

    setBookingRecord(finalBooking);
    setIsSubmitting(false);
    setIsBookingSuccess(true);

    if (onBookingSuccess) {
      onBookingSuccess(finalBooking);
    }
  };

  if (isBookingSuccess && bookingRecord) {
    return (
      <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 text-center shadow-2xl border border-stone-200">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 text-emerald-700">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          
          <h3 className="text-2xl font-bold text-stone-900 mb-1">Demande de Location Confirmée</h3>
          <p className="text-xs text-stone-500">
            Référence : <span className="font-bold text-emerald-800 font-mono">LK-{String(bookingRecord.id).substring(0, 8).toUpperCase()}</span>
          </p>

          {/* Cash Summary Card */}
          <div className="bg-stone-50 rounded-2xl p-4 my-5 text-left text-xs space-y-2.5 border border-stone-200">
            <div className="flex justify-between pb-2 border-b border-stone-200 font-medium">
              <span className="text-stone-600">Matériel :</span>
              <span className="font-bold text-stone-900">{equipment.title || equipment.titre}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-600">Période :</span>
              <span className="font-bold text-stone-800">{calculations.days} jours ({startDate} au {endDate})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-600">Mode de remise :</span>
              <span className="font-bold text-stone-800">
                {deliveryOption === 'retrait_sur_place' ? 'Retrait sur place (Gratuit)' : 'Livraison Partenaire (49 MAD)'}
              </span>
            </div>

            {/* Cash on Delivery Callout */}
            <div className="bg-emerald-50 rounded-xl p-3 border border-emerald-200 mt-2">
              <div className="flex items-center gap-1.5 font-bold text-emerald-900 text-xs mb-1">
                <Banknote className="w-4 h-4 text-emerald-700 shrink-0" />
                <span>Montant en espèces à apporter à la remise :</span>
              </div>
              <div className="flex justify-between text-xs pt-1 border-t border-emerald-200/60">
                <span className="text-emerald-800">Prix location :</span>
                <span className="font-bold text-emerald-950">{calculations.totalToPay} MAD</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-emerald-800">Caution cash (restituée au retour) :</span>
                <span className="font-bold text-emerald-950">{calculations.deposit} MAD</span>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 gap-2.5 mb-4">
            <button
              onClick={() => {
                if (onOpenContract) onOpenContract(bookingRecord.id, bookingRecord);
              }}
              className="py-2.5 px-3 rounded-xl border border-stone-300 text-stone-700 font-bold text-xs hover:bg-stone-50 flex items-center justify-center gap-1.5 transition-colors"
            >
              <FileText className="w-4 h-4 text-emerald-800" />
              <span>Contrat de Bail</span>
            </button>

            <button
              onClick={() => {
                if (onOpenInspection) onOpenInspection(bookingRecord, 'check_in');
              }}
              className="py-2.5 px-3 rounded-xl bg-emerald-50 text-emerald-800 font-bold text-xs border border-emerald-200 hover:bg-emerald-100 flex items-center justify-center gap-1.5 transition-colors"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>Préparer État des Lieux</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="w-full bg-emerald-800 hover:bg-emerald-900 text-white font-bold py-3 rounded-xl transition-all shadow text-xs"
          >
            Fermer & Retour au Catalogue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-2xl w-full overflow-hidden shadow-2xl border border-stone-200 my-8">
        
        {/* Header Image */}
        <div className="relative h-60 bg-stone-900">
          <img
            src={equipment.image || equipment.photos?.[0] || '/images/default_tool.jpg'}
            alt={equipment.title || equipment.titre}
            className="w-full h-full object-cover opacity-90"
          />
          <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-black/50 hover:bg-black/80 text-white w-9 h-9 rounded-full flex items-center justify-center backdrop-blur-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="absolute bottom-4 left-6 right-6 text-white">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider bg-emerald-800 px-2.5 py-0.5 rounded-md">
                {(equipment.category || equipment.categorie || 'Outils').toUpperCase()}
              </span>
              <span className="text-[11px] bg-black/40 backdrop-blur-md px-2 py-0.5 rounded-md flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {equipment.city || equipment.ville || 'Casablanca'}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold leading-tight">{equipment.title || equipment.titre}</h2>
          </div>
        </div>

        {/* Modal Content */}
        <div className="p-6 sm:p-8">
          
          {/* Navigation Tabs */}
          <div className="flex border-b border-stone-200 mb-6">
            <button
              onClick={() => setMode('details')}
              className={`pb-3 text-sm font-bold transition-colors mr-6 ${
                mode === 'details'
                  ? 'border-b-2 border-emerald-800 text-emerald-800'
                  : 'text-stone-400 hover:text-stone-600'
              }`}
            >
              Fiche Technique & Loueur
            </button>
            <button
              onClick={() => setMode('book')}
              className={`pb-3 text-sm font-bold transition-colors ${
                mode === 'book'
                  ? 'border-b-2 border-emerald-800 text-emerald-800'
                  : 'text-stone-400 hover:text-stone-600'
              }`}
            >
              Réserver en Paiement Cash (COD)
            </button>
          </div>

          {mode === 'details' ? (
            <div>
              <p className="text-sm text-stone-600 leading-relaxed mb-6">
                {equipment.description}
              </p>

              {/* Owner Info Card */}
              <div className="bg-stone-50 rounded-2xl p-4 border border-stone-200 mb-6">
                <div className="text-xs font-bold uppercase tracking-wider text-stone-400 mb-2">Profil du Loueur</div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold text-sm">
                      <User className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="font-bold text-stone-900 text-sm flex items-center gap-1.5">
                        <span>{equipment.owner_name || equipment.loueur?.nom || 'Atlas Location BTP Maroc'}</span>
                        <span className="inline-flex items-center gap-0.5 px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                          <ShieldCheck className="w-3 h-3" /> Vérifié Didit
                        </span>
                      </div>
                      <div className="text-xs text-stone-500 flex items-center gap-3 mt-0.5">
                        <span className="flex items-center gap-1 text-amber-700 font-bold">
                          <Star className="w-3.5 h-3.5 fill-amber-500" /> {equipment.rating || 4.95} (34 avis)
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5 text-stone-400" /> Réponse en &lt; 15 min
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Specifications */}
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-400 mb-3">Spécifications Matériel</h4>
              <div className="grid grid-cols-2 gap-3 mb-6">
                {Object.entries(equipment.specs || equipment.specs_json || {}).map(([key, val]) => (
                  <div key={key} className="bg-stone-50 p-3 rounded-xl border border-stone-200 text-xs">
                    <span className="text-stone-400 block">{key}</span>
                    <span className="font-bold text-stone-800">{String(val)}</span>
                  </div>
                ))}
              </div>

              {/* Sticky Price & Action Bar */}
              <div className="flex items-center justify-between pt-4 border-t border-stone-200">
                <div>
                  <span className="text-xs text-stone-500">Tarif journalier</span>
                  <div className="text-2xl font-bold text-stone-900">
                    {equipment.daily_price_mad || equipment.prix_par_jour || 120} <span className="text-xs font-bold text-emerald-800">MAD / jour</span>
                  </div>
                  <div className="text-[11px] text-stone-500">
                    Caution cash : {equipment.deposit_amount_mad || equipment.montant_caution || 1000} MAD
                  </div>
                </div>
                <button
                  onClick={() => setMode('book')}
                  className="bg-emerald-800 hover:bg-emerald-900 text-white font-bold text-sm px-6 py-3 rounded-xl transition-all shadow"
                >
                  Réserver maintenant
                </button>
              </div>
            </div>
          ) : (
            <div>
              {/* Date Selection */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-xs font-bold text-stone-600 mb-1">Date de début</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-emerald-800"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-stone-600 mb-1">Date de fin</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-emerald-800"
                  />
                </div>
              </div>

              {/* Delivery Options */}
              <div className="mb-4">
                <label className="block text-xs font-bold text-stone-600 mb-1.5">Option de remise</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <button
                    type="button"
                    onClick={() => setDeliveryOption('retrait_sur_place')}
                    className={`p-3 rounded-xl border text-left flex items-start gap-2.5 transition-colors ${
                      deliveryOption === 'retrait_sur_place'
                        ? 'border-emerald-800 bg-emerald-50 text-emerald-900'
                        : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-stone-100'
                    }`}
                  >
                    <MapPin className="w-4 h-4 mt-0.5 text-emerald-800 shrink-0" />
                    <div>
                      <div className="font-bold text-xs">Retrait sur place</div>
                      <div className="text-[11px] text-stone-500">Gratuit ({equipment.address || 'Casablanca'})</div>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => setDeliveryOption('livraison_premium')}
                    className={`p-3 rounded-xl border text-left flex items-start gap-2.5 transition-colors ${
                      deliveryOption === 'livraison_premium'
                        ? 'border-emerald-800 bg-emerald-50 text-emerald-900'
                        : 'border-stone-200 bg-stone-50 text-stone-700 hover:bg-stone-100'
                    }`}
                  >
                    <Truck className="w-4 h-4 mt-0.5 text-emerald-800 shrink-0" />
                    <div>
                      <div className="font-bold text-xs">Livraison Partenaire</div>
                      <div className="text-[11px] text-stone-500">+49 MAD (Coursier express)</div>
                    </div>
                  </button>
                </div>
              </div>

              {/* Price Calculation Summary */}
              <div className="bg-stone-50 rounded-2xl p-4 border border-stone-200 mb-4 space-y-2.5">
                <div className="flex justify-between text-xs text-stone-600">
                  <span>Durée :</span>
                  <span className="font-bold text-stone-900">{calculations.days} jour(s)</span>
                </div>

                {calculations.discountPct > 0 && (
                  <div className="flex justify-between text-xs text-emerald-800 bg-emerald-100/70 px-2 py-1 rounded-lg">
                    <span>Remise de durée appliquée :</span>
                    <span className="font-bold">-{calculations.discountPct}%</span>
                  </div>
                )}

                <div className="flex justify-between text-sm font-bold pt-2 border-t border-stone-200 text-stone-900">
                  <span>Montant de la location :</span>
                  <span className="text-emerald-800 font-bold text-base">{calculations.totalToPay} MAD</span>
                </div>

                {/* COD Caution Box */}
                <div className="bg-white p-3 rounded-xl border border-stone-200 text-xs space-y-1">
                  <div className="flex items-center justify-between font-bold text-stone-800">
                    <span className="flex items-center gap-1.5">
                      <Banknote className="w-4 h-4 text-emerald-700" />
                      Caution en espèces requise :
                    </span>
                    <span className="text-emerald-800 font-bold">{calculations.deposit} MAD</span>
                  </div>
                  <p className="text-[11px] text-stone-500 leading-snug">
                    Paiement à la livraison (COD). La caution est remise en cash au loueur lors de la remise et restituée intégralement au retour après validation de l état des lieux.
                  </p>
                </div>
              </div>

              {/* Digital Contract Checkbox */}
              <div className="flex items-start gap-2.5 mb-5 text-xs text-stone-600">
                <input
                  type="checkbox"
                  id="contract-agree"
                  checked={contractAccepted}
                  onChange={(e) => setContractAccepted(e.target.checked)}
                  className="mt-0.5 rounded border-stone-300 text-emerald-800 focus:ring-emerald-800"
                />
                <label htmlFor="contract-agree" className="cursor-pointer leading-snug">
                  J accepte les conditions du contrat de bail numérique (Dahir des Obligations et Contrats &amp; Loi 53-05) et m engage à respecter le protocole d état des lieux.
                </label>
              </div>

              {/* Submit CTA */}
              <button
                disabled={isSubmitting || !contractAccepted}
                onClick={handleConfirmBooking}
                className="w-full bg-emerald-800 hover:bg-emerald-900 disabled:opacity-50 text-white font-bold py-3.5 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-sm"
              >
                {isSubmitting ? (
                  <span>Enregistrement de la réservation...</span>
                ) : (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Confirmer la Réservation COD ({calculations.totalToPay} MAD)</span>
                  </>
                )}
              </button>
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
