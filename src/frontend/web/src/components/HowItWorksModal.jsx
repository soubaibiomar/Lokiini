import React from 'react';
import { X, ShieldCheck, Banknote, FileCheck, Camera, CheckCircle2, ArrowRight } from 'lucide-react';

const STEPS = [
  {
    num: '01',
    title: 'Trouvez et Réservez votre Matériel',
    desc: 'Explorez le catalogue d équipements vérifiés près de chez vous. Sélectionnez vos dates de location et choisissez entre le retrait sur place ou la livraison coursier.',
    icon: Banknote,
    detail: 'Paiement à la livraison (COD) : Aucun numéro de carte bancaire n est requis en ligne.'
  },
  {
    num: '02',
    title: 'Vérification d Identité Didit (CNDP)',
    desc: 'Pour activer la transaction en toute confiance, votre document marocain (CIN ou Passeport) et un rapide selfie vidéo de vivacité sont validés par Didit.',
    icon: ShieldCheck,
    detail: 'Zero-Knowledge : Vos données biométriques sont analysées en mémoire vive et immédiatement purgées.'
  },
  {
    num: '03',
    title: 'Remise & État des Lieux Numérique Contradictoire',
    desc: 'Lors de la remise de l équipement, le propriétaire et le locataire prennent les photos d état des lieux horodatées RFC 3161 et signent le contrat de bail (Loi 53-05).',
    icon: Camera,
    detail: 'Réglez le montant de la location et déposez la caution en espèces auprès du loueur.'
  },
  {
    num: '04',
    title: 'Retour du Matériel & Restitution de la Caution',
    desc: 'À l échéance, l état des lieux de retour est scellé. Le loueur valide la restitution et vous rend l intégralité de votre caution en cash.',
    icon: FileCheck,
    detail: 'Garantie anti-litige : En cas de désaccord, l arbitrage Lokiini intervient sous 24h sur la base des photos scellées.'
  }
];

export default function HowItWorksModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-200 mb-6">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-md">
              Processus Sécurisé
            </span>
            <h2 className="text-2xl font-bold text-stone-900 mt-1">
              Comment fonctionne la location sur Lokiini ?
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Un tiers de confiance numérique adapté aux réalités du marché marocain.
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Steps List */}
        <div className="space-y-4 mb-6">
          {STEPS.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div key={idx} className="p-4 rounded-2xl bg-stone-50 border border-stone-200 flex items-start gap-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-800 text-white font-bold flex items-center justify-center shrink-0 text-sm">
                  {step.num}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-stone-900 text-sm">{step.title}</h3>
                  </div>
                  <p className="text-xs text-stone-600 mt-1 leading-relaxed">{step.desc}</p>
                  <div className="mt-2 text-[11px] font-semibold text-emerald-800 bg-white p-2 rounded-lg border border-stone-200">
                    {step.detail}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* CTA */}
        <button
          onClick={onClose}
          className="w-full bg-emerald-800 hover:bg-emerald-900 text-white font-bold py-3 rounded-xl transition-all shadow-xs text-xs"
        >
          J ai compris, explorer les annonces
        </button>

      </div>
    </div>
  );
}
