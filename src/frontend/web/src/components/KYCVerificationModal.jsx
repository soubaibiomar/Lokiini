import React, { useState } from 'react';
import { X, ShieldCheck, Camera, Upload, CheckCircle2, Lock, FileText, ArrowRight } from 'lucide-react';

export default function KYCVerificationModal({ isOpen, onClose, onVerificationSuccess }) {
  const [cinNumber, setCinNumber] = useState('BK849201');
  const [step, setStep] = useState(1); // 1: Info, 2: Camera Selfie / Liveness, 3: Success
  const [isProcessing, setIsProcessing] = useState(false);

  if (!isOpen) return null;

  const handleSimulateVerification = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setStep(3);
      onVerificationSuccess();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-8 shadow-2xl border border-stone-200 animate-in fade-in zoom-in duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-stone-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-teal-50 flex items-center justify-center text-lokiini-teal">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-black text-base text-lokiini-charcoal font-['Outfit']">Vérification d'Identité CNDP</h3>
              <span className="text-[10px] text-stone-400">Conforme à la Loi n° 09-08 (Royaume du Maroc)</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-stone-100 hover:bg-stone-200 flex items-center justify-center text-stone-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content according to step */}
        {step === 1 && (
          <div className="py-6 space-y-4">
            <p className="text-xs text-stone-600 leading-relaxed">
              Pour garantir la sécurité des matériels loués et activer les cautions sans débit, votre Carte d'Identité Nationale (CIN) est vérifiée selon le protocole sécurisé <span className="font-bold text-lokiini-charcoal">Zero-Knowledge</span>.
            </p>

            <div>
              <label className="block text-xs font-bold text-stone-700 mb-1">Numéro de CIN Marocaine</label>
              <input
                type="text"
                value={cinNumber}
                onChange={(e) => setCinNumber(e.target.value.toUpperCase())}
                placeholder="Ex: BK123456"
                className="w-full bg-stone-50 border border-stone-300 rounded-xl px-4 py-2.5 text-sm font-bold tracking-wider text-stone-800 focus:outline-none focus:border-lokiini-teal"
              />
            </div>

            <div className="grid grid-cols-2 gap-3 pt-2">
              <div className="border-2 border-dashed border-stone-200 rounded-xl p-4 text-center hover:bg-stone-50 cursor-pointer transition-colors">
                <Upload className="w-6 h-6 text-stone-400 mx-auto mb-2" />
                <span className="text-[11px] font-bold text-stone-600 block">Recto CIN</span>
                <span className="text-[9px] text-stone-400">JPG, PNG</span>
              </div>
              <div className="border-2 border-dashed border-stone-200 rounded-xl p-4 text-center hover:bg-stone-50 cursor-pointer transition-colors">
                <Upload className="w-6 h-6 text-stone-400 mx-auto mb-2" />
                <span className="text-[11px] font-bold text-stone-600 block">Verso CIN</span>
                <span className="text-[9px] text-stone-400">JPG, PNG</span>
              </div>
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs flex items-center justify-center gap-2 mt-4"
            >
              <span>Continuer vers le selfie vidéo</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="py-6 text-center space-y-4">
            <div className="w-36 h-36 mx-auto rounded-full border-4 border-lokiini-teal overflow-hidden bg-stone-900 relative shadow-inner flex items-center justify-center">
              <Camera className="w-12 h-12 text-white/50 animate-pulse" />
              <div className="absolute inset-0 border border-white/20 rounded-full" />
            </div>

            <div>
              <h4 className="font-bold text-sm text-stone-800">Test de Vivacité Anti-Deepfake</h4>
              <p className="text-xs text-stone-500 max-w-xs mx-auto mt-1">
                Regardez l'écran et tournez lentement la tête pour valider votre présence en direct.
              </p>
            </div>

            <div className="bg-amber-50 text-amber-800 border border-amber-200 rounded-xl p-2.5 text-[11px] text-left flex items-start gap-2">
              <Lock className="w-4 h-4 shrink-0 text-amber-600 mt-0.5" />
              <span>
                Politique Zero-Knowledge : Cette vidéo est analysée en mémoire vive puis <span className="font-bold">immédiatement purgée</span>. Aucune image biométrique brute n'est conservée.
              </span>
            </div>

            <button
              disabled={isProcessing}
              onClick={handleSimulateVerification}
              className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3.5 rounded-xl transition-all shadow text-xs flex items-center justify-center gap-2"
            >
              {isProcessing ? (
                <span>Vérification algorithmique en cours...</span>
              ) : (
                <span>Valider le Liveness Check & Chiffrer</span>
              )}
            </button>
          </div>
        )}

        {step === 3 && (
          <div className="py-6 text-center space-y-4">
            <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto text-emerald-600 shadow-md">
              <CheckCircle2 className="w-10 h-10" />
            </div>

            <h4 className="text-xl font-black text-lokiini-charcoal font-['Outfit']">Identité Certifiée CNDP</h4>
            <p className="text-xs text-stone-500 max-w-xs mx-auto">
              Score de vivacité : <span className="font-bold text-emerald-600">96.5%</span>. Vous pouvez désormais réserver et louer du matériel en 1 clic.
            </p>

            <div className="bg-stone-50 p-3 rounded-xl border border-stone-200 text-left text-[11px] text-stone-500 font-mono">
              Empreinte Audit CNDP : 7b2a...94f1 (SHA-256)
            </div>

            <button
              onClick={onClose}
              className="w-full bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 rounded-xl transition-all shadow text-xs"
            >
              Terminer & Accéder aux Réservations
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
