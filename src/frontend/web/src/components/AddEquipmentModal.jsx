import React, { useState } from 'react';
import { X, Plus, Sparkles, Image, ShieldCheck, CheckCircle2, AlertCircle } from 'lucide-react';
import { MOROCCAN_CITIES, CATEGORIES } from '../data/mockData';
import { createEquipment } from '../services/api';

const SAMPLE_IMAGES = [
  { label: 'Bétonnière Chantier', url: '/images/concrete_mixer.jpg' },
  { label: 'Mini-Pelle Bobcat', url: '/images/mini_excavator.jpg' },
  { label: 'Nettoyeur 180 Bar', url: '/images/pressure_washer.jpg' },
  { label: 'Caméra Sony FX3', url: '/images/sony_fx3.jpg' },
  { label: 'Groupe 10kVA', url: '/images/generator_10kva.jpg' },
  { label: 'Perforateur Démo', url: '/images/jackhammer.jpg' },
  { label: 'Échafaudage Alu', url: 'https://images.unsplash.com/photo-1541888946425-d0fbb186156a?w=800' },
  { label: 'Compacteur Sol', url: 'https://images.unsplash.com/photo-1581092335397-9583fe92d232?w=800' }
];

export default function AddEquipmentModal({ isOpen, onClose, onEquipmentAdded }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('btp');
  const [city, setCity] = useState('Casablanca');
  const [address, setAddress] = useState('');
  const [dailyPrice, setDailyPrice] = useState('');
  const [depositAmount, setDepositAmount] = useState('');
  const [discountPct, setDiscountPct] = useState('0');
  const [specKey1, setSpecKey1] = useState('Puissance');
  const [specVal1, setSpecVal1] = useState('');
  const [specKey2, setSpecKey2] = useState('Poids');
  const [specVal2, setSpecVal2] = useState('');
  const [selectedImage, setSelectedImage] = useState(SAMPLE_IMAGES[0].url);
  const [customImageUrl, setCustomImageUrl] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !description || !dailyPrice || !depositAmount) {
      setErrorMsg('Veuillez renseigner tous les champs obligatoires.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    const specs = {};
    if (specKey1 && specVal1) specs[specKey1] = specVal1;
    if (specKey2 && specVal2) specs[specKey2] = specVal2;

    const payload = {
      title,
      description,
      category,
      city,
      address: address || `${city}, Maroc`,
      daily_price_mad: parseFloat(dailyPrice),
      deposit_amount_mad: parseFloat(depositAmount),
      discount_pct: parseInt(discountPct) || 0,
      is_available: true,
      specs_json: specs,
      images_urls: [customImageUrl.trim() || selectedImage]
    };

    // Attempt API save
    const created = await createEquipment(payload);
    
    // In all cases, create local item for immediate UI reactivity
    const finalItem = created || {
      id: `local-${Date.now()}`,
      ...payload,
      rating: 5.0,
      reviews_count: 1,
      is_verified: true,
      image: payload.images_urls[0],
      specs
    };

    setIsSubmitting(false);
    setIsSuccess(true);

    setTimeout(() => {
      onEquipmentAdded(finalItem);
      onClose();
      setIsSuccess(false);
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-2xl w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100 mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center text-lokiini-teal font-black">
              <Plus className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-black text-xl text-lokiini-charcoal font-['Outfit']">Déposer une Annonce de Matériel</h3>
              <p className="text-xs text-stone-500">Mise en location sécurisée avec caution CMI séquestrée</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {isSuccess ? (
          <div className="py-12 text-center space-y-4">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h4 className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">Annonce Publiée avec Succès !</h4>
            <p className="text-sm text-stone-500 max-w-md mx-auto">
              Votre équipement est désormais visible sur toute la marketplace marocaine et prêt à recevoir des demandes de réservation.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {errorMsg && (
              <div className="bg-red-50 text-red-700 border border-red-200 rounded-xl p-3 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Title */}
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Titre de l'équipement *</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Ex: Compresseur Chantier 500L Mobile"
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-lokiini-teal"
                required
              />
            </div>

            {/* Category & City */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Catégorie *</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-lokiini-teal cursor-pointer"
                >
                  {CATEGORIES.filter(c => c.id !== 'all').map(c => (
                    <option key={c.id} value={c.id}>{c.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Ville Marocaine *</label>
                <select
                  value={city}
                  onChange={(e) => setCity(e.target.value)}
                  className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2.5 text-sm font-semibold text-stone-800 focus:outline-none focus:border-lokiini-teal cursor-pointer"
                >
                  {MOROCCAN_CITIES.filter(c => c !== 'Toutes les villes').map(c => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Address */}
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Adresse ou Quartier</label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Ex: Zone Industrielle Sidi Maarouf, Casablanca"
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-2.5 text-sm text-stone-800 focus:outline-none focus:border-lokiini-teal"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Description détaillée *</label>
              <textarea
                rows={3}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="État du matériel, accessoires inclus, conditions d'utilisation..."
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-2 text-sm text-stone-800 focus:outline-none focus:border-lokiini-teal"
                required
              />
            </div>

            {/* Pricing and Deposit Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 bg-stone-50 p-4 rounded-2xl border border-stone-200">
              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Prix Journalier (MAD) *</label>
                <input
                  type="number"
                  value={dailyPrice}
                  onChange={(e) => setDailyPrice(e.target.value)}
                  placeholder="Ex: 250"
                  className="w-full bg-white border border-stone-300 rounded-xl px-3.5 py-2 text-sm font-black text-lokiini-charcoal focus:outline-none focus:border-lokiini-teal"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Caution CMI (MAD) *</label>
                <input
                  type="number"
                  value={depositAmount}
                  onChange={(e) => setDepositAmount(e.target.value)}
                  placeholder="Ex: 2000"
                  className="w-full bg-white border border-stone-300 rounded-xl px-3.5 py-2 text-sm font-black text-lokiini-terracotta focus:outline-none focus:border-lokiini-teal"
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-stone-700 mb-1">Promo (%)</label>
                <input
                  type="number"
                  value={discountPct}
                  onChange={(e) => setDiscountPct(e.target.value)}
                  placeholder="Ex: 10"
                  className="w-full bg-white border border-stone-300 rounded-xl px-3.5 py-2 text-sm font-semibold text-stone-800 focus:outline-none focus:border-lokiini-teal"
                />
              </div>
            </div>

            {/* Custom Specs */}
            <div className="grid grid-cols-2 gap-3">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={specKey1}
                  onChange={(e) => setSpecKey1(e.target.value)}
                  placeholder="Spéc. 1"
                  className="w-1/2 bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-bold text-stone-600"
                />
                <input
                  type="text"
                  value={specVal1}
                  onChange={(e) => setSpecVal1(e.target.value)}
                  placeholder="Ex: 1500W"
                  className="w-1/2 bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-semibold text-stone-800"
                />
              </div>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={specKey2}
                  onChange={(e) => setSpecKey2(e.target.value)}
                  placeholder="Spéc. 2"
                  className="w-1/2 bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-bold text-stone-600"
                />
                <input
                  type="text"
                  value={specVal2}
                  onChange={(e) => setSpecVal2(e.target.value)}
                  placeholder="Ex: 50 kg"
                  className="w-1/2 bg-stone-50 border border-stone-300 rounded-xl px-3 py-2 text-xs font-semibold text-stone-800"
                />
              </div>
            </div>

            {/* Image Selection */}
            <div>
              <label className="block text-xs font-bold text-stone-700 mb-2">Illustration du matériel</label>
              <div className="grid grid-cols-4 sm:grid-cols-8 gap-2 mb-3">
                {SAMPLE_IMAGES.map((img, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => { setSelectedImage(img.url); setCustomImageUrl(''); }}
                    className={`h-12 rounded-xl overflow-hidden border-2 transition-all ${
                      selectedImage === img.url && !customImageUrl
                        ? 'border-lokiini-teal ring-2 ring-lokiini-teal/30 scale-105'
                        : 'border-stone-200 opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={img.url} alt={img.label} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
              <input
                type="url"
                value={customImageUrl}
                onChange={(e) => setCustomImageUrl(e.target.value)}
                placeholder="Ou collez une URL d'image personnalisée (https://...)"
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-3.5 py-2 text-xs text-stone-800 focus:outline-none focus:border-lokiini-teal"
              />
            </div>

            {/* Submit Button */}
            <div className="pt-4 border-t border-stone-200 flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="w-1/3 py-3 rounded-xl border border-stone-300 text-stone-700 font-bold text-xs hover:bg-stone-50 transition-colors"
              >
                Annuler
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-2/3 bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs flex items-center justify-center gap-2"
              >
                {isSubmitting ? (
                  <span>Publication en cours...</span>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    <span>Publier l'Annonce Sécurisée</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}

      </div>
    </div>
  );
}
