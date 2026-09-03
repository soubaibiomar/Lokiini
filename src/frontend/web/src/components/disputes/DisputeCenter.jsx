import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertCircle, ArrowLeft, Camera, CheckCircle2, FileText, Hash, MessageSquare,
  Paperclip, Scale, ShieldCheck, Trash2, Upload,
} from 'lucide-react';
import {
  createDispute, deleteDisputeEvidence, getDispute, getDisputeContext,
  submitDisputeForReview, uploadDisputeEvidence,
} from '../../services/api';
import {
  Badge, Button, Card, Checkbox, EmptyState, ErrorState, Select,
  Skeleton, Stepper, Textarea,
} from '../ui';
import {
  DISPUTE_REASONS, DISPUTE_STEPS, canOpenDispute, disputeDecision,
  disputeDepositStatus, disputeReason, disputeStatus, disputeSubmissionKey,
} from './disputeExperience';


const MAX_EVIDENCE_BYTES = 25 * 1024 * 1024;

function money(value) {
  return `${new Intl.NumberFormat('fr-MA', { maximumFractionDigits: 2 }).format(Number(value) || 0)} MAD`;
}

function fileSize(value) {
  const bytes = Number(value) || 0;
  return bytes >= 1024 * 1024 ? `${(bytes / (1024 * 1024)).toFixed(1)} Mo` : `${Math.max(1, Math.round(bytes / 1024))} Ko`;
}

function EvidencePreview({ item, removable, onDelete }) {
  const isPhoto = item.media_kind === 'photo';
  const isVideo = item.media_kind === 'video';
  return (
    <Card className="overflow-hidden">
      <div className="flex aspect-[16/10] items-center justify-center bg-stone-100">
        {isPhoto && <img src={item.file_url} alt={`Pièce ${item.original_filename}`} className="size-full object-contain" />}
        {isVideo && <video src={item.file_url} controls preload="metadata" aria-label={`Pièce vidéo ${item.original_filename}`} className="size-full bg-black object-contain" />}
        {!isPhoto && !isVideo && <FileText className="size-9 text-primary" aria-hidden="true" />}
      </div>
      <div className="p-3">
        <div className="flex items-start justify-between gap-2"><div className="min-w-0"><p className="truncate text-xs font-bold text-ink">{item.original_filename}</p><p className="mt-1 text-[11px] text-muted">{fileSize(item.size_bytes)} · {new Date(item.stored_at).toLocaleString('fr-MA')}</p></div>{removable && <Button variant="ghost" size="icon" className="size-8 text-error" onClick={() => onDelete(item)} aria-label="Supprimer cette pièce"><Trash2 className="size-4" /></Button>}</div>
        <p className="mt-2 break-all font-mono text-[10px] leading-4 text-muted"><Hash className="me-1 inline size-3" />{item.sha256_hash}</p>
        <a href={item.file_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs font-bold text-primary hover:underline">Ouvrir l’original</a>
      </div>
    </Card>
  );
}

function ContextPanel({ context, currentUser }) {
  return (
    <div className="space-y-6">
      <section>
        <h3 className="font-display text-lg font-bold text-ink">États des lieux associés</h3>
        <p className="mt-1 text-xs leading-5 text-muted">Rapports enregistrés pour cette réservation, présentés sans interprétation.</p>
        {context.inspections.length ? <div className="mt-3 space-y-3">{context.inspections.map((inspection) => <Card key={inspection.id} className="p-4"><div className="flex flex-wrap items-center justify-between gap-2"><Badge variant="neutral">{inspection.inspection_type === 'check_out' ? 'Check-out' : 'Check-in'}</Badge><span className="text-xs text-muted">{new Date(inspection.recorded_at).toLocaleString('fr-MA')}</span></div><dl className="mt-3 grid gap-3 text-xs sm:grid-cols-2"><div><dt className="font-semibold text-muted">État</dt><dd className="mt-1 text-ink">{inspection.condition || 'Non renseigné'}</dd></div><div><dt className="font-semibold text-muted">Dommages décrits</dt><dd className="mt-1 text-ink">{inspection.existing_damage || 'Aucun renseigné'}</dd></div><div><dt className="font-semibold text-muted">Accessoires</dt><dd className="mt-1 text-ink">{inspection.accessories?.length ? inspection.accessories.join(', ') : 'Aucun renseigné'}</dd></div><div><dt className="font-semibold text-muted">Relevé</dt><dd className="mt-1 text-ink">{inspection.meter_type ? `${inspection.meter_reading} ${inspection.meter_type === 'hours' ? 'heures' : 'km'}` : 'Non pertinent'}</dd></div></dl>{inspection.notes && <p className="mt-3 rounded-control bg-stone-50 p-3 text-xs leading-5 text-muted">{inspection.notes}</p>}{inspection.evidence.length > 0 && <div className="mt-3 flex flex-wrap gap-2">{inspection.evidence.map((evidence) => <a key={evidence.id} href={evidence.file_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 rounded-full border border-border px-3 py-1.5 text-xs font-bold text-primary"><Paperclip className="size-3" />{evidence.original_filename}</a>)}</div>}</Card>)}</div> : <Card className="mt-3"><EmptyState icon={Camera} title="Aucun état des lieux enregistré" description="Aucun rapport d’inspection n’est disponible pour cette réservation." /></Card>}
      </section>

      <section>
        <h3 className="font-display text-lg font-bold text-ink">Messages liés à la réservation</h3>
        <p className="mt-1 text-xs leading-5 text-muted">Historique consulté en lecture seule dans ce dossier.</p>
        {context.messages.length ? <Card className="mt-3 max-h-80 space-y-3 overflow-y-auto bg-stone-50/60 p-4">{context.messages.map((message) => { const mine = String(message.sender_id) === String(currentUser?.id); return <div key={message.id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}><div className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${mine ? 'bg-primary text-white' : 'border border-border bg-white text-ink'}`}><p className="mb-1 text-[10px] font-bold uppercase opacity-70">{mine ? 'Vous' : 'Autre participant'}</p><p>{message.content}</p><p className="mt-1 text-[10px] opacity-70">{new Date(message.created_at).toLocaleString('fr-MA')}</p></div></div>; })}</Card> : <Card className="mt-3"><EmptyState icon={MessageSquare} title="Aucun message lié" description="Aucun échange associé à cette réservation n’est disponible." /></Card>}
      </section>
    </div>
  );
}

export default function DisputeCenter({
  bookings, disputes, currentUser, initialBookingId, loading, error, onRefresh,
}) {
  const [view, setView] = useState('list');
  const [bookingId, setBookingId] = useState('');
  const [reasonCode, setReasonCode] = useState('');
  const [description, setDescription] = useState('');
  const [acknowledged, setAcknowledged] = useState(false);
  const [selected, setSelected] = useState(null);
  const [context, setContext] = useState(null);
  const [busy, setBusy] = useState(false);
  const [uploading, setUploading] = useState(null);
  const [localError, setLocalError] = useState('');
  const fileInputRef = useRef(null);
  const handledInitialBookingRef = useRef(null);

  const eligibleBookings = useMemo(() => bookings.filter((booking) => canOpenDispute(booking, disputes)), [bookings, disputes]);
  const selectedStatus = disputeStatus(selected?.status);
  const currentContributionSubmitted = selected && (
    (String(currentUser?.id) === String(selected.renter_id) && selected.evidence_submitted_by_renter)
    || (String(currentUser?.id) === String(selected.owner_id) && selected.evidence_submitted_by_owner)
  );
  const collectionStage = ['open', 'evidence_collection'].includes(selected?.status);
  const collecting = collectionStage && !currentContributionSubmitted;

  const openDispute = async (dispute) => {
    setView('detail');
    setLocalError('');
    setBusy(true);
    try {
      const [detail, nextContext] = await Promise.all([getDispute(dispute.id), getDisputeContext(dispute.id)]);
      setSelected(detail);
      setContext(nextContext);
    } catch (loadError) {
      setLocalError(loadError.message);
    } finally {
      setBusy(false);
    }
  };

  useEffect(() => {
    if (!initialBookingId || handledInitialBookingRef.current === String(initialBookingId)) return;
    handledInitialBookingRef.current = String(initialBookingId);
    const existing = disputes.find((item) => String(item.booking_id) === String(initialBookingId));
    if (existing) openDispute(existing);
    else {
      setBookingId(String(initialBookingId));
      setView('create');
    }
  }, [initialBookingId]);

  const create = async (event) => {
    event.preventDefault();
    if (!bookingId || !reasonCode || description.trim().length < 20 || !acknowledged || busy) return;
    setBusy(true);
    setLocalError('');
    try {
      const created = await createDispute({ booking_id: bookingId, reason_code: reasonCode, description: description.trim() }, disputeSubmissionKey(bookingId));
      setSelected(created);
      setContext(await getDisputeContext(created.id));
      setView('detail');
      await onRefresh?.();
    } catch (createError) {
      setLocalError(createError.message);
    } finally {
      setBusy(false);
    }
  };

  const upload = async (file) => {
    if (!file || uploading) return;
    if (file.size > MAX_EVIDENCE_BYTES) { setLocalError('Ce fichier dépasse la limite de 25 Mo.'); return; }
    setUploading({ name: file.name, progress: 0 });
    setLocalError('');
    try {
      await uploadDisputeEvidence(selected.id, file, { onProgress: (progress) => setUploading({ name: file.name, progress }) });
      setSelected(await getDispute(selected.id));
      await onRefresh?.();
    } catch (uploadError) {
      setLocalError(uploadError.message);
    } finally {
      setUploading(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const removeEvidence = async (item) => {
    setLocalError('');
    try {
      await deleteDisputeEvidence(item.id);
      setSelected(await getDispute(selected.id));
    } catch (deleteError) {
      setLocalError(deleteError.message);
    }
  };

  const submit = async () => {
    if (busy) return;
    setBusy(true);
    setLocalError('');
    try {
      setSelected(await submitDisputeForReview(selected.id));
      await onRefresh?.();
    } catch (submitError) {
      setLocalError(submitError.message);
    } finally {
      setBusy(false);
    }
  };

  if (view === 'create') return (
    <section>
      <Button variant="ghost" size="sm" onClick={() => setView('list')}><ArrowLeft className="size-4" />Retour aux dossiers</Button>
      <div className="mt-4 max-w-2xl"><h2 className="font-display text-2xl font-bold text-ink">Ouvrir un dossier</h2><p className="mt-2 text-sm leading-6 text-muted">Décrivez les faits avec précision. L’ouverture d’un dossier ne détermine la responsabilité d’aucune partie.</p></div>
      {localError && <div role="alert" className="mt-4 rounded-control border border-error/20 bg-error-subtle p-3 text-sm text-error">{localError}</div>}
      <Card className="mt-5 p-5 sm:p-6"><form onSubmit={create} className="space-y-5"><Select label="Réservation concernée" required value={bookingId} onChange={(event) => setBookingId(event.target.value)} options={[{ value: '', label: 'Choisir une réservation' }, ...eligibleBookings.map((booking) => ({ value: String(booking.id), label: `${booking.article_titre || 'Matériel'} · ${String(booking.id).slice(0, 8).toUpperCase()}` }))]} /><Select label="Motif du dossier" required value={reasonCode} onChange={(event) => setReasonCode(event.target.value)} options={[{ value: '', label: 'Choisir un motif' }, ...DISPUTE_REASONS]} /><Textarea label="Description factuelle" required rows={7} minLength={20} maxLength={5000} value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Indiquez ce qui s’est passé, quand, et les éléments que vous avez constatés…" hint="20 caractères minimum. Évitez les suppositions sur l’intention de l’autre partie." /><Checkbox checked={acknowledged} onChange={(event) => setAcknowledged(event.target.checked)} label="Je confirme que cette description correspond à mes observations" description="L’autre partie pourra consulter le dossier et ajouter ses propres éléments." /><Button type="submit" loading={busy} loadingLabel="Ouverture…" disabled={!bookingId || !reasonCode || description.trim().length < 20 || !acknowledged}>Ouvrir le dossier</Button></form></Card>
    </section>
  );

  if (view === 'detail') return (
    <section>
      <Button variant="ghost" size="sm" onClick={() => { setView('list'); setSelected(null); setContext(null); }}><ArrowLeft className="size-4" />Retour aux dossiers</Button>
      {localError && <div role="alert" className="mt-4 flex items-start gap-2 rounded-control border border-error/20 bg-error-subtle p-3 text-sm text-error"><AlertCircle className="mt-0.5 size-4 shrink-0" />{localError}</div>}
      {busy && !selected ? <div className="mt-5 space-y-3"><Skeleton className="h-28" /><Skeleton className="h-52" /></div> : selected && <div className="mt-5 space-y-6"><div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between"><div><Badge variant={selectedStatus.tone}>{selectedStatus.label}</Badge><h2 className="mt-3 font-display text-2xl font-bold text-ink">{disputeReason(selected.reason_code)}</h2><p className="mt-1 text-xs text-muted">Dossier LK-{String(selected.id).slice(0, 8).toUpperCase()}</p></div><p className="text-xs text-muted">Ouvert le {new Date(selected.created_at).toLocaleString('fr-MA')}</p></div><Stepper steps={DISPUTE_STEPS} current={selectedStatus.step} className="grid-cols-2 sm:grid-cols-5" /><Card className="p-5"><p className="text-xs font-bold uppercase tracking-wide text-muted">Description transmise</p><p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-ink">{selected.description}</p></Card>

      <section><div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><h3 className="font-display text-lg font-bold text-ink">Pièces ajoutées par les participants</h3><p className="mt-1 text-xs leading-5 text-muted">Photos, vidéos et PDF originaux. Chaque fichier reçoit une empreinte SHA-256 calculée par le backend.</p></div>{collecting && <><input ref={fileInputRef} className="hidden" type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/webm,video/quicktime,application/pdf" onChange={(event) => upload(event.target.files?.[0])} /><Button size="sm" variant="secondary" onClick={() => fileInputRef.current?.click()} disabled={Boolean(uploading)}><Upload className="size-4" />Ajouter une pièce</Button></>}</div>{uploading && <Card className="mt-3 p-4"><div className="flex items-center justify-between gap-3 text-xs"><span className="truncate font-bold text-ink">{uploading.name}</span><span className="text-muted">{uploading.progress}%</span></div><div className="mt-2 h-1.5 overflow-hidden rounded-full bg-stone-200"><div className="h-full bg-primary" style={{ width: `${uploading.progress}%` }} /></div></Card>}{selected.evidence.length ? <div className="mt-3 grid gap-3 sm:grid-cols-2">{selected.evidence.map((item) => <EvidencePreview key={item.id} item={item} removable={collecting && String(item.uploaded_by_id) === String(currentUser?.id)} onDelete={removeEvidence} />)}</div> : <Card className="mt-3"><EmptyState icon={Paperclip} title="Aucune pièce ajoutée" description="Vous pouvez terminer votre contribution sans fichier si les états des lieux ou messages contiennent déjà les éléments utiles." /></Card>}<Card className="mt-4 p-4"><p className="text-xs font-bold uppercase tracking-wide text-muted">Contributions</p><div className="mt-3 grid gap-2 text-xs sm:grid-cols-2"><p className="rounded-control bg-stone-50 p-3">Locataire : <strong>{selected.evidence_submitted_by_renter ? 'contribution terminée' : 'collecte en cours'}</strong></p><p className="rounded-control bg-stone-50 p-3">Propriétaire : <strong>{selected.evidence_submitted_by_owner ? 'contribution terminée' : 'collecte en cours'}</strong></p></div></Card>{collecting && <div className="mt-4 rounded-card border border-border bg-stone-50 p-4"><div className="flex items-start gap-3"><ShieldCheck className="mt-0.5 size-5 shrink-0 text-primary" /><div><p className="text-sm font-bold text-ink">Votre contribution est prête ?</p><p className="mt-1 text-xs leading-5 text-muted">Après validation, vos pièces deviennent non modifiables. Le dossier passe à l’examen lorsque les deux parties ont terminé leur contribution. La décision et tout montant éventuel restent sous contrôle du backend et de l’équipe habilitée.</p></div></div><Button className="mt-4 w-full sm:w-auto" loading={busy} loadingLabel="Validation…" onClick={submit}>Terminer ma contribution</Button></div>}{collectionStage && currentContributionSubmitted && <p className="mt-4 rounded-control border border-info/20 bg-info-subtle p-3 text-xs leading-5 text-info">Votre contribution est terminée. La collecte reste ouverte pour l’autre partie.</p>}</section>

      {selected.decision_code && <Card className="border-info/20 bg-info-subtle p-5"><div className="flex items-start gap-3"><Scale className="mt-0.5 size-5 shrink-0 text-info" /><div><p className="text-sm font-bold text-ink">{disputeDecision(selected)}</p><p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-muted">{selected.decision_summary}</p>{selected.deposit_capture_amount_mad != null && <p className="mt-3 text-sm font-bold text-ink">Montant décidé : {money(selected.deposit_capture_amount_mad)}</p>}{disputeDepositStatus(selected.deposit_action_status) && <Badge variant={selected.deposit_action_status === 'confirmed' || selected.deposit_action_status === 'not_applicable' ? 'success' : 'warning'} className="mt-3">{disputeDepositStatus(selected.deposit_action_status)}</Badge>}</div></div></Card>}

      {context ? <ContextPanel context={context} currentUser={currentUser} /> : <ErrorState title="Contexte indisponible" description="Les états des lieux et messages n’ont pas pu être chargés." onRetry={() => openDispute(selected)} />}</div>}
    </section>
  );

  return (
    <section>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between"><div><h2 className="font-display text-xl font-bold text-ink">Dossiers et litiges</h2><p className="mt-1 text-sm leading-6 text-muted">Consultez les éléments, suivez l’examen et retrouvez les décisions sans présumer de la responsabilité.</p></div><Button size="sm" onClick={() => setView('create')} disabled={!eligibleBookings.length}>Ouvrir un dossier</Button></div>
      {error && <div className="mt-4"><ErrorState title="Dossiers indisponibles" description={error} onRetry={onRefresh} /></div>}
      {loading ? <div className="mt-5 space-y-3"><Skeleton className="h-28" /><Skeleton className="h-28" /></div> : disputes.length ? <div className="mt-5 space-y-3">{disputes.map((dispute) => { const status = disputeStatus(dispute.status); return <Card key={dispute.id} className="p-5"><div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"><div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><Badge variant={status.tone}>{status.label}</Badge><span className="text-xs text-muted">LK-{String(dispute.id).slice(0, 8).toUpperCase()}</span></div><h3 className="mt-3 font-display text-lg font-bold text-ink">{disputeReason(dispute.reason_code)}</h3><p className="mt-1 line-clamp-2 text-sm leading-6 text-muted">{dispute.description}</p></div><Button size="sm" variant="secondary" onClick={() => openDispute(dispute)}>Consulter</Button></div></Card>; })}</div> : <Card className="mt-5"><EmptyState icon={CheckCircle2} title="Aucun dossier" description="Aucun litige n’est actuellement associé à vos réservations." action={eligibleBookings.length ? <Button size="sm" onClick={() => setView('create')}>Ouvrir un dossier</Button> : undefined} /></Card>}
    </section>
  );
}
