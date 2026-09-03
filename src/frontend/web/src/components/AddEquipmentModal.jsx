import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  AlertCircle, ArrowLeft, ArrowRight, Check, ChevronLeft, ChevronRight,
  ImagePlus, MapPin, Package, Plus, RefreshCw, ShieldCheck, Trash2, Truck, Upload,
} from 'lucide-react';
import { createEquipment, deleteEquipmentPhoto, uploadEquipmentPhoto } from '../services/api';
import {
  Badge, Button, Card, Checkbox, Input, Modal, PriceDisplay, Select, Switch, Textarea,
} from './ui';
import {
  CATEGORY_OPTIONS, CITY_OPTIONS, PUBLISHING_STEPS, buildEquipmentPayload,
  compressEquipmentPhoto, createEmptyListing, validateCompleteListing, validatePublishingStep,
} from './equipmentPublishing';
import { useI18n } from '../i18n';

const PUBLISHING_STEP_KEYS = ['category', 'information', 'photos', 'description', 'specifications', 'location', 'price', 'deposit', 'availability', 'handover', 'rules', 'preview', 'publish'];

const CONDITION_OPTIONS = [
  { value: 'neuf', label: 'Comme neuf' },
  { value: 'tres_bon', label: 'Très bon état' },
  { value: 'bon', label: 'Bon état' },
  { value: 'usage', label: 'État d’usage' },
];

const CATEGORY_ICONS = {
  tools: Package, btp: Package, audiovisual: ImagePlus, event: Package, outdoor: Package,
  cleaning: Package, energy: Package, transport: Truck, vehicles: Truck, hightech: Package,
  medical: ShieldCheck,
};

function bytesLabel(value) {
  const bytes = Number(value);
  if (!Number.isFinite(bytes)) return '';
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} Ko`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
}

function StepHeading({ eyebrow, title, description }) {
  return (
    <div className="mb-6">
      <p className="text-xs font-bold uppercase tracking-[0.15em] text-primary">{eyebrow}</p>
      <h3 className="mt-1 font-display text-2xl font-bold text-ink">{title}</h3>
      {description && <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>}
    </div>
  );
}

function FieldError({ children }) {
  if (!children) return null;
  return <p role="alert" tabIndex="-1" className="mt-2 text-xs font-semibold text-error">{children}</p>;
}

function ProgressSteps({ current, maxVisited, onSelect }) {
  const { t, formatNumber } = useI18n();
  return (
    <ol aria-label={t('publish.progressAria')} className="space-y-1">
      {PUBLISHING_STEPS.map((label, index) => {
        const active = current === index;
        const complete = index < current;
        const available = index <= maxVisited;
        return (
          <li key={label}>
            <button
              type="button"
              disabled={!available}
              aria-current={active ? 'step' : undefined}
              onClick={() => onSelect(index)}
              className={`flex min-h-11 w-full items-center gap-3 rounded-lg px-2.5 text-start text-xs font-bold transition ${active ? 'bg-primary-subtle text-primary' : available ? 'text-muted hover:bg-stone-100 hover:text-ink' : 'cursor-not-allowed text-slate-300'}`}
            >
              <span className={`flex size-6 shrink-0 items-center justify-center rounded-full border text-[10px] ${complete ? 'border-primary bg-primary text-white' : active ? 'border-primary bg-white text-primary' : 'border-border bg-white'}`}>
                {complete ? <Check aria-hidden="true" className="size-3.5" /> : formatNumber(index + 1)}
              </span>
              <span className="truncate">{t(`publish.steps.${PUBLISHING_STEP_KEYS[index]}`, {}, label)}</span>
            </button>
          </li>
        );
      })}
    </ol>
  );
}

export default function AddEquipmentModal({ isOpen, onClose, onEquipmentAdded }) {
  const { t, cityLabel, formatMAD, formatNumber } = useI18n();
  const [step, setStep] = useState(0);
  const [maxVisited, setMaxVisited] = useState(0);
  const [listing, setListing] = useState(createEmptyListing);
  const [photos, setPhotos] = useState([]);
  const [errors, setErrors] = useState({});
  const [globalError, setGlobalError] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [published, setPublished] = useState(null);
  const fileInputRef = useRef(null);
  const photosRef = useRef([]);
  const publishRef = useRef(false);

  useEffect(() => { photosRef.current = photos; }, [photos]);

  useEffect(() => () => {
    photosRef.current.forEach((photo) => {
      photo.controller?.abort();
      if (photo.preview?.startsWith('blob:')) URL.revokeObjectURL(photo.preview);
    });
  }, []);

  const updateListing = (field, value) => {
    setListing((current) => ({ ...current, [field]: value }));
    setErrors((current) => ({ ...current, [field]: undefined }));
  };

  const updatePhoto = useCallback((photoId, changes) => {
    setPhotos((current) => current.map((photo) => (
      photo.id === photoId ? { ...photo, ...changes } : photo
    )));
  }, []);

  const resetWizard = useCallback(() => {
    photosRef.current.forEach((photo) => {
      photo.controller?.abort();
      if (photo.preview?.startsWith('blob:')) URL.revokeObjectURL(photo.preview);
    });
    setStep(0);
    setMaxVisited(0);
    setListing(createEmptyListing());
    setPhotos([]);
    setErrors({});
    setGlobalError('');
    setPublishing(false);
    setPublished(null);
    publishRef.current = false;
  }, []);

  const cleanupRemotePhotos = useCallback(() => {
    const uploaded = photosRef.current.filter((photo) => photo.filename);
    return Promise.allSettled(uploaded.map((photo) => deleteEquipmentPhoto(photo.filename)));
  }, []);

  const requestClose = useCallback(() => {
    if (publishing) return;
    const hasWork = photosRef.current.length > 0 || listing.title || listing.description || listing.dailyPrice;
    if (!published && hasWork && !window.confirm(t('publish.confirmClose'))) return;
    if (!published) cleanupRemotePhotos();
    resetWizard();
    onClose();
  }, [cleanupRemotePhotos, listing.dailyPrice, listing.description, listing.title, onClose, published, publishing, resetWizard, t]);

  const uploadPreparedPhoto = useCallback(async (photoId, file) => {
    const controller = new AbortController();
    updatePhoto(photoId, { file, controller, status: 'uploading', progress: 0, error: '' });
    try {
      const uploaded = await uploadEquipmentPhoto(file, {
        signal: controller.signal,
        onProgress: (progress) => updatePhoto(photoId, { progress }),
      });
      updatePhoto(photoId, {
        status: 'uploaded', progress: 100, url: uploaded.url, filename: uploaded.filename,
        uploadedBytes: uploaded.size_bytes, controller: null,
      });
    } catch (error) {
      if (error.code !== 'REQUEST_CANCELLED') {
        updatePhoto(photoId, { status: 'failed', progress: 0, error: error.message, controller: null });
      }
    }
  }, [updatePhoto]);

  const addFiles = async (event) => {
    const selected = Array.from(event.target.files || []);
    event.target.value = '';
    setErrors((current) => ({ ...current, photos: undefined }));
    setGlobalError('');
    const remaining = Math.max(0, 8 - photosRef.current.length);
    if (selected.length > remaining) setGlobalError(`Vous pouvez publier au maximum 8 photos. ${remaining} emplacement${remaining > 1 ? 's restent' : ' reste'}.`);
    const accepted = selected.slice(0, remaining);
    for (const original of accepted) {
      const photoId = globalThis.crypto?.randomUUID?.() || `photo-${Date.now()}-${Math.random()}`;
      const originalPreview = URL.createObjectURL(original);
      setPhotos((current) => [...current, {
        id: photoId, file: original, preview: originalPreview, status: 'compressing',
        progress: 0, originalBytes: original.size, error: '', url: null, filename: null,
      }]);
      try {
        const compressed = await compressEquipmentPhoto(original);
        const compressedPreview = compressed === original ? originalPreview : URL.createObjectURL(compressed);
        if (compressedPreview !== originalPreview) URL.revokeObjectURL(originalPreview);
        updatePhoto(photoId, { file: compressed, preview: compressedPreview, compressedBytes: compressed.size });
        await uploadPreparedPhoto(photoId, compressed);
      } catch (error) {
        updatePhoto(photoId, { status: 'failed', error: error.message, progress: 0 });
      }
    }
  };

  const retryPhoto = async (photo) => {
    if (!photo.file) return;
    setGlobalError('');
    await uploadPreparedPhoto(photo.id, photo.file);
  };

  const removePhoto = async (photo) => {
    photo.controller?.abort();
    updatePhoto(photo.id, { status: 'deleting' });
    if (photo.filename) {
      try { await deleteEquipmentPhoto(photo.filename); } catch (error) { setGlobalError(`La photo a été retirée de l’annonce, mais son nettoyage a échoué : ${error.message}`); }
    }
    if (photo.preview?.startsWith('blob:')) URL.revokeObjectURL(photo.preview);
    setPhotos((current) => current.filter((item) => item.id !== photo.id));
  };

  const movePhoto = (index, direction) => {
    setPhotos((current) => {
      const target = index + direction;
      if (target < 0 || target >= current.length) return current;
      const reordered = [...current];
      [reordered[index], reordered[target]] = [reordered[target], reordered[index]];
      return reordered;
    });
  };

  const goNext = () => {
    const stepErrors = validatePublishingStep(step, listing, photos);
    setErrors(stepErrors);
    setGlobalError('');
    if (Object.keys(stepErrors).length) {
      requestAnimationFrame(() => document.querySelector('[role="dialog"] [aria-invalid="true"], [role="dialog"] [role="alert"]')?.focus());
      return;
    }
    const next = Math.min(PUBLISHING_STEPS.length - 1, step + 1);
    setStep(next);
    setMaxVisited((current) => Math.max(current, next));
  };

  const publish = async () => {
    if (publishRef.current || publishing) return;
    const validation = validateCompleteListing(listing, photos);
    if (Object.keys(validation).length) {
      setErrors(validation);
      const firstInvalid = Array.from({ length: 13 }, (_, index) => index)
        .find((index) => Object.keys(validatePublishingStep(index, listing, photos)).length > 0);
      setStep(firstInvalid ?? 0);
      setGlobalError('Corrigez les informations signalées avant de publier.');
      requestAnimationFrame(() => requestAnimationFrame(() => document.querySelector('[role="dialog"] [aria-invalid="true"], [role="dialog"] [role="alert"]')?.focus()));
      return;
    }
    publishRef.current = true;
    setPublishing(true);
    setGlobalError('');
    try {
      const created = await createEquipment(buildEquipmentPayload(listing, photos));
      setPublished(created);
      onEquipmentAdded?.(created);
    } catch (error) {
      setGlobalError(`Publication impossible : ${error.message}`);
    } finally {
      publishRef.current = false;
      setPublishing(false);
    }
  };

  const specifications = listing.specifications;
  const categoryOption = CATEGORY_OPTIONS.find((item) => item.value === listing.category);
  const categoryLabel = t(`category.${listing.category}`, {}, categoryOption?.label || t('catalogue.category'));

  const renderStep = () => {
    if (published) {
      return (
        <div className="flex min-h-[430px] flex-col items-center justify-center px-4 text-center">
          <span className="flex size-16 items-center justify-center rounded-full bg-success-subtle text-success"><Check aria-hidden="true" className="size-8" /></span>
          <h3 className="mt-5 font-display text-3xl font-bold text-ink">Annonce publiée</h3>
          <p className="mt-3 max-w-lg text-sm leading-6 text-muted">Le backend Lokiini a confirmé la publication. Votre matériel peut maintenant apparaître dans le catalogue et recevoir des demandes.</p>
          <p className="mt-3 text-xs font-semibold text-muted">Référence : {published.article_id}</p>
        </div>
      );
    }

    if (step === 0) return (
      <section>
        <StepHeading eyebrow="Étape 1 sur 13" title="Choisissez la catégorie" description="Une catégorie précise aide les locataires à trouver le matériel adapté." />
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {CATEGORY_OPTIONS.map((category) => {
            const Icon = CATEGORY_ICONS[category.value] || Package;
            const selected = listing.category === category.value;
            return <button key={category.value} type="button" onClick={() => updateListing('category', category.value)} className={`flex min-h-20 items-center gap-3 rounded-card border-2 p-4 text-start transition ${selected ? 'border-primary bg-primary-subtle' : 'border-border bg-white hover:border-primary/30'}`}><span className={`flex size-10 items-center justify-center rounded-xl ${selected ? 'bg-primary text-white' : 'bg-stone-100 text-muted'}`}><Icon aria-hidden="true" className="size-5" /></span><span className="text-sm font-bold text-ink">{t(`category.${category.value}`, {}, category.label)}</span></button>;
          })}
        </div>
        <FieldError>{errors.category}</FieldError>
      </section>
    );

    if (step === 1) return (
      <section>
        <StepHeading eyebrow="Étape 2 sur 13" title="Informations essentielles" description="Utilisez un titre concret avec le type, la marque et le modèle lorsque vous les connaissez." />
        <div className="space-y-5">
          <Input label="Titre de l’annonce" required value={listing.title} onChange={(event) => updateListing('title', event.target.value)} placeholder="Ex. Perforateur Bosch GBH 8-45 DV" error={errors.title} maxLength={255} />
          <Select label="État actuel" required value={listing.condition} onChange={(event) => updateListing('condition', event.target.value)} options={CONDITION_OPTIONS.map((option) => ({ ...option, label: t(`publish.condition.${option.value}`, {}, option.label) }))} placeholder="Choisir l’état" error={errors.condition} />
        </div>
      </section>
    );

    if (step === 2) return (
      <section>
        <StepHeading eyebrow="Étape 3 sur 13" title="Ajoutez de vraies photos" description="Jusqu’à 8 images. Les grandes photos sont compressées dans le navigateur puis envoyées au stockage Lokiini." />
        <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" multiple className="hidden" onChange={addFiles} />
        <button type="button" onClick={() => fileInputRef.current?.click()} disabled={photos.length >= 8} className="flex min-h-36 w-full flex-col items-center justify-center rounded-card border-2 border-dashed border-border bg-stone-50 p-5 text-center transition hover:border-primary hover:bg-primary-subtle disabled:cursor-not-allowed disabled:opacity-50">
          <span className="flex size-12 items-center justify-center rounded-xl bg-primary-subtle text-primary"><Upload aria-hidden="true" className="size-6" /></span>
          <span className="mt-3 text-sm font-bold text-ink">Sélectionner des photos</span>
          <span className="mt-1 text-xs text-muted">JPEG, PNG ou WebP · 12 Mo maximum avant compression</span>
        </button>
        <FieldError>{errors.photos}</FieldError>
        {photos.length > 0 && <div className="mt-5 grid gap-3 sm:grid-cols-2">{photos.map((photo, index) => <Card key={photo.id} className="overflow-hidden"><div className="relative aspect-[16/10] bg-stone-100"><img src={photo.preview} alt={`Aperçu ${index + 1}`} className="size-full object-cover" />{index === 0 && <Badge variant="primary" className="absolute start-3 top-3">Photo principale</Badge>}</div><div className="p-3"><div className="flex items-center justify-between gap-2"><div className="min-w-0"><p className="truncate text-xs font-bold text-ink">Photo {index + 1}</p><p className="mt-0.5 text-[11px] text-muted">{photo.compressedBytes && photo.compressedBytes < photo.originalBytes ? `${bytesLabel(photo.originalBytes)} → ${bytesLabel(photo.compressedBytes)}` : bytesLabel(photo.originalBytes)}</p></div><div className="flex gap-1"><Button variant="ghost" size="icon" className="size-8" disabled={index === 0} onClick={() => movePhoto(index, -1)} aria-label="Déplacer avant"><ChevronLeft className="size-4" /></Button><Button variant="ghost" size="icon" className="size-8" disabled={index === photos.length - 1} onClick={() => movePhoto(index, 1)} aria-label="Déplacer après"><ChevronRight className="size-4" /></Button><Button variant="ghost" size="icon" className="size-8 text-error" onClick={() => removePhoto(photo)} aria-label="Supprimer la photo"><Trash2 className="size-4" /></Button></div></div>{['compressing', 'uploading'].includes(photo.status) && <div className="mt-3"><div className="mb-1 flex justify-between text-[11px] font-semibold text-muted"><span>{photo.status === 'compressing' ? 'Compression…' : 'Importation…'}</span><span>{photo.status === 'compressing' ? '' : `${photo.progress}%`}</span></div><div className="h-1.5 overflow-hidden rounded-full bg-stone-200"><div className="h-full rounded-full bg-primary transition-all" style={{ width: `${photo.status === 'compressing' ? 12 : photo.progress}%` }} /></div></div>}{photo.status === 'uploaded' && <p className="mt-2 flex items-center gap-1 text-[11px] font-bold text-success"><Check className="size-3.5" />Importée</p>}{photo.status === 'failed' && <div className="mt-2"><p className="text-[11px] font-semibold text-error">{photo.error}</p><Button variant="secondary" size="sm" className="mt-2" onClick={() => retryPhoto(photo)}><RefreshCw className="size-3.5" />Réessayer</Button></div>}</div></Card>)}</div>}
      </section>
    );

    if (step === 3) return <section><StepHeading eyebrow="Étape 4 sur 13" title="Décrivez le matériel" description="Mentionnez l’état réel, les accessoires inclus, les limites d’utilisation et les éventuels défauts." /><Textarea label="Description détaillée" required rows={8} value={listing.description} onChange={(event) => updateListing('description', event.target.value)} placeholder="Décrivez précisément ce que le locataire recevra…" error={errors.description} maxLength={3000} /><p className="mt-2 text-end text-xs text-muted">{formatNumber(listing.description.length)}/3000</p></section>;

    if (step === 4) return (
      <section>
        <StepHeading eyebrow="Étape 5 sur 13" title="Spécifications" description="Ajoutez seulement les caractéristiques utiles pour comparer et utiliser le matériel." />
        <div className="space-y-3">{specifications.map((spec, index) => <div key={spec.id} className="grid gap-2 rounded-card border border-border p-3 sm:grid-cols-[1fr_1fr_auto]"><Input aria-label={`Nom de la spécification ${index + 1}`} value={spec.key} onChange={(event) => updateListing('specifications', specifications.map((item) => item.id === spec.id ? { ...item, key: event.target.value } : item))} placeholder="Ex. Puissance" /><Input aria-label={`Valeur de la spécification ${index + 1}`} value={spec.value} onChange={(event) => updateListing('specifications', specifications.map((item) => item.id === spec.id ? { ...item, value: event.target.value } : item))} placeholder="Ex. 1500 W" /><Button variant="ghost" size="icon" className="text-error" disabled={specifications.length === 1} onClick={() => updateListing('specifications', specifications.filter((item) => item.id !== spec.id))} aria-label="Supprimer la spécification"><Trash2 className="size-4" /></Button></div>)}</div>
        <FieldError>{errors.specifications}</FieldError>
        {specifications.length < 10 && <Button variant="secondary" size="sm" className="mt-4" onClick={() => updateListing('specifications', [...specifications, { id: globalThis.crypto?.randomUUID?.() || `spec-${Date.now()}`, key: '', value: '' }])}><Plus className="size-4" />Ajouter une spécification</Button>}
      </section>
    );

    if (step === 5) return <section><StepHeading eyebrow="Étape 6 sur 13" title="Localisation du retrait" description="L’annonce affiche la ville et la zone approximative. Ne saisissez pas d’informations privées inutiles." /><div className="grid gap-5 sm:grid-cols-2"><Select label={t('form.city')} required value={listing.city} onChange={(event) => updateListing('city', event.target.value)} options={CITY_OPTIONS.map((option) => ({ ...option, label: cityLabel(option.value) }))} error={errors.city} /><Input label="Quartier ou zone" required value={listing.address} onChange={(event) => updateListing('address', event.target.value)} leadingIcon={MapPin} placeholder="Ex. Sidi Maarouf" error={errors.address} /></div><div className="mt-5 rounded-card bg-info-subtle p-4 text-xs leading-5 text-info">L’adresse exacte et l’horaire restent à confirmer dans la réservation. La publication n’utilise pas votre position GPS.</div></section>;

    if (step === 6) return <section><StepHeading eyebrow="Étape 7 sur 13" title="Prix de location" description="Indiquez uniquement votre prix par jour. Les devis, durées, frais et totaux de réservation seront calculés par FastAPI." /><div className="max-w-md"><Input label="Prix par jour" required type="number" min="0.01" step="0.01" value={listing.dailyPrice} onChange={(event) => updateListing('dailyPrice', event.target.value)} trailing="MAD" placeholder="250" error={errors.dailyPrice} /></div><div className="mt-5 rounded-card border border-border bg-stone-50 p-4"><p className="text-sm font-bold text-ink">Aucun calcul commercial dans ce formulaire</p><p className="mt-1 text-xs leading-5 text-muted">Aucun prix hebdomadaire, commission ou total locataire n’est estimé ici. Le backend reste la source de vérité.</p></div></section>;

    if (step === 7) return <section><StepHeading eyebrow="Étape 8 sur 13" title="Dépôt de garantie" description="Saisissez le montant que vous demandez. Il reste distinct du prix de location et n’est jamais présenté comme un revenu." /><div className="max-w-md"><Input label="Dépôt de garantie remboursable" required type="number" min="0" step="0.01" value={listing.depositAmount} onChange={(event) => updateListing('depositAmount', event.target.value)} trailing="MAD" placeholder="1000" error={errors.depositAmount} /></div><div className="mt-5 rounded-card border border-warning/20 bg-warning-subtle p-4"><p className="text-sm font-bold text-warning">Montant séparé de la location</p><p className="mt-1 text-xs leading-5 text-muted">Lokiini affichera clairement le dépôt à part. Ce formulaire ne prétend pas qu’il est bloqué, encaissé ou garanti.</p></div></section>;

    if (step === 8) return <section><StepHeading eyebrow="Étape 9 sur 13" title="Disponibilité" description="Indiquez si le matériel peut recevoir des demandes immédiatement." /><Card className="p-5"><Switch checked={listing.availableNow} onChange={(value) => updateListing('availableNow', value)} label="Accepter des demandes dès la publication" description="Si cette option est désactivée, l’annonce reste dans Mon matériel mais n’apparaît pas dans le catalogue disponible." /></Card><p className="mt-4 text-xs leading-5 text-muted">Le backend prend actuellement en charge une disponibilité active ou inactive. Aucune activation future automatique n’est promise.</p></section>;

    if (step === 9) return <section><StepHeading eyebrow="Étape 10 sur 13" title="Retrait et livraison" description="Le retrait sur place est le mode actuellement pris en charge lors de la réservation. Une livraison peut seulement être annoncée comme modalité à convenir." /><Textarea label="Instructions de retrait" required rows={4} value={listing.pickupInstructions} onChange={(event) => updateListing('pickupInstructions', event.target.value)} placeholder="Ex. Retrait sur rendez-vous, du lundi au samedi…" error={errors.pickupInstructions} /><Card className="mt-5 p-5"><Switch checked={listing.deliveryAvailable} onChange={(value) => updateListing('deliveryAvailable', value)} label="Livraison éventuellement possible" description="Aucun frais de livraison n’est calculé ou ajouté par ce formulaire." />{listing.deliveryAvailable && <Textarea className="mt-4" label="Zone et conditions" value={listing.deliveryDetails} onChange={(event) => updateListing('deliveryDetails', event.target.value)} placeholder="Ex. Casablanca, à convenir avant confirmation…" error={errors.deliveryDetails} />}</Card></section>;

    if (step === 10) return <section><StepHeading eyebrow="Étape 11 sur 13" title="Règles d’utilisation" description="Expliquez les limites importantes avant qu’un locataire envoie sa demande." /><Textarea label="Règles supplémentaires" rows={6} value={listing.rules} disabled={listing.noAdditionalRules} onChange={(event) => updateListing('rules', event.target.value)} placeholder="Ex. Usage intérieur uniquement, nettoyage avant retour…" error={errors.rules} /><Checkbox className="mt-3" checked={listing.noAdditionalRules} onChange={(event) => updateListing('noAdditionalRules', event.target.checked)} label="Je n’ai pas de règle supplémentaire à indiquer" description="Les conditions finales de la réservation restent applicables." /><Textarea className="mt-5" label="Conditions d’annulation indiquées par le propriétaire (optionnel)" rows={3} value={listing.cancellationTerms} onChange={(event) => updateListing('cancellationTerms', event.target.value)} placeholder="Décrivez uniquement vos conditions réelles." /></section>;

    if (step === 11) return (
      <section>
        <StepHeading eyebrow="Étape 12 sur 13" title="Aperçu de l’annonce" description="Vérifiez ce que les locataires verront. Revenez à une étape pour corriger une information." />
        <Card className="overflow-hidden"><div className="grid lg:grid-cols-[1.1fr_0.9fr]"><div className="bg-stone-100">{photos[0]?.preview ? <img src={photos[0].preview} alt="Aperçu principal" className="aspect-[4/3] size-full object-cover" /> : <div className="flex aspect-[4/3] items-center justify-center text-muted"><ImagePlus className="size-10" /></div>}</div><div className="p-5 sm:p-6"><Badge variant="primary">{categoryLabel}</Badge><h4 className="mt-3 font-display text-2xl font-bold text-ink">{listing.title || 'Titre de l’annonce'}</h4><p className="mt-2 flex items-center gap-1.5 text-sm text-muted"><MapPin className="size-4" />{listing.address ? `${listing.address}, ${listing.city}` : listing.city}</p><p className="mt-4 line-clamp-5 text-sm leading-6 text-muted">{listing.description || 'Description non renseignée.'}</p><div className="mt-6 grid grid-cols-2 gap-3"><div className="rounded-card bg-stone-50 p-3"><p className="text-[11px] font-bold uppercase text-muted">Location</p><PriceDisplay className="mt-1" amount={listing.dailyPrice} period="jour" /></div><div className="rounded-card bg-warning-subtle p-3"><p className="text-[11px] font-bold uppercase text-warning">Dépôt remboursable</p><PriceDisplay className="mt-1" amount={listing.depositAmount} /></div></div><div className="mt-5 flex flex-wrap gap-2"><Badge variant={listing.availableNow ? 'success' : 'warning'}>{listing.availableNow ? 'Disponible immédiatement' : 'Annonce masquée du catalogue'}</Badge><Badge variant="neutral">{listing.deliveryAvailable ? 'Livraison à convenir' : 'Retrait sur place'}</Badge></div></div></div></Card>
        {photos.length > 1 && <div className="mt-3 flex gap-2 overflow-x-auto">{photos.slice(1).map((photo, index) => <img key={photo.id} src={photo.preview} alt={`Aperçu secondaire ${index + 2}`} className="h-20 w-28 shrink-0 rounded-control object-cover" />)}</div>}
      </section>
    );

    return (
      <section>
        <StepHeading eyebrow="Étape 13 sur 13" title="Prêt à publier" description="La publication n’a lieu qu’après votre confirmation. Le backend ne prend pas encore en charge l’enregistrement de brouillons partiels." />
        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="p-5"><p className="text-xs font-bold uppercase tracking-wide text-muted">Annonce</p><p className="mt-2 font-display text-lg font-bold text-ink">{listing.title}</p><p className="mt-1 text-xs text-muted">{categoryLabel} · {listing.city} · {photos.length} photo{photos.length > 1 ? 's' : ''}</p></Card>
          <Card className="p-5"><p className="text-xs font-bold uppercase tracking-wide text-muted">Montants saisis</p><div className="mt-2 flex items-center justify-between gap-3 text-sm"><span className="text-muted">Location / jour</span><span className="font-bold text-ink">{formatMAD(listing.dailyPrice)}</span></div><div className="mt-2 flex items-center justify-between gap-3 text-sm"><span className="text-muted">Dépôt remboursable</span><span className="font-bold text-warning">{formatMAD(listing.depositAmount)}</span></div></Card>
        </div>
        <Card className="mt-5 p-5"><Checkbox checked={listing.confirmed} onChange={(event) => updateListing('confirmed', event.target.checked)} label="Je confirme que les informations et les photos correspondent réellement à mon matériel" description="Les montants saisis seront transmis tels quels. Les calculs de réservation resteront effectués par le backend." /><FieldError>{errors.confirmed}</FieldError></Card>
        <div className="mt-5 rounded-card border border-info/20 bg-info-subtle p-4 text-xs leading-5 text-info"><strong>Brouillon :</strong> aucun brouillon serveur n’est disponible actuellement. Fermer ce formulaire supprime les photos importées qui ne sont liées à aucune annonce.</div>
      </section>
    );
  };

  const footer = published ? (
    <Button onClick={requestClose}>{t('publish.close')}</Button>
  ) : (
    <>
      <Button variant="ghost" onClick={requestClose} disabled={publishing}>{t('publish.cancel')}</Button>
      <div className="grid flex-1 grid-cols-2 items-center gap-2 sm:flex sm:justify-end">
        {step > 0 && <Button variant="secondary" onClick={() => setStep((current) => current - 1)} disabled={publishing}><ArrowLeft className="rtl-flip size-4" />{t('publish.previous')}</Button>}
        {step < PUBLISHING_STEPS.length - 1 ? <Button onClick={goNext}>{t('common.continue')}<ArrowRight className="rtl-flip size-4" /></Button> : <Button variant="action" onClick={publish} loading={publishing} loadingLabel={t('publish.publishing')}><Upload className="size-4" />{t('publish.action')}</Button>}
      </div>
    </>
  );

  return (
    <Modal
      open={isOpen}
      onClose={requestClose}
      title={t('publish.title')}
      description={published ? t('publish.confirmed') : `${t(`publish.steps.${PUBLISHING_STEP_KEYS[step]}`, {}, PUBLISHING_STEPS[step])} · ${t('publish.step', { current: formatNumber(step + 1), total: formatNumber(PUBLISHING_STEPS.length) })}`}
      size="xl"
      className="max-w-6xl"
      footer={footer}
    >
      {!published && <div className="mb-5 lg:hidden"><div className="mb-2 flex items-center justify-between text-xs font-bold text-muted"><span>{t(`publish.steps.${PUBLISHING_STEP_KEYS[step]}`, {}, PUBLISHING_STEPS[step])}</span><span>{formatNumber(step + 1)}/{formatNumber(PUBLISHING_STEPS.length)}</span></div><div className="h-2 overflow-hidden rounded-full bg-stone-100"><div className="h-full rounded-full bg-primary transition-all" style={{ width: `${((step + 1) / PUBLISHING_STEPS.length) * 100}%` }} /></div></div>}
      {globalError && <div role="alert" className="mb-5 flex items-start gap-3 rounded-card border border-error/20 bg-error-subtle p-4 text-sm font-semibold text-error"><AlertCircle aria-hidden="true" className="mt-0.5 size-5 shrink-0" /><span>{globalError}</span></div>}
      <div className={published ? '' : 'grid gap-7 lg:grid-cols-[190px_minmax(0,1fr)]'}>
        {!published && <aside className="hidden border-e border-border pe-4 lg:block"><ProgressSteps current={step} maxVisited={maxVisited} onSelect={setStep} /></aside>}
        <div className="min-w-0">{renderStep()}</div>
      </div>
    </Modal>
  );
}
