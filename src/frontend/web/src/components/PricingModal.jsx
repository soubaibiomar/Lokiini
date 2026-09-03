import React from 'react';
import { X, Check, ShieldCheck, Zap, Sparkles, Building2, User } from 'lucide-react';

const PRICING_PLANS = [
  {
    id: 'gratuit',
    name: 'Gratuit (Découverte)',
    badge: 'Pour démarrer',
    price: '0',
    period: 'MAD / mois',
    commission: '15% par transaction',
    description: 'Idéal pour louer du matériel occasionnel entre voisins et artisans.',
    features: [
      'Modalités de paiement selon disponibilité',
      'Contrat de bail numérique sous DOC',
      'État des lieux photo scellé SHA-256',
      'Support standard par email'
    ],
    cta: 'Commencer gratuitement',
    highlight: false
  },
  {
    id: 'premium',
    name: 'Premium Particulier',
    badge: 'Recommandé Particulier',
    price: '49',
    period: 'MAD / mois',
    commission: '10% par transaction',
    description: 'Pour les bricoleurs et créateurs réguliers qui louent souvent.',
    features: [
      'Commission réduite à 10%',
      'Livraison express partenaire disponible',
      'Badge Confiance VIP sur le profil',
      'Support prioritaire WhatsApp'
    ],
    cta: 'Choisir la formule Premium',
    highlight: true
  },
  {
    id: 'pro',
    name: 'Pro BTP & Événementiel',
    badge: 'Plus populaire',
    price: '299',
    period: 'MAD / mois',
    commission: '7% par transaction',
    description: 'Pour les entreprises du BTP, sociétés de production et loueurs pro.',
    features: [
      'Commission ultra-réduite à 7%',
      'Gestion de flotte multi-chantiers',
      'Facturation B2B automatisée avec ICE',
      'Assurance dommages matériel incluse',
      'Conseiller dédié WhatsApp 24/7'
    ],
    cta: 'Rejoindre le réseau Pro',
    highlight: false
  },
  {
    id: 'entreprise',
    name: 'Grands Comptes',
    badge: 'Sur mesure',
    price: '990',
    period: 'MAD / mois',
    commission: '3% à 5%',
    description: 'Pour les parcs matériels industriels et grandes entreprises.',
    features: [
      'Commission négociée de 3% à 5%',
      'Accès API direct & intégration ERP',
      'Contrats-cadres multi-utilisateurs',
      'Gestionnaire de compte dédié',
      'Assurance tous risques sur mesure'
    ],
    cta: 'Contacter l équipe Grands Comptes',
    highlight: false
  }
];

export default function PricingModal({ isOpen, onClose, onSelectPlan }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-5xl w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-200 mb-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md">
              Grille Tarifaire Transparente
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold text-stone-900 mt-1">
              Des tarifs adaptés à votre activité au Maroc
            </h2>
            <p className="text-xs sm:text-sm text-stone-500 mt-1">
              Choisissez la formule qui correspond à votre volume de location.
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {PRICING_PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`rounded-2xl p-5 border flex flex-col justify-between transition-all ${
                plan.highlight
                  ? 'border-emerald-800 bg-emerald-50/50 shadow-md ring-1 ring-emerald-800/30'
                  : 'border-stone-200 bg-stone-50/40 hover:bg-white hover:shadow-sm'
              }`}
            >
              <div>
                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md inline-block mb-2 ${
                  plan.highlight ? 'bg-emerald-800 text-white' : 'bg-stone-200 text-stone-700'
                }`}>
                  {plan.badge}
                </span>

                <h3 className="text-base font-bold text-stone-900">{plan.name}</h3>
                <p className="text-[11px] text-stone-500 mt-1 min-h-[32px]">{plan.description}</p>

                {/* Price Display */}
                <div className="my-4 pt-3 border-t border-stone-200">
                  <div className="text-2xl font-black text-stone-900">
                    {plan.price} <span className="text-xs font-medium text-stone-500">{plan.period}</span>
                  </div>
                  <div className="text-xs font-bold text-emerald-800 mt-0.5">
                    Commission : {plan.commission}
                  </div>
                </div>

                {/* Features List */}
                <ul className="space-y-2 text-xs text-stone-600 mb-6">
                  {plan.features.map((feat, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Check className="w-3.5 h-3.5 text-emerald-700 shrink-0 mt-0.5" />
                      <span className="leading-tight">{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Action CTA */}
              <button
                onClick={() => {
                  if (onSelectPlan) onSelectPlan(plan.id);
                  onClose();
                }}
                className={`w-full py-2.5 px-3 rounded-xl font-bold text-xs transition-all shadow-xs ${
                  plan.highlight
                    ? 'bg-emerald-800 hover:bg-emerald-900 text-white'
                    : 'bg-stone-900 hover:bg-black text-white'
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>

        {/* Footer Note */}
        <div className="p-3.5 bg-stone-100 rounded-xl text-center text-xs text-stone-500">
          Facturation conforme aux normes fiscales marocaines avec émission automatique de quittances et factures avec Identifiant Commun de l Entreprise (ICE).
        </div>

      </div>
    </div>
  );
}
