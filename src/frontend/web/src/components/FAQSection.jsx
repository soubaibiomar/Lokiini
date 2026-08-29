import React, { useState } from 'react';
import { HelpCircle, ChevronDown, ChevronUp, FileCheck, Shield, Banknote } from 'lucide-react';

const FAQ_ITEMS = [
  {
    q: "Comment fonctionne la caution séquestrée CMI sans débit bancaire sur Lokiini ?",
    a: "Contrairement aux plateformes classiques où l'utilisateur doit verser des milliers de dirhams en espèces, Lokiini utilise une pré-autorisation monétique via le Centre Monétique Interbancaire (CMI). Le montant de la caution est simplement réservé sur votre plafond carte bancaire sans être débité de votre compte. À la fin de la location, après validation de l'état des lieux contradictoire de retour, la caution est débloquée automatiquement en temps réel."
  },
  {
    q: "Quelles sont les obligations légales et conformité au Dahir des Obligations et Contrats (DOC) ?",
    a: "Toute location opérée sur Lokiini génère un contrat de louage de choses juridiquement contraignant, conforme aux articles 627 et suivants du Dahir formant Code des Obligations et des Contrats (DOC du Royaume du Maroc). Ce contrat est signé par voie électronique dématérialisée sous l'égide de la Loi n° 53-05 relative à l'échange électronique des données juridiques."
  },
  {
    q: "Comment mes données personnelles et ma CIN sont-elles protégées (Loi CNDP n° 09-08) ?",
    a: "Lokiini applique une architecture de sécurité Zero-Knowledge strictement conforme à la Loi n° 09-08 de la Commission Nationale de contrôle de la protection des Données à caractère Personnel (CNDP). Les flux vidéos du test de vivacité (liveness check) sont analysés en mémoire vive volatile (RAM) et purgés immédiatement après calcul. Seule une empreinte cryptographique SHA-256 d'attestation est conservée en base de données."
  },
  {
    q: "Comment se déroule l'état des lieux vidéo contradictoire lors de la prise en main ?",
    a: "Lors de la remise de l'équipement, le propriétaire et le locataire réalisent un enregistrement vidéo de 30 secondes via l'application Lokiini. La vidéo capture l'état fonctionnel et les éventuelles micro-rayures. Le fichier est instantanément scellé par empreinte SHA-256 et horodatage RFC 3161, éliminant tout litige lors de la restitution."
  },
  {
    q: "Dans quelles villes marocaines les équipements sont-ils disponibles ?",
    a: "Le service est opérationnel dans l'ensemble des 12 régions du Maroc avec une large sélection de matériel événementiel, audiovisuel, drones, outillage de bricolage, véhicules, high-tech, matériel médical et engins professionnels à Casablanca, Rabat, Marrakech, Tanger, Fès, Agadir, Oujda, Meknès, Kénitra, Tétouan, El Jadida et Laâyoune."
  }
];

export default function FAQSection() {
  const [openIndex, setOpenIndex] = useState(null);

  const toggle = (idx) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-xs font-bold mb-3">
          <HelpCircle className="w-3.5 h-3.5" />
          <span>Foire Aux Questions & Cadre Opérationnel Maroc</span>
        </div>
        <h2 className="text-2xl sm:text-3xl font-black text-lokiini-charcoal font-['Outfit'] tracking-tight">
          Questions Fréquentes sur la Location Sécurisée
        </h2>
        <p className="text-stone-600 text-sm mt-3 leading-relaxed">
          Tout savoir sur les cautions CMI, le cadre juridique du bail DOC, les règles CNDP et le fonctionnement sur les chantiers.
        </p>
      </div>

      <div className="space-y-4">
        {FAQ_ITEMS.map((item, idx) => {
          const isOpen = openIndex === idx;
          return (
            <div
              key={idx}
              className="bg-white rounded-2xl border border-stone-200 overflow-hidden transition-all shadow-sm"
            >
              <button
                onClick={() => toggle(idx)}
                className="w-full text-left p-5 sm:p-6 flex items-center justify-between gap-4 font-bold text-stone-900 text-sm sm:text-base hover:text-lokiini-teal transition-colors"
              >
                <span>{item.q}</span>
                <span className="p-1 rounded-lg bg-stone-100 text-stone-500 shrink-0">
                  {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </span>
              </button>

              {isOpen && (
                <div className="px-5 sm:px-6 pb-6 pt-0 text-xs sm:text-sm text-stone-600 leading-relaxed border-t border-stone-100 bg-stone-50/50">
                  <div className="pt-4">{item.a}</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}
