import React, { useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertCircle, Camera, Check, CheckCircle2, ChevronLeft, ChevronRight,
  Clock3, FileCheck2, Gauge, Hash, PackageCheck, RefreshCw, ShieldCheck,
  Trash2, Upload, Video, X,
} from 'lucide-react';
import {
  confirmInspection, createInspection, deleteInspectionEvidence, getInspectionRequirements,
  getInspections, uploadInspectionEvidence,
} from '../services/api';
import { Badge, Button, Card, Checkbox, Input, Select, Skeleton, Stepper, Textarea, useDialogLayer } from './ui';
import {
  CONDITION_OPTIONS, INSPECTION_STEPS, METER_OPTIONS, currentUserHasConfirmed,
  inspectionConditionLabel, inspectionPayload, inspectionSubmissionKey,
  inspectionTypeLabel, validateInspectionStep,
} from './inspection/inspectionExperience';


function bytesLabel(value) {
  const bytes = Number(value) || 0;
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
  return `${Math.max(1, Math.round(bytes / 1024))} Ko`;
}


function EvidenceCard({ item, onRetry, onDelete }) {
  const isVideo = item.file?.type?.startsWith('video/') || item.record?.media_kind === 'video';
  return (
    <Card className="overflow-hidden">
      <div className="relative flex aspect-[16/10] items-center justify-center bg-stone-100">
        {item.preview && !isVideo && <img src={item.preview} alt={item.file?.name || 'Preuve photographique'} className="size-full object-cover" />}
        {isVideo && <Video aria-hidden="true" className="size-9 text-muted" />}
        <Badge variant={isVideo ? 'info' : 'neutral'} className="absolute start-2 top-2">{isVideo ? 'Vidéo' : 'Photo'}</Badge>
      </div>
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0"><p className="truncate text-xs font-bold text-ink">{item.file?.name || item.record?.original_filename}</p><p className="mt-0.5 text-[11px] text-muted">{bytesLabel(item.file?.size || item.record?.size_bytes)}</p></div>
          <Button variant="ghost" size="icon" className="size-8 text-error" onClick={() => onDelete(item)} aria-label="Supprimer la preuve"><Trash2 className="size-4" /></Button>
        </div>
        {item.status === 'uploading' && <div className="mt-3"><div className="mb-1 flex justify-between text-[11px] font-semibold text-muted"><span>Importation de l’original…</span><span>{item.progress}%</span></div><div className="h-1.5 overflow-hidden rounded-full bg-stone-200"><div className="h-full rounded-full bg-primary transition-all" style={{ width: `${item.progress}%` }} /></div></div>}
        {item.status === 'uploaded' && <div className="mt-2 space-y-1"><p className="flex items-center gap-1 text-[11px] font-bold text-success"><Check className="size-3.5" />Original stocké</p><p className="flex items-center gap-1 truncate font-mono text-[10px] text-muted" title={item.record.sha256_hash}><Hash className="size-3 shrink-0" />{item.record.sha256_hash}</p></div>}
        {item.status === 'failed' && <div className="mt-2"><p className="text-[11px] font-semibold text-error">{item.error}</p><Button variant="secondary" size="sm" className="mt-2" onClick={() => onRetry(item)}><RefreshCw className="size-3.5" />Réessayer</Button></div>}
      </div>
    </Card>
  );
}


function RecordedEvidenceCard({ item }) {
  const isVideo = item.media_kind === 'video';
  return (
    <Card className="overflow-hidden">
      <div className="flex aspect-[16/10] items-center justify-center bg-stone-100">
        {isVideo
          ? <video src={item.file_url} controls preload="metadata" className="size-full bg-black object-contain" aria-label={`Preuve vidéo ${item.original_filename}`} />
          : <img src={item.file_url} alt={`Preuve ${item.original_filename}`} className="size-full object-contain" />}
      </div>
      <div className="p-3">
        <div className="flex items-start justify-between gap-2">
          <div className="min-w-0"><p className="truncate text-xs font-bold text-ink">{item.original_filename}</p><p className="mt-1 text-[11px] text-muted">{bytesLabel(item.size_bytes)} · reçu le {new Date(item.stored_at).toLocaleString('fr-MA')}</p></div>
          <Badge variant={isVideo ? 'info' : 'neutral'}>{isVideo ? 'Vidéo' : 'Photo'}</Badge>
        </div>
        <p className="mt-2 break-all font-mono text-[10px] leading-4 text-muted">SHA-256 · {item.sha256_hash}</p>
        <a href={item.file_url} target="_blank" rel="noreferrer" className="mt-2 inline-flex text-xs font-bold text-primary hover:underline">Ouvrir le fichier original</a>
      </div>
    </Card>
  );
}


function InspectionRecord({ inspection, currentUser, confirming, acknowledged, onAcknowledged, onConfirm, onClose }) {
  const confirmed = inspection.status === 'confirmed';
  const alreadyConfirmed = currentUserHasConfirmed(inspection, currentUser?.id);
  return (
    <div className="space-y-5">
      <div className={`rounded-card border p-4 ${confirmed ? 'border-success/20 bg-success-subtle' : 'border-warning/20 bg-warning-subtle'}`}>
        <div className="flex items-start gap-3"><span className={`flex size-10 shrink-0 items-center justify-center rounded-xl bg-white ${confirmed ? 'text-success' : 'text-warning'}`}>{confirmed ? <CheckCircle2 className="size-5" /> : <Clock3 className="size-5" />}</span><div><Badge variant={confirmed ? 'success' : 'warning'}>{confirmed ? 'Confirmé par les deux parties' : 'Confirmation de l’autre partie attendue'}</Badge><p className="mt-2 text-sm leading-6 text-ink">Enregistré le {new Date(inspection.recorded_at).toLocaleString('fr-MA')} pour la réservation LK-{String(inspection.reservation_id).slice(0, 8).toUpperCase()}.</p></div></div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card className="p-4"><p className="text-xs font-bold uppercase tracking-wide text-muted">État constaté</p><p className="mt-2 text-sm font-bold text-ink">{inspectionConditionLabel(inspection.condition)}</p>{inspection.existing_damage && <p className="mt-2 text-xs leading-5 text-muted">Dommages existants : {inspection.existing_damage}</p>}</Card>
        <Card className="p-4"><p className="text-xs font-bold uppercase tracking-wide text-muted">Confirmations</p><p className="mt-2 text-xs text-ink">Propriétaire : {inspection.confirmed_by_owner ? 'confirmé' : 'en attente'}</p><p className="mt-1 text-xs text-ink">Locataire : {inspection.confirmed_by_renter ? 'confirmé' : 'en attente'}</p></Card>
      </div>

      <Card className="p-4">
        <p className="text-xs font-bold uppercase tracking-wide text-muted">Détails relevés</p>
        <dl className="mt-3 grid gap-3 text-xs sm:grid-cols-2">
          <div><dt className="font-semibold text-muted">Accessoires</dt><dd className="mt-1 text-ink">{inspection.accessories?.length ? inspection.accessories.join(', ') : 'Aucun renseigné'}</dd></div>
          <div><dt className="font-semibold text-muted">Numéro de série</dt><dd className="mt-1 text-ink">{inspection.serial_number || 'Non pertinent ou non visible'}</dd></div>
          <div><dt className="font-semibold text-muted">Compteur</dt><dd className="mt-1 text-ink">{inspection.meter_type ? `${inspection.meter_reading} ${inspection.meter_type === 'hours' ? 'heures' : 'km'}` : 'Non pertinent'}</dd></div>
          <div><dt className="font-semibold text-muted">Notes</dt><dd className="mt-1 text-ink">{inspection.notes || 'Aucune note'}</dd></div>
        </dl>
      </Card>

      <section><p className="text-xs font-bold uppercase tracking-wide text-muted">Preuves originales</p><div className="mt-3 grid gap-3 sm:grid-cols-2">{inspection.evidence.map((item) => <RecordedEvidenceCard key={item.id} item={item} />)}</div></section>

      {!confirmed && !alreadyConfirmed && <div className="rounded-card border border-border p-4"><Checkbox checked={acknowledged} onChange={(event) => onAcknowledged(event.target.checked)} label="Je confirme que ce rapport correspond à l’état constaté" description="Votre confirmation est enregistrée par le backend. Elle ne constitue pas une signature électronique qualifiée." /><Button className="mt-4 w-full" disabled={!acknowledged} loading={confirming} loadingLabel="Confirmation…" onClick={onConfirm}>Confirmer ce rapport</Button></div>}
      {!confirmed && alreadyConfirmed && <p className="rounded-control bg-stone-50 p-3 text-xs leading-5 text-muted">Vous avez confirmé ce rapport. L’autre partie doit maintenant le vérifier.</p>}
      <Button variant="secondary" className="w-full" onClick={onClose}>Fermer</Button>
    </div>
  );
}


export default function InspectionModal({ isOpen, onClose, booking, type = 'check_in', currentUser, onInspectionSuccess }) {
  const [step, setStep] = useState(0);
  const [requirements, setRequirements] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [condition, setCondition] = useState('');
  const [existingDamage, setExistingDamage] = useState('');
  const [accessories, setAccessories] = useState('');
  const [serialRelevant, setSerialRelevant] = useState(false);
  const [serialNumber, setSerialNumber] = useState('');
  const [meterType, setMeterType] = useState('none');
  const [meterReading, setMeterReading] = useState('');
  const [notes, setNotes] = useState('');
  const [confirmed, setConfirmed] = useState(false);
  const [existingInspection, setExistingInspection] = useState(null);
  const [counterpartyAcknowledged, setCounterpartyAcknowledged] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState('');
  const photoInputRef = useRef(null);
  const videoInputRef = useRef(null);
  const submittingRef = useRef(false);
  const evidenceRef = useRef([]);
  const dialogRef = useRef(null);
  useDialogLayer(Boolean(isOpen && booking), onClose, dialogRef);

  const normalizedType = type === 'check_out' ? 'check_out' : 'check_in';
  const uploaded = useMemo(() => evidence.filter((item) => item.status === 'uploaded' && item.record), [evidence]);

  useEffect(() => {
    if (!isOpen || !booking?.id) return undefined;
    let active = true;
    setLoading(true);
    setError('');
    Promise.all([getInspectionRequirements(booking.id, normalizedType), getInspections(booking.id)])
      .then(([nextRequirements, inspections]) => {
        if (!active) return;
        setRequirements(nextRequirements);
        setExistingInspection((inspections || []).find((item) => item.inspection_type === normalizedType) || null);
      })
      .catch((loadError) => active && setError(loadError.message))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [isOpen, booking?.id, normalizedType]);

  useEffect(() => {
    evidenceRef.current = evidence;
  }, [evidence]);

  useEffect(() => () => {
    evidenceRef.current.forEach((item) => {
      item.controller?.abort();
      if (item.preview) URL.revokeObjectURL(item.preview);
    });
  }, []);

  if (!isOpen || !booking) return null;

  const updateEvidence = (localId, patch) => setEvidence((items) => items.map((item) => item.localId === localId ? { ...item, ...patch } : item));

  const uploadFile = async (item) => {
    const controller = new AbortController();
    updateEvidence(item.localId, { status: 'uploading', progress: 0, error: '', controller });
    try {
      const record = await uploadInspectionEvidence(booking.id, normalizedType, item.file, {
        signal: controller.signal,
        onProgress: (progress) => updateEvidence(item.localId, { progress }),
      });
      updateEvidence(item.localId, { status: 'uploaded', progress: 100, record, controller: null });
    } catch (uploadError) {
      if (uploadError.code !== 'REQUEST_CANCELLED') updateEvidence(item.localId, { status: 'failed', progress: 0, error: uploadError.message, controller: null });
    }
  };

  const addFiles = async (files, kind) => {
    setError('');
    const selected = Array.from(files || []);
    const currentCount = evidence.filter((item) => item.file?.type?.startsWith(`${kind}/`)).length;
    const limit = kind === 'image' ? 10 : 1;
    const maxBytes = kind === 'image'
      ? (requirements?.photo_max_bytes || 12 * 1024 * 1024)
      : (requirements?.video_max_bytes || 100 * 1024 * 1024);
    for (const file of selected.slice(0, Math.max(0, limit - currentCount))) {
      if (file.size > maxBytes) {
        setError(`${file.name} dépasse la limite de ${bytesLabel(maxBytes)}.`);
        continue;
      }
      const localId = globalThis.crypto?.randomUUID?.() || `evidence-${Date.now()}-${Math.random()}`;
      const item = { localId, file, preview: URL.createObjectURL(file), status: 'uploading', progress: 0, record: null, error: '' };
      setEvidence((current) => [...current, item]);
      await uploadFile(item);
    }
  };

  const removeEvidence = async (item) => {
    item.controller?.abort();
    if (item.record?.id) {
      try { await deleteInspectionEvidence(item.record.id); } catch (deleteError) { setError(deleteError.message); return; }
    }
    if (item.preview) URL.revokeObjectURL(item.preview);
    setEvidence((items) => items.filter((entry) => entry.localId !== item.localId));
  };

  const next = () => {
    const validation = validateInspectionStep(step, {
      evidence, requirements, condition, serialRelevant, serialNumber,
      meterType, meterReading, confirmed,
    });
    if (validation) { setError(validation); return; }
    setError('');
    setStep((current) => Math.min(INSPECTION_STEPS.length - 1, current + 1));
  };

  const submit = async () => {
    if (submittingRef.current) return;
    const validation = validateInspectionStep(3, {
      evidence, requirements, condition, serialRelevant, serialNumber,
      meterType, meterReading, confirmed,
    });
    if (validation) { setError(validation); return; }
    submittingRef.current = true;
    setSubmitting(true);
    setError('');
    try {
      const payload = inspectionPayload({ bookingId: booking.id, type: normalizedType, evidence, condition, existingDamage, accessories, serialNumber: serialRelevant ? serialNumber : '', meterType, meterReading, notes });
      const report = await createInspection(payload, inspectionSubmissionKey(booking.id, normalizedType));
      setExistingInspection(report);
      onInspectionSuccess?.(booking.id, normalizedType);
    } catch (submitError) {
      setError(submitError.message);
    } finally {
      submittingRef.current = false;
      setSubmitting(false);
    }
  };

  const confirmExisting = async () => {
    if (!counterpartyAcknowledged || confirming) return;
    setConfirming(true);
    setError('');
    try {
      const report = await confirmInspection(existingInspection.id);
      setExistingInspection(report);
      onInspectionSuccess?.(booking.id, normalizedType);
    } catch (confirmationError) {
      setError(confirmationError.message);
    } finally {
      setConfirming(false);
    }
  };

  const renderStep = () => {
    if (step === 0) return <section><h2 className="font-display text-xl font-bold text-ink">Ajoutez les preuves originales</h2><p className="mt-1 text-sm leading-6 text-muted">Prenez au moins {requirements?.minimum_photos || 3} photos nettes : vue générale, côtés, commandes et défauts. Les fichiers originaux sont stockés avant calcul de leur SHA-256.</p><div className="mt-4 grid gap-3 sm:grid-cols-2"><input ref={photoInputRef} className="hidden" type="file" accept="image/jpeg,image/png,image/webp" capture="environment" multiple onChange={(event) => addFiles(event.target.files, 'image')} /><button type="button" onClick={() => photoInputRef.current?.click()} className="flex min-h-28 flex-col items-center justify-center rounded-card border-2 border-dashed border-border bg-stone-50 p-4 text-center"><Camera className="size-6 text-primary" /><span className="mt-2 text-sm font-bold text-ink">Ajouter des photos</span><span className="mt-1 text-xs text-muted">JPEG, PNG ou WebP · {bytesLabel(requirements?.photo_max_bytes || 12 * 1024 * 1024)} max</span></button><input ref={videoInputRef} className="hidden" type="file" accept="video/mp4,video/webm,video/quicktime" capture="environment" onChange={(event) => addFiles(event.target.files, 'video')} /><button type="button" onClick={() => videoInputRef.current?.click()} className="flex min-h-28 flex-col items-center justify-center rounded-card border-2 border-dashed border-border bg-stone-50 p-4 text-center"><Video className="size-6 text-primary" /><span className="mt-2 text-sm font-bold text-ink">Ajouter une vidéo {requirements?.video_required ? '(requise)' : '(optionnelle)'}</span><span className="mt-1 text-xs text-muted">MP4, MOV ou WebM · {bytesLabel(requirements?.video_max_bytes || 100 * 1024 * 1024)} max</span></button></div>{evidence.length > 0 && <div className="mt-4 grid gap-3 sm:grid-cols-2">{evidence.map((item) => <EvidenceCard key={item.localId} item={item} onRetry={uploadFile} onDelete={removeEvidence} />)}</div>}</section>;
    if (step === 1) return <section><h2 className="font-display text-xl font-bold text-ink">Décrivez l’état constaté</h2><p className="mt-1 text-sm text-muted">Utilisez les mêmes critères au check-in et au check-out.</p><div className="mt-4 grid gap-2 sm:grid-cols-2">{CONDITION_OPTIONS.map((option) => <label key={option.value} className={`flex min-h-12 cursor-pointer items-center gap-3 rounded-control border p-3 ${condition === option.value ? 'border-primary bg-primary-subtle' : 'border-border'}`}><input type="radio" name="inspection-condition" value={option.value} checked={condition === option.value} onChange={() => setCondition(option.value)} /><span className="text-sm font-bold text-ink">{option.label}</span></label>)}</div><Textarea className="mt-4" label={normalizedType === 'check_in' ? 'Dommages déjà présents' : 'Dommages ou changements constatés'} rows={5} value={existingDamage} onChange={(event) => setExistingDamage(event.target.value)} placeholder="Décrivez précisément les rayures, fissures, pièces manquantes ou autres défauts…" maxLength={3000} /><Input className="mt-4" label="Accessoires présents" value={accessories} onChange={(event) => setAccessories(event.target.value)} placeholder="Ex. chargeur, batterie, câble, mallette" hint="Séparez les accessoires par une virgule." /></section>;
    if (step === 2) return <section><h2 className="font-display text-xl font-bold text-ink">Identifiants et relevés</h2><p className="mt-1 text-sm text-muted">Renseignez uniquement ce qui est pertinent pour ce matériel.</p><div className="mt-4 space-y-4"><Checkbox checked={serialRelevant} onChange={(event) => setSerialRelevant(event.target.checked)} label="Un numéro de série est visible" description="Il aide à confirmer qu’il s’agit du même équipement au retour." />{serialRelevant && <Input label="Numéro de série" required value={serialNumber} onChange={(event) => setSerialNumber(event.target.value)} maxLength={150} />}<Select label="Compteur pertinent" value={meterType} onChange={(event) => setMeterType(event.target.value)} options={METER_OPTIONS} />{meterType !== 'none' && <Input label={meterType === 'hours' ? 'Nombre d’heures' : 'Kilométrage'} type="number" min="0" step="0.01" required value={meterReading} onChange={(event) => setMeterReading(event.target.value)} leadingIcon={Gauge} />}<Textarea label="Notes complémentaires" rows={5} value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Propreté, niveau de carburant, comportement au démarrage, éléments à surveiller…" maxLength={3000} /></div></section>;
    return <section><h2 className="font-display text-xl font-bold text-ink">Vérifiez et confirmez</h2><div className="mt-4 grid gap-3 sm:grid-cols-2"><Card className="p-4"><p className="text-xs font-bold uppercase text-muted">Inspection</p><p className="mt-2 text-sm font-bold text-ink">{inspectionTypeLabel(normalizedType)}</p><p className="mt-1 text-xs text-muted">{booking.article_titre || booking.equipment_title || 'Équipement'}</p></Card><Card className="p-4"><p className="text-xs font-bold uppercase text-muted">État</p><p className="mt-2 text-sm font-bold text-ink">{inspectionConditionLabel(condition)}</p><p className="mt-1 text-xs text-muted">{uploaded.filter((item) => item.record.media_kind === 'photo').length} photos · {uploaded.filter((item) => item.record.media_kind === 'video').length} vidéo</p></Card></div><Card className="mt-3 p-4"><div className="flex items-start gap-3"><ShieldCheck className="mt-0.5 size-5 shrink-0 text-primary" /><div><p className="text-sm font-bold text-ink">Ce que Lokiini enregistrera</p><p className="mt-1 text-xs leading-5 text-muted">Réservation, matériel, propriétaire, locataire, type d’inspection, auteur, heure de réception et empreinte SHA-256 calculée à partir de chaque fichier original.</p><p className="mt-2 text-xs leading-5 text-muted">Aucune autorité d’horodatage externe ni signature électronique qualifiée n’est revendiquée.</p></div></div></Card><Checkbox className="mt-4" checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} label="Je confirme l’exactitude de ce rapport" description="L’autre partie devra le vérifier séparément avant la clôture de cette étape." /></section>;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center sm:p-4" role="dialog" aria-modal="true" aria-label={inspectionTypeLabel(normalizedType)}>
      <div ref={dialogRef} tabIndex="-1" className="flex max-h-[100dvh] w-full flex-col overflow-hidden rounded-t-3xl border border-border bg-white shadow-2xl sm:max-h-[92vh] sm:max-w-3xl sm:rounded-3xl">
        <div className="shrink-0 flex items-start justify-between gap-3 border-b border-border p-4 sm:p-5"><div><Badge variant={normalizedType === 'check_in' ? 'primary' : 'warning'}>{inspectionTypeLabel(normalizedType)}</Badge><h1 className="mt-2 font-display text-xl font-bold text-ink">État du matériel</h1></div><Button variant="ghost" size="icon" onClick={onClose} aria-label="Fermer"><X className="size-5" /></Button></div>
        <div className="min-h-0 overflow-y-auto overscroll-contain p-4 pb-[max(1rem,env(safe-area-inset-bottom))] sm:p-6">
          {error && <div role="alert" className="mb-4 flex items-start gap-2 rounded-control border border-error/20 bg-error-subtle p-3 text-xs font-semibold text-error"><AlertCircle className="mt-0.5 size-4 shrink-0" />{error}</div>}
          {loading ? <div className="space-y-3"><Skeleton className="h-20" /><Skeleton className="h-40" /></div> : existingInspection ? <InspectionRecord inspection={existingInspection} currentUser={currentUser} confirming={confirming} acknowledged={counterpartyAcknowledged} onAcknowledged={setCounterpartyAcknowledged} onConfirm={confirmExisting} onClose={onClose} /> : <><Stepper steps={INSPECTION_STEPS.map((label) => ({ label }))} current={step} className="mb-6 grid-cols-2 sm:grid-cols-4" />{renderStep()}<div className="sticky bottom-0 mt-6 flex gap-3 border-t border-border bg-white pt-4"><Button variant="secondary" className="flex-1" disabled={step === 0 || submitting} onClick={() => { setError(''); setStep((current) => current - 1); }}><ChevronLeft className="size-4" />Retour</Button>{step < INSPECTION_STEPS.length - 1 ? <Button className="flex-1" onClick={next}>Continuer<ChevronRight className="size-4" /></Button> : <Button className="flex-1" loading={submitting} loadingLabel="Enregistrement…" onClick={submit}><FileCheck2 className="size-4" />Envoyer le rapport</Button>}</div></>}
        </div>
      </div>
    </div>
  );
}
