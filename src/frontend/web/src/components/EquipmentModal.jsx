import React, { useState, useMemo } from 'react';
import { X, Calendar, Shield, CreditCard, CheckCircle2, AlertCircle, FileText, Lock, Video } from 'lucide-react';
import { createBooking, calculatePricing } from '../services/api';

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
    if (days >= 30) discountPct = 50;
    else if (days >= 7) discountPct = 30;
    else if (days >= 3) discountPct = 15;

    const basePrice = equipment.daily_price_mad;
    const discountedRate = basePrice * (1 - discountPct / 100);
    const subtotal = Math.round(discountedRate * days);
    const deposit = equipment.deposit_amount_mad;

    return {
      days,
      discountPct,
      discountedRate,
      subtotal,
      deposit
    };
  }, [startDate, endDate, equipment]);

  const handleConfirmBooking = async () => {
    if (!isKYCVerified) {
      onOpenKYC();
      return;
    }

    setIsSubmitting(true);

    // Call API with fallback
    const apiBooking = await createBooking(equipment.id, startDate, endDate);
    
    const finalBooking = apiBooking || {
      id: `local-b-${Date.now()}`,
      equipment_id: equipment.id,
      equipment_title: equipment.title,
      start_date: startDate,
      end_date: endDate,
      total_days: calculations.days,
      rental_total_mad: calculations.subtotal,
      deposit_hold_mad: calculations.deposit,
      booking_status: 'confirmed',
      cmi_status: 'held',
      cmi_auth_token: `CMI_AUTH_${Math.random().toString(36).substring(2, 10).toUpperCase()}`
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
        <div className="bg-white rounded-3xl max-w-lg w-full p-8 text-center shadow-2xl animate-in fade-in zoom-in duration-300">
          <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 text-emerald-600">
            <CheckCircle2 className="w-10 h-10" />
          </div>
          
          <h3 className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">Réservation Confirmée !</h3>
          <p className="text-xs text-stone-500 mt-1">
            Réf. Contrat : <span className="font-bold text-lokiini-teal font-mono">LK-{String(bookingRecord.id).substring(0, 8).toUpperCase()}</span>
          </p>

          {/* Details Card */}
          <div className="bg-stone-50 rounded-2xl p-4 my-5 text-left text-xs space-y-2 border border-stone-200">
            <div className="flex justify-between">
              <span className="text-stone-500">Matériel :</span>
              <span className="font-bold text-stone-800">{equipment.title}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-500">Période :</span>
              <span className="font-bold text-stone-800">{calculations.days} jours ({startDate} ➔ {endDate})</span>
            </div>
            <div className="flex justify-between">
              <span className="text-stone-500">Total Location TTC :</span>
              <span className="font-black text-lokiini-teal">{calculations.subtotal} MAD</span>
            </div>
            <div className="flex justify-between border-t border-stone-200 pt-2 text-emerald-700">
              <span className="font-semibold">Empreinte Caution CMI :</span>
              <span className="font-bold">{calculations.deposit} MAD (Bloqué, non débité)</span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="grid grid-cols-2 gap-2.5 mb-4">
            <button
              onClick={() => {
                if (onOpenContract) onOpenContract(bookingRecord.id, bookingRecord);
              }}
              className="py-2.5 px-3 rounded-xl border border-stone-300 text-stone-700 font-bold text-xs hover:bg-stone-50 flex items-center justify-center gap-1.5 transition-colors"
            >
              <FileText className="w-4 h-4 text-lokiini-teal" />
              <span>Voir Contrat DOC</span>
            </button>

            <button
              onClick={() => {
                if (onOpenInspection) onOpenInspection(bookingRecord, 'check_in');
              }}
              className="py-2.5 px-3 rounded-xl bg-teal-50 text-lokiini-teal font-bold text-xs border border-teal-200 hover:bg-teal-100 flex items-center justify-center gap-1.5 transition-colors"
            >
              <Video className="w-4 h-4" />
              <span>Check-in Vidéo</span>
            </button>
          </div>

          <button
            onClick={onClose}
            className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs"
          >
            Terminer & Retour au Catalogue
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-2xl w-full overflow-hidden shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8">
        
        {/* Modal Header */}
        <div className="relative h-64 bg-stone-900">
          <img
            src={equipment.image}
            alt={equipment.title}
            className="w-full h-full object-cover opacity-85"
          />
          <button
            onClick={onClose}
            className="absolute top-4 right-4 bg-black/50 hover:bg-black/80 text-white w-9 h-9 rounded-full flex items-center justify-center backdrop-blur-md transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          <div className="absolute bottom-4 left-6 right-6 text-white">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-[11px] font-bold uppercase tracking-wider bg-lokiini-teal px-2.5 py-0.5 rounded-md">
                {equipment.category.toUpperCase()}
              </span>
              <span className="text-[11px] bg-white/30 backdrop-blur-md px-2 py-0.5 rounded-md">
                {equipment.city}
              </span>
            </div>
            <h2 className="text-xl sm:text-2xl font-black font-['Outfit'] leading-tight">{equipment.title}</h2>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 sm:p-8">
          
          {/* Tabs */}
          <div className="flex border-b border-stone-200 mb-6">
            <button
              onClick={() => setMode('details')}
              className={`pb-3 text-sm font-bold transition-colors mr-6 ${
                mode === 'details'
                  ? 'border-b-2 border-lokiini-teal text-lokiini-teal'
                  : 'text-stone-400 hover:text-stone-600'
              }`}
            >
              Fiche Technique
            </button>
            <button
              onClick={() => setMode('book')}
              className={`pb-3 text-sm font-bold transition-colors ${
                mode === 'book'
                  ? 'border-b-2 border-lokiini-teal text-lokiini-teal'
                  : 'text-stone-400 hover:text-stone-600'
              }`}
            >
              Réserver & Bloquer la Caution CMI
            </button>
          </div>

          {mode === 'details' ? (
            <div>
              <p className="text-sm text-stone-600 leading-relaxed mb-6">
                {equipment.description}
              </p>

              {/* Specs Grid */}
              <h4 className="text-xs font-bold uppercase tracking-wider text-stone-400 mb-3">Spécifications</h4>
              <div className="grid grid-cols-2 gap-3 mb-6">
                {Object.entries(equipment.specs || equipment.specs_json || {}).map(([key, val]) => (
                  <div key={key} className="bg-stone-50 p-3 rounded-xl border border-stone-200 text-xs">
                    <span className="text-stone-400 block">{key}</span>
                    <span className="font-bold text-stone-800">{String(val)}</span>
                  </div>
                ))}
              </div>

              {/* Pricing & Booking CTA */}
              <div className="flex items-center justify-between pt-4 border-t border-stone-200">
                <div>
                  <span className="text-xs text-stone-400">Tarif journalier</span>
                  <div className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">
                    {equipment.daily_price_mad} <span className="text-xs font-bold text-lokiini-teal">MAD / jour</span>
                  </div>
                </div>
                <button
                  onClick={() => setMode('book')}
                  className="bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold text-sm px-6 py-3 rounded-xl transition-all shadow"
                >
                  Configurer ma location
                </button>
              </div>
            </div>
          ) : (
            <div>
              {/* Date Pickers */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block text-xs font-bold text-stone-600 mb-1">Date de début</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-lokiini-teal"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-stone-600 mb-1">Date de fin</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-lokiini-teal"
                  />
                </div>
              </div>

              {/* Calculation Summary Box */}
              <div className="bg-stone-50 rounded-2xl p-5 border border-stone-200 mb-6 space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="text-stone-600">Durée sélectionnée :</span>
                  <span className="font-bold text-stone-800">{calculations.days} jour(s)</span>
                </div>

                {calculations.discountPct > 0 && (
                  <div className="flex justify-between text-xs text-amber-700 bg-amber-50 p-2 rounded-lg border border-amber-200">
                    <span>Remise dégressive appliquée :</span>
                    <span className="font-bold">-{calculations.discountPct}%</span>
                  </div>
                )}

                <div className="flex justify-between text-sm font-bold pt-2 border-t border-stone-200 text-lokiini-charcoal">
                  <span>Total Location (TTC) :</span>
                  <span className="text-lokiini-teal font-black text-base">{calculations.subtotal} MAD</span>
                </div>

                {/* CMI Caution Detail */}
                <div className="bg-white p-3.5 rounded-xl border border-stone-200 space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-bold text-stone-800 flex items-center gap-1.5">
                      <CreditCard className="w-4 h-4 text-lokiini-terracotta" />
                      Empreinte Caution CMI :
                    </span>
                    <span className="font-black text-lokiini-terracotta">{calculations.deposit} MAD</span>
                  </div>
                  <p className="text-[11px] text-stone-500">
                    ℹ️ Ce montant est bloqué temporairement sur votre plafond bancaire. <span className="font-bold">Il n'est pas débité de votre compte</span> et sera libéré instantanément dès le check-out de restitution validé.
                  </p>
                </div>
              </div>

              {/* KYC Warning if not verified */}
              {!isKYCVerified && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-xs text-amber-800 flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-amber-600 shrink-0" />
                    <span>Vérification CIN obligatoire avant confirmation</span>
                  </div>
                  <button
                    onClick={onOpenKYC}
                    className="font-bold text-amber-900 underline hover:text-black"
                  >
                    Vérifier maintenant
                  </button>
                </div>
              )}

              {/* Submit Button */}
              <button
                disabled={isSubmitting}
                onClick={handleConfirmBooking}
                className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3.5 rounded-xl transition-all shadow-md flex items-center justify-center gap-2 text-sm"
              >
                {isSubmitting ? (
                  <span>Pré-autorisation CMI 3D-Secure en cours...</span>
                ) : (
                  <>
                    <Lock className="w-4 h-4" />
                    <span>Confirmer & Bloquer l'Empreinte CMI ({calculations.deposit} MAD)</span>
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
