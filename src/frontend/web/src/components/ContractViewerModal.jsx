import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  CalendarDays, Check, Download, FileCheck2, FileText, Languages, Package,
  Printer, RefreshCw, ShieldAlert, UserRound,
} from 'lucide-react';

import { getContract, signContract } from '../services/api';
import {
  Badge, Button, Card, Checkbox, ErrorState, Modal, Skeleton, Stepper,
} from './ui';

const money = new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' });

const CONTRACT_STEPS = [
  { label: 'Réservation confirmée', description: 'Validée par le backend' },
  { label: 'Contrat généré', description: 'Version française disponible' },
  { label: 'Revue des parties', description: 'Propriétaire et locataire' },
  { label: 'Acceptation', description: 'Prestataire requis' },
  { label: 'Document final', description: 'Après les deux signatures' },
];

function formatDate(value) {
  if (!value) return 'Date indisponible';
  const parsed = new Date(`${String(value).slice(0, 10)}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return 'Date indisponible';
  return new Intl.DateTimeFormat('fr-MA', { day: 'numeric', month: 'long', year: 'numeric' }).format(parsed);
}

function signaturePresentation(status, available) {
  if (status === 'signed') return { label: 'Accepté et signé', tone: 'success' };
  if (!available || status === 'unavailable') return { label: 'Signature indisponible', tone: 'neutral' };
  return { label: 'Acceptation en attente', tone: 'warning' };
}

function PartyCard({ title, party, accent = 'primary' }) {
  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <span className={`flex size-10 shrink-0 items-center justify-center rounded-xl ${accent === 'action' ? 'bg-action-subtle text-action' : 'bg-primary-subtle text-primary'}`}>
          <UserRound aria-hidden="true" className="size-5" />
        </span>
        <div className="min-w-0">
          <p className="text-xs font-bold uppercase tracking-wide text-muted">{title}</p>
          <p className="mt-1 font-display text-base font-bold text-ink">{party?.name || 'Information indisponible'}</p>
          {party?.company_name && <p className="mt-1 text-sm text-muted">{party.company_name}</p>}
          {party?.company_ice && <p className="mt-1 text-xs text-muted">ICE : {party.company_ice}</p>}
          {party?.city && <p className="mt-1 text-xs text-muted">{party.city}</p>}
        </div>
      </div>
    </Card>
  );
}

function ContractSkeleton() {
  return (
    <div className="space-y-5" aria-label="Chargement du contrat">
      <Skeleton className="h-24 w-full" />
      <div className="grid gap-4 sm:grid-cols-2"><Skeleton className="h-32" /><Skeleton className="h-32" /></div>
      <Skeleton className="h-72 w-full" />
    </div>
  );
}

export default function ContractViewerModal({ isOpen, onClose, bookingId, onContractUpdated }) {
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [language, setLanguage] = useState('fr');
  const [consented, setConsented] = useState(false);
  const [signing, setSigning] = useState(false);
  const [signError, setSignError] = useState(null);

  const loadContract = useCallback(async (signal) => {
    if (!bookingId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getContract(bookingId, { signal });
      setContract(data);
      setLanguage(data?.language || 'fr');
    } catch (requestError) {
      if (requestError?.code !== 'REQUEST_CANCELLED') {
        setContract(null);
        setError(requestError);
      }
    } finally {
      setLoading(false);
    }
  }, [bookingId]);

  useEffect(() => {
    if (!isOpen || !bookingId) return undefined;
    const controller = new AbortController();
    setConsented(false);
    setSignError(null);
    loadContract(controller.signal);
    return () => controller.abort();
  }, [isOpen, bookingId, loadContract]);

  const currentStep = useMemo(() => {
    if (contract?.completed) return 4;
    if (contract?.owner_signature_status === 'signed' || contract?.renter_signature_status === 'signed') return 3;
    return 2;
  }, [contract]);

  const contractText = language === 'ar' ? contract?.contract_text_ar : contract?.contract_text;
  const availableLanguages = contract?.available_languages || ['fr'];
  const ownerSignature = signaturePresentation(contract?.owner_signature_status, contract?.signature_available);
  const renterSignature = signaturePresentation(contract?.renter_signature_status, contract?.signature_available);

  const downloadText = () => {
    if (!contractText) return;
    const blob = new Blob([contractText], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${contract.contract_number || 'contrat-lokiini'}.${language}.txt`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const acceptContract = async () => {
    if (!consented || !contract?.signature_available) return;
    setSigning(true);
    setSignError(null);
    try {
      await signContract(bookingId, { consentement_explicite: true });
      await loadContract();
      onContractUpdated?.();
    } catch (requestError) {
      setSignError(requestError?.message || 'L’acceptation du contrat n’a pas pu être enregistrée.');
    } finally {
      setSigning(false);
    }
  };

  const errorDescription = error?.code === 'CONTRACT_NOT_READY'
    ? 'Le contrat sera disponible lorsque la réservation atteindra le statut confirmé.'
    : error?.message || 'Le contrat ne peut pas être chargé pour le moment.';

  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      title="Contrat de location"
      description={contract?.contract_number || 'Document associé à la réservation'}
      size="xl"
    >
      {loading ? <ContractSkeleton /> : error ? (
        <ErrorState
          title={error?.code === 'CONTRACT_NOT_READY' ? 'Contrat pas encore disponible' : 'Contrat indisponible'}
          description={errorDescription}
          onRetry={() => loadContract()}
        />
      ) : contract && (
        <div className="space-y-6">
          <section aria-labelledby="contract-progress-title">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 id="contract-progress-title" className="font-display text-lg font-bold text-ink">Progression du contrat</h3>
                <p className="mt-1 text-sm text-muted">Chaque étape dépend des capacités réellement disponibles côté backend.</p>
              </div>
              <Badge variant={contract.completed ? 'success' : 'info'}>{contract.completed ? 'Contrat finalisé' : 'Version à relire'}</Badge>
            </div>
            <Stepper steps={CONTRACT_STEPS} current={currentStep} className="mt-5" />
          </section>

          {!contract.signature_available && (
            <div role="status" className="flex items-start gap-3 rounded-card border border-warning/25 bg-warning-subtle p-4">
              <ShieldAlert aria-hidden="true" className="mt-0.5 size-5 shrink-0 text-warning" />
              <div>
                <p className="text-sm font-bold text-ink">Acceptation et signature non disponibles</p>
                <p className="mt-1 text-xs leading-5 text-muted">Aucun prestataire de signature professionnellement validé n’est configuré. Lokiini permet la consultation du contrat, mais ne présente ni signature qualifiée ni certificat.</p>
              </div>
            </div>
          )}

          <section aria-labelledby="contract-parties-title">
            <h3 id="contract-parties-title" className="font-display text-lg font-bold text-ink">Les parties</h3>
            <div className="mt-3 grid gap-4 sm:grid-cols-2">
              <PartyCard title="Propriétaire" party={contract.owner} />
              <PartyCard title="Locataire" party={contract.renter} accent="action" />
            </div>
          </section>

          <section aria-labelledby="contract-rental-title">
            <h3 id="contract-rental-title" className="font-display text-lg font-bold text-ink">Location concernée</h3>
            <Card className="mt-3 overflow-hidden">
              <div className="grid gap-5 p-5 lg:grid-cols-[1.4fr_1fr]">
                <div>
                  <div className="flex items-start gap-3">
                    <span className="flex size-10 shrink-0 items-center justify-center rounded-xl bg-stone-100 text-muted"><Package aria-hidden="true" className="size-5" /></span>
                    <div><p className="font-display text-lg font-bold text-ink">{contract.equipment?.title}</p><p className="mt-1 text-xs text-muted">{contract.equipment?.category}</p></div>
                  </div>
                  {contract.equipment?.description && <p className="mt-4 text-sm leading-6 text-muted">{contract.equipment.description}</p>}
                </div>
                <dl className="space-y-3 rounded-control bg-stone-50 p-4 text-sm">
                  <div><dt className="text-xs font-bold text-muted">Période</dt><dd className="mt-1 flex items-start gap-2 font-semibold text-ink"><CalendarDays aria-hidden="true" className="mt-0.5 size-4 shrink-0 text-primary" />{formatDate(contract.start_date)} — {formatDate(contract.end_date)}</dd></div>
                  <div><dt className="text-xs font-bold text-muted">Durée enregistrée</dt><dd className="mt-1 font-semibold text-ink">{contract.number_of_days} jour{contract.number_of_days > 1 ? 's' : ''}</dd></div>
                </dl>
              </div>
              <div className="grid border-t border-border sm:grid-cols-2 sm:divide-x sm:divide-border">
                <div className="p-5"><p className="text-xs font-bold uppercase tracking-wide text-muted">Prix de location</p><p className="mt-2 font-display text-2xl font-bold text-primary">{money.format(contract.rental_price_mad)}</p><p className="mt-1 text-xs text-muted">{contract.payment_method}</p></div>
                <div className="border-t border-border p-5 sm:border-t-0"><p className="text-xs font-bold uppercase tracking-wide text-muted">Dépôt de garantie</p><p className="mt-2 font-display text-2xl font-bold text-action">{money.format(contract.deposit_amount_mad)}</p><p className="mt-1 text-xs text-muted">{contract.deposit_method}</p></div>
              </div>
            </Card>
          </section>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card className="p-5"><h3 className="font-display text-base font-bold text-ink">Responsabilités</h3><ul className="mt-3 space-y-2">{contract.responsibilities?.map((item) => <li key={item} className="flex items-start gap-2 text-sm leading-6 text-muted"><Check aria-hidden="true" className="mt-1 size-4 shrink-0 text-primary" /><span>{item}</span></li>)}</ul></Card>
            <Card className="p-5"><h3 className="font-display text-base font-bold text-ink">Conditions importantes</h3><ul className="mt-3 space-y-2">{contract.important_conditions?.map((item) => <li key={item} className="flex items-start gap-2 text-sm leading-6 text-muted"><FileCheck2 aria-hidden="true" className="mt-1 size-4 shrink-0 text-action" /><span>{item}</span></li>)}</ul></Card>
          </div>

          <section aria-labelledby="contract-document-title">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div><h3 id="contract-document-title" className="font-display text-lg font-bold text-ink">Document à relire</h3><p className="mt-1 text-sm text-muted">Contenu généré par FastAPI à partir de la réservation confirmée.</p></div>
              <div className="flex items-center gap-2">
                <Languages aria-hidden="true" className="size-4 text-muted" />
                {availableLanguages.map((code) => <Button key={code} size="sm" variant={language === code ? 'primary' : 'secondary'} onClick={() => setLanguage(code)}>{code === 'ar' ? 'العربية' : 'Français'}</Button>)}
              </div>
            </div>
            <Card className="mt-3 p-5 sm:p-6">
              <pre dir={language === 'ar' ? 'rtl' : 'ltr'} className="whitespace-pre-wrap font-serif text-sm leading-7 text-ink">{contractText}</pre>
              <div className="mt-5 border-t border-border pt-4 text-xs text-muted"><p>Empreinte du contenu : <span className="break-all font-mono">{contract.contract_sha256}</span></p><p className="mt-1">Référence juridique déclarée : {contract.applicable_law}</p></div>
            </Card>
          </section>

          <section aria-labelledby="contract-signatures-title">
            <h3 id="contract-signatures-title" className="font-display text-lg font-bold text-ink">Statut des parties</h3>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <Card className="flex items-center justify-between gap-3 p-4"><div><p className="text-xs font-bold text-muted">Propriétaire</p><p className="mt-1 text-sm font-bold text-ink">{contract.owner?.name}</p></div><Badge variant={ownerSignature.tone}>{ownerSignature.label}</Badge></Card>
              <Card className="flex items-center justify-between gap-3 p-4"><div><p className="text-xs font-bold text-muted">Locataire</p><p className="mt-1 text-sm font-bold text-ink">{contract.renter?.name}</p></div><Badge variant={renterSignature.tone}>{renterSignature.label}</Badge></Card>
            </div>
            {contract.signature_available && !contract.completed && (
              <Card className="mt-4 p-5">
                <Checkbox checked={consented} onChange={(event) => setConsented(event.target.checked)} label="J’ai lu le contrat et j’en accepte le contenu" description="Cette confirmation sera envoyée au prestataire de signature configuré." />
                {signError && <p role="alert" className="mt-3 text-sm font-semibold text-error">{signError}</p>}
                <Button className="mt-4" disabled={!consented} loading={signing} loadingLabel="Enregistrement…" onClick={acceptContract}>Accepter et signer</Button>
              </Card>
            )}
          </section>

          <div className="flex flex-col-reverse gap-3 border-t border-border pt-5 sm:flex-row sm:justify-end">
            <Button variant="secondary" onClick={onClose}>Fermer</Button>
            <Button variant="secondary" onClick={() => window.print()}><Printer aria-hidden="true" className="size-4" /> Imprimer</Button>
            <Button variant="secondary" onClick={downloadText}><Download aria-hidden="true" className="size-4" /> Télécharger le texte</Button>
            {contract.document_url && contract.completed && <Button onClick={() => window.open(contract.document_url, '_blank', 'noopener,noreferrer')}><FileText aria-hidden="true" className="size-4" /> Ouvrir le document final</Button>}
            {!contract.completed && <Button variant="ghost" onClick={() => loadContract()}><RefreshCw aria-hidden="true" className="size-4" /> Actualiser</Button>}
          </div>
        </div>
      )}
    </Modal>
  );
}
