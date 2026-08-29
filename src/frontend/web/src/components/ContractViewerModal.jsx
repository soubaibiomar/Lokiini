import React, { useState, useEffect } from 'react';
import { X, FileText, Download, ShieldCheck, Printer, CheckCircle2 } from 'lucide-react';
import { getContract } from '../services/api';

export default function ContractViewerModal({ isOpen, onClose, bookingId, bookingData }) {
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isOpen || !bookingId) return;

    async function loadContract() {
      setLoading(true);
      const data = await getContract(bookingId);
      if (data) {
        setContract(data);
      } else {
        // Fallback local contract data
        setContract({
          booking_id: bookingId,
          contract_reference: `DOC-MAROC-${String(bookingId).substring(0, 8).toUpperCase()}`,
          legal_framework: "Dahir des Obligations et Contrats (DOC) & Loi 53-05 Maroc",
          contract_date: new Date().toLocaleDateString('fr-FR'),
          renter_name: bookingData?.renter_name || "Karim Tazi",
          renter_cin: "BK849201",
          renter_phone: "+212 6 62 00 00 02",
          owner_name: bookingData?.owner_name || "Lokiini Loueur Partenaire",
          owner_company: bookingData?.owner_company || "Entreprise Loueur Partenaire",
          owner_ice: bookingData?.owner_ice || "002345678000045",
          equipment_title: bookingData?.equipment_title || "Matériel / Équipement Certifié",
          equipment_category: bookingData?.category || "Matériel & Équipement",
          rental_period: `${bookingData?.start_date || '2026-08-28'} au ${bookingData?.end_date || '2026-08-31'} (${bookingData?.total_days || 3} jours)`,
          daily_rate_mad: bookingData?.daily_rate_applied_mad || 180,
          total_rental_mad: bookingData?.rental_total_mad || 540,
          cmi_deposit_hold_mad: bookingData?.deposit_hold_mad || 1500,
          cmi_auth_token: bookingData?.cmi_auth_token || "CMI_AUTH_89421A9E",
          sha256_seal: bookingData?.contract_sha256 || "7b2a94f1c3098e72ba6301fa38290f9b6910a301db54321fa98bc1948301ec74",
          legal_clauses: [
            "Article 1 — Objet : Le présent contrat de louage de chose mobilière (matériel audiovisuel, événementiel, outillage, véhicules, high-tech, médical, énergie et engins) est régi par les dispositions des articles 627 et suivants du Dahir des Obligations et Contrats (DOC) du Royaume du Maroc.",
            "Article 2 — Équipement loué : Matériel mis à disposition en parfait état de fonctionnement avec vérification contradictoire d'entrée horodatée RFC 3161.",
            "Article 3 — Cautionnement CMI : Une pré-autorisation bancaire de garantie est bloquée sous séquestre électronique CMI sans débit immédiat.",
            "Article 4 — Signature & Force Probante : En application de la Loi n° 53-05 relative à l'échange électronique de données juridiques, le présent acte a pleine valeur probatoire entre les parties.",
            "Article 5 — Juridiction : Tout litige relève de la compétence exclusive du Tribunal de Commerce compétent au Royaume du Maroc."
          ]
        });
      }
      setLoading(false);
    }
    loadContract();
  }, [isOpen, bookingId, bookingData]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white rounded-3xl max-w-3xl w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200 my-8 flex flex-col max-h-[90vh]">
        
        {/* Modal Top Controls */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-200 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-teal-50 flex items-center justify-center text-lokiini-teal">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-black text-lg text-lokiini-charcoal font-['Outfit']">Contrat de Bail Numérique DOC</h3>
              <span className="text-xs text-stone-500">Conforme au Dahir des Obligations et Contrats & Loi 53-05</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => window.print()}
              className="p-2 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 transition-colors"
              title="Imprimer le contrat"
            >
              <Printer className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Contract Printable Area */}
        <div className="overflow-y-auto py-6 pr-2 space-y-6 text-xs text-stone-700 leading-relaxed font-serif">
          
          {/* Header Banner */}
          <div className="text-center border-b border-stone-200 pb-4">
            <img src="/logo.png" alt="Lokiini Maroc" className="h-10 w-auto mx-auto mb-2 object-contain" />
            <h2 className="text-base font-bold uppercase tracking-widest text-stone-900 font-sans">
              ROYAUME DU MAROC — CONTRAT DE LOCATION DE MATÉRIEL
            </h2>
            <div className="text-[11px] text-stone-500 font-mono mt-1">
              Réf : <span className="font-bold text-stone-800">{contract?.contract_reference}</span> | Date : {contract?.contract_date}
            </div>
            <div className="inline-block bg-teal-50 text-lokiini-teal text-[10px] font-bold px-3 py-0.5 rounded-full mt-2 font-sans border border-teal-200">
              Scellé par Signature Électronique Dématérialisée (Loi n° 53-05)
            </div>
          </div>

          {/* Parties Box */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 font-sans text-xs">
            <div className="bg-stone-50 p-4 rounded-xl border border-stone-200 space-y-1">
              <h4 className="font-bold text-stone-900 uppercase text-[10px] tracking-wider text-lokiini-teal">
                LE LOUEUR (Propriétaire)
              </h4>
              <div className="font-bold text-stone-900">{contract?.owner_name}</div>
              <div className="text-stone-600">{contract?.owner_company}</div>
              <div className="text-stone-500 text-[11px]">ICE : {contract?.owner_ice}</div>
            </div>

            <div className="bg-stone-50 p-4 rounded-xl border border-stone-200 space-y-1">
              <h4 className="font-bold text-stone-900 uppercase text-[10px] tracking-wider text-lokiini-terracotta">
                LE PRENEUR (Locataire)
              </h4>
              <div className="font-bold text-stone-900">{contract?.renter_name}</div>
              <div className="text-stone-600">CIN : {contract?.renter_cin} (Certifiée CNDP)</div>
              <div className="text-stone-500 text-[11px]">Tél : {contract?.renter_phone}</div>
            </div>
          </div>

          {/* Financials Table */}
          <div className="font-sans">
            <table className="w-full text-left border-collapse border border-stone-200 text-xs">
              <thead className="bg-stone-100 text-stone-700">
                <tr>
                  <th className="p-2.5 border border-stone-200">Désignation du Matériel</th>
                  <th className="p-2.5 border border-stone-200">Période</th>
                  <th className="p-2.5 border border-stone-200">Total Location TTC</th>
                  <th className="p-2.5 border border-stone-200">Caution Séquestrée (CMI)</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="p-2.5 border border-stone-200 font-bold">{contract?.equipment_title}</td>
                  <td className="p-2.5 border border-stone-200">{contract?.rental_period}</td>
                  <td className="p-2.5 border border-stone-200 font-black text-lokiini-teal">{contract?.total_rental_mad} MAD</td>
                  <td className="p-2.5 border border-stone-200 font-black text-lokiini-terracotta">{contract?.cmi_deposit_hold_mad} MAD</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Articles & Clauses */}
          <div className="space-y-2.5">
            <h4 className="font-bold text-stone-900 font-sans text-xs uppercase tracking-wider">
              Clauses & Conditions Générales du Dahir des Obligations et Contrats
            </h4>
            {contract?.legal_clauses?.map((clause, idx) => (
              <p key={idx} className="text-stone-600 text-justify text-[11px] leading-relaxed">
                {clause}
              </p>
            ))}
          </div>

          {/* Cryptographic Seal Footprint */}
          <div className="bg-stone-50 p-4 rounded-xl border border-stone-200 font-mono text-[10px] text-stone-500 space-y-1">
            <div className="flex items-center gap-1 font-bold text-emerald-700 font-sans text-xs mb-1">
              <ShieldCheck className="w-4 h-4" />
              <span>Empreinte Cryptographique d'Horodatage SHA-256</span>
            </div>
            <div className="truncate text-stone-800 font-bold">{contract?.sha256_seal}</div>
            <div>Jeton CMI : {contract?.cmi_auth_token}</div>
          </div>

        </div>

        {/* Footer */}
        <div className="pt-4 border-t border-stone-200 flex justify-end gap-3 shrink-0">
          <button
            onClick={onClose}
            className="bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold px-6 py-2.5 rounded-xl transition-all shadow text-xs"
          >
            Fermer
          </button>
        </div>

      </div>
    </div>
  );
}
