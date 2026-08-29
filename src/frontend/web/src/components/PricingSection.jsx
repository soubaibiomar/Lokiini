import React, { useState } from 'react';
import { Check, Zap, Sparkles, Building2, Shield, ArrowRight, Star } from 'lucide-react';

export default function PricingSection({ onSelectPlan, onOpenAuth }) {
  const [billingCycle, setBillingCycle] = useState('monthly'); // 'monthly' | 'annual'

  const plans = [
    {
      id: 'Gratuit',
      name: 'Gratuit',
      subtitle: 'Pour particuliers louant occasionnellement',
      priceMonthly: 0,
      priceAnnual: 0,
      commission: '15%',
      maxListings: 'Jusqu\'à 3 annonces',
      badge: null,
      highlight: false,
      buttonText: 'Commencer Gratuitement',
      buttonVariant: 'outline',
      features: [
        '3 annonces actives simultanées',
        'Caution séquestrée non débitée CMI',
        'Contrats de bail DOC (Art. 627+)',
        'Vérification d\'identité CIN (Loi 09-08)',
        'Commission standard de 15%',
        'Paiement Cash COD ou Carte CMI',
        'Support standard par email'
      ]
    },
    {
      id: 'Premium',
      name: 'Premium',
      subtitle: 'Pour loueurs réguliers, créateurs et artisans',
      priceMonthly: 79,
      priceAnnual: 63,
      commission: '12%',
      maxListings: 'Jusqu\'à 15 annonces',
      badge: 'Loueur Recommandé',
      highlight: false,
      buttonText: 'Choisir Premium',
      buttonVariant: 'secondary',
      features: [
        '15 annonces actives simultanées',
        'Commission réduite à 12%',
        'Badge officiel "Loueur Recommandé"',
        'Statistiques de vues et clics en temps réel',
        'Mise en avant prioritaire dans les recherches',
        'Scellement d\'états des lieux SHA-256 illimité',
        'Support prioritaire WhatsApp 7j/7'
      ]
    },
    {
      id: 'Pro',
      name: 'Pro — Entreprises & Loueurs',
      subtitle: 'Idéal pour parcs de location, agences événementielles, matériel pro et transport',
      priceMonthly: 149,
      priceAnnual: 119,
      commission: '7%',
      maxListings: 'Annonces Illimitées',
      badge: 'Le Plus Populaire 🔥',
      highlight: true,
      buttonText: 'Souscrire au Forfait Pro',
      buttonVariant: 'primary',
      features: [
        'Annonces & équipements ILLIMITÉS',
        'Commission ultra-réduite à 7%',
        'Badge de confiance "Loueur Pro Certifié"',
        'Facturation automatique avec ICE & TVA 20% déductible',
        'Tableau de bord financier des gains en MAD',
        'Contrats de bail DOC personnalisés avec logo d\'entreprise',
        'Alertes WhatsApp instantanées n8n',
        'Support prioritaire dédié 7j/7'
      ]
    },
    {
      id: 'Entreprise',
      name: 'Grands Parcs & Flottes',
      subtitle: 'Pour grandes agences, concessions de matériel, régies et parcs multi-villes',
      priceMonthly: 300,
      priceAnnual: 239,
      commission: '5%',
      maxListings: 'Parc Illimité Multi-villes',
      badge: 'Sur-Mesure',
      highlight: false,
      buttonText: 'Contacter un Conseiller',
      buttonVariant: 'outline',
      features: [
        'Gestion de parcs multi-villes et multi-dépôts',
        'Commission minimale négociée à 5%',
        'Gestion multi-comptes et agents délégués',
        'Intégration API & ERP personnalisée via n8n',
        'Garantie et assurance grand compte',
        'Gestionnaire de compte dédié au Maroc',
        'Export comptable personnalisé'
      ]
    }
  ];

  return (
    <section id="tarifs" className="py-20 bg-gradient-to-b from-stone-50 via-white to-stone-50 border-t border-stone-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <div className="inline-flex items-center gap-2 bg-emerald-50 border border-emerald-200 text-emerald-800 px-3.5 py-1.5 rounded-full text-xs font-bold mb-4 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span>Monétisez votre matériel en toute sécurité</span>
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-stone-900 tracking-tight">
            Tarifs Transparents & <span className="text-lokiini-teal">Formules d'Abonnement</span>
          </h2>
          <p className="mt-4 text-base text-stone-600">
            Publiez gratuitement vos premiers équipements ou passez au forfait Pro pour booster votre rentabilité avec des commissions réduites dès <span className="font-bold text-stone-900">7%</span> et des factures avec <span className="font-bold text-stone-900">ICE & TVA</span> déductibles.
          </p>

          {/* Billing Cycle Switcher */}
          <div className="mt-8 inline-flex items-center bg-stone-100 p-1.5 rounded-2xl border border-stone-200 shadow-inner">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-5 py-2 rounded-xl text-xs font-bold transition-all ${
                billingCycle === 'monthly'
                  ? 'bg-white text-stone-900 shadow-sm'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              Facturation Mensuelle
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`flex items-center gap-1.5 px-5 py-2 rounded-xl text-xs font-bold transition-all ${
                billingCycle === 'annual'
                  ? 'bg-lokiini-teal text-white shadow-sm'
                  : 'text-stone-600 hover:text-stone-900'
              }`}
            >
              <span>Facturation Annuelle</span>
              <span className="bg-amber-400 text-stone-900 text-[10px] px-1.5 py-0.5 rounded-full font-extrabold">
                -20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 items-stretch">
          {plans.map((plan) => {
            const price = billingCycle === 'annual' ? plan.priceAnnual : plan.priceMonthly;
            
            return (
              <div
                key={plan.id}
                className={`relative rounded-3xl flex flex-col justify-between transition-all duration-200 ${
                  plan.highlight
                    ? 'bg-white border-2 border-lokiini-teal shadow-xl ring-4 ring-lokiini-teal/10 scale-105 z-10'
                    : 'bg-white border border-stone-200 hover:border-stone-300 shadow-sm hover:shadow-md'
                } p-6 sm:p-7`}
              >
                {/* Popular Badge */}
                {plan.badge && (
                  <div className={`absolute -top-3.5 left-1/2 -translate-x-1/2 px-3.5 py-1 rounded-full text-xs font-extrabold tracking-wide uppercase shadow-sm ${
                    plan.highlight
                      ? 'bg-lokiini-teal text-white'
                      : 'bg-stone-900 text-white'
                  }`}>
                    {plan.badge}
                  </div>
                )}

                <div>
                  {/* Title & Subtitle */}
                  <div className="mb-4">
                    <h3 className="text-xl font-bold text-stone-900">{plan.name}</h3>
                    <p className="text-xs text-stone-500 mt-1 min-h-[32px]">{plan.subtitle}</p>
                  </div>

                  {/* Price */}
                  <div className="my-6 pb-6 border-b border-stone-100 flex items-baseline gap-1">
                    <span className="text-4xl font-extrabold text-stone-900">
                      {price}
                    </span>
                    <span className="text-sm font-bold text-stone-500">DH</span>
                    <span className="text-xs text-stone-400">/ mois</span>
                  </div>

                  {/* Key Metrics */}
                  <div className="grid grid-cols-2 gap-2 mb-6 bg-stone-50 p-3 rounded-xl text-center">
                    <div>
                      <div className="text-[10px] text-stone-400 font-bold uppercase">Commission</div>
                      <div className="text-sm font-extrabold text-lokiini-teal">{plan.commission}</div>
                    </div>
                    <div>
                      <div className="text-[10px] text-stone-400 font-bold uppercase">Capacité</div>
                      <div className="text-xs font-bold text-stone-800">{plan.maxListings}</div>
                    </div>
                  </div>

                  {/* Features List */}
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feat, idx) => (
                      <li key={idx} className="flex items-start gap-2.5 text-xs text-stone-700">
                        <div className="mt-0.5 p-0.5 rounded-full bg-emerald-100 text-emerald-700 shrink-0">
                          <Check className="w-3 h-3" />
                        </div>
                        <span className="leading-snug">{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Action CTA Button */}
                <div>
                  <button
                    onClick={() => {
                      if (onSelectPlan) onSelectPlan(plan.id);
                      else if (onOpenAuth) onOpenAuth();
                    }}
                    className={`w-full py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                      plan.highlight
                        ? 'bg-lokiini-teal hover:bg-lokiini-teal-dark text-white shadow-md hover:shadow-lg'
                        : plan.buttonVariant === 'secondary'
                        ? 'bg-stone-900 hover:bg-stone-800 text-white'
                        : 'border border-stone-300 hover:bg-stone-50 text-stone-800'
                    }`}
                  >
                    <span>{plan.buttonText}</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>

              </div>
            );
          })}
        </div>

        {/* B2B Assurance Banner */}
        <div className="mt-14 bg-stone-900 text-white rounded-3xl p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6 shadow-xl">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-lokiini-teal/20 border border-lokiini-teal/40 flex items-center justify-center shrink-0">
              <Building2 className="w-6 h-6 text-lokiini-teal" />
            </div>
            <div>
              <h4 className="text-base font-bold">Entreprise, Agence Événementielle, Studio ou Société de Location ?</h4>
              <p className="text-xs text-stone-300 mt-1">
                Toutes nos factures comportent l'ICE, la TVA déductible à 20% et la conformité juridique au Dahir des Obligations et Contrats (DOC).
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <a
              href="https://wa.me/212661000000"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-white hover:bg-stone-100 text-stone-900 px-5 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-sm"
            >
              <Zap className="w-3.5 h-3.5 text-amber-500" />
              <span>Contact WhatsApp Direct</span>
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
