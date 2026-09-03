export const PUBLISHING_STEPS = [
  'Catégorie',
  'Informations',
  'Photos',
  'Description',
  'Spécifications',
  'Localisation',
  'Prix',
  'Dépôt',
  'Disponibilité',
  'Remise',
  'Règles',
  'Aperçu',
  'Publication',
];

export const CATEGORY_OPTIONS = [
  { value: 'tools', label: 'Outils et bricolage' },
  { value: 'btp', label: 'BTP et chantier' },
  { value: 'audiovisual', label: 'Photo et audiovisuel' },
  { value: 'event', label: 'Événementiel' },
  { value: 'outdoor', label: 'Plein air et camping' },
  { value: 'cleaning', label: 'Nettoyage et entretien' },
  { value: 'energy', label: 'Énergie' },
  { value: 'transport', label: 'Transport' },
  { value: 'vehicles', label: 'Véhicules' },
  { value: 'hightech', label: 'High-tech' },
  { value: 'medical', label: 'Matériel médical' },
];

export const CITY_OPTIONS = [
  'Casablanca', 'Rabat', 'Marrakech', 'Tanger', 'Fès', 'Agadir', 'Oujda',
].map((city) => ({ value: city, label: city }));

export function createEmptyListing() {
  return {
    category: '',
    title: '',
    condition: '',
    description: '',
    specifications: [{ id: 'spec-1', key: '', value: '' }],
    city: 'Casablanca',
    address: '',
    dailyPrice: '',
    depositAmount: '',
    availableNow: true,
    pickupInstructions: '',
    deliveryAvailable: false,
    deliveryDetails: '',
    rules: '',
    cancellationTerms: '',
    noAdditionalRules: false,
    confirmed: false,
  };
}

function specificationErrors(specifications) {
  const incomplete = specifications.some((spec) => (
    (spec.key.trim() && !spec.value.trim()) || (!spec.key.trim() && spec.value.trim())
  ));
  return incomplete ? { specifications: 'Chaque spécification doit avoir un nom et une valeur.' } : {};
}

export function validatePublishingStep(step, listing, photos) {
  const errors = {};
  if (step === 0 && !listing.category) errors.category = 'Choisissez une catégorie.';
  if (step === 1) {
    if (listing.title.trim().length < 3) errors.title = 'Le titre doit contenir au moins 3 caractères.';
    if (!listing.condition) errors.condition = 'Indiquez l’état actuel du matériel.';
  }
  if (step === 2) {
    if (!photos.length) errors.photos = 'Ajoutez au moins une vraie photo du matériel.';
    else if (photos.some((photo) => ['compressing', 'uploading', 'deleting'].includes(photo.status))) errors.photos = 'Attendez la fin de toutes les importations.';
    else if (photos.some((photo) => photo.status !== 'uploaded')) errors.photos = 'Réessayez ou supprimez les photos en erreur.';
  }
  if (step === 3 && listing.description.trim().length < 30) errors.description = 'Décrivez l’état, les accessoires et l’usage en au moins 30 caractères.';
  if (step === 4) Object.assign(errors, specificationErrors(listing.specifications));
  if (step === 5) {
    if (!listing.city) errors.city = 'Choisissez une ville.';
    if (listing.address.trim().length < 3) errors.address = 'Indiquez au minimum le quartier ou la zone de retrait.';
  }
  if (step === 6 && !(Number(listing.dailyPrice) > 0)) errors.dailyPrice = 'Le prix par jour doit être supérieur à 0 MAD.';
  if (step === 7 && (listing.depositAmount === '' || Number(listing.depositAmount) < 0)) errors.depositAmount = 'Le dépôt doit être égal ou supérieur à 0 MAD.';
  if (step === 9) {
    if (listing.pickupInstructions.trim().length < 3) errors.pickupInstructions = 'Précisez comment organiser le retrait.';
    if (listing.deliveryAvailable && listing.deliveryDetails.trim().length < 5) errors.deliveryDetails = 'Expliquez la zone ou les conditions de livraison, sans inventer de tarif.';
  }
  if (step === 10 && !listing.noAdditionalRules && listing.rules.trim().length < 10) errors.rules = 'Ajoutez des règles claires ou confirmez qu’il n’y en a pas de supplémentaires.';
  if (step === 12 && !listing.confirmed) errors.confirmed = 'Confirmez que les informations sont exactes avant publication.';
  return errors;
}

export function validateCompleteListing(listing, photos) {
  return Array.from({ length: 13 }, (_, step) => validatePublishingStep(step, listing, photos))
    .reduce((all, current) => ({ ...all, ...current }), {});
}

export function buildEquipmentPayload(listing, photos) {
  const specs = {};
  listing.specifications.forEach((spec) => {
    const key = spec.key.trim();
    const value = spec.value.trim();
    if (key && value) specs[key] = value;
  });
  specs.etat = listing.condition;
  specs.option_livraison = listing.deliveryAvailable
    ? 'Retrait sur place ou livraison à convenir avec le propriétaire'
    : 'Retrait sur place';
  specs.retrait = listing.pickupInstructions.trim();
  specs.regles = listing.noAdditionalRules
    ? 'Aucune règle supplémentaire indiquée par le propriétaire.'
    : listing.rules.trim();
  if (listing.cancellationTerms.trim()) specs.politique_annulation = listing.cancellationTerms.trim();
  if (listing.deliveryAvailable) specs.details_livraison = listing.deliveryDetails.trim();

  return {
    title: listing.title.trim(),
    description: listing.description.trim(),
    category: listing.category,
    city: listing.city,
    address: listing.address.trim(),
    daily_price_mad: Number(listing.dailyPrice),
    deposit_amount_mad: Number(listing.depositAmount),
    images_urls: photos.map((photo) => photo.url),
    specs_json: specs,
    is_available: listing.availableNow,
    calendrier_disponibilite: {
      disponible_immediatement: listing.availableNow,
      dates_bloquees: [],
    },
  };
}

function normalizedPhotoName(name) {
  const base = String(name || 'photo').replace(/\.[^.]+$/, '').replace(/[^a-z0-9_-]+/gi, '-').slice(0, 80) || 'photo';
  return `${base}.webp`;
}

export async function compressEquipmentPhoto(file, { maxDimension = 1920, quality = 0.82 } = {}) {
  if (!file.type.startsWith('image/')) throw new Error('Sélectionnez un fichier image.');
  if (file.size > 12 * 1024 * 1024) throw new Error('La photo dépasse 12 Mo avant compression.');
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) throw new Error('Formats acceptés : JPEG, PNG ou WebP.');
  if (typeof createImageBitmap !== 'function' || typeof document === 'undefined') return file;

  const bitmap = await createImageBitmap(file);
  const scale = Math.min(1, maxDimension / Math.max(bitmap.width, bitmap.height));
  const width = Math.max(1, Math.round(bitmap.width * scale));
  const height = Math.max(1, Math.round(bitmap.height * scale));
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext('2d');
  if (!context) {
    bitmap.close?.();
    throw new Error('Compression de la photo indisponible sur cet appareil.');
  }
  context.drawImage(bitmap, 0, 0, width, height);
  bitmap.close?.();
  const blob = await new Promise((resolve, reject) => {
    canvas.toBlob((result) => result ? resolve(result) : reject(new Error('Compression de la photo impossible.')), 'image/webp', quality);
  });
  return new File([blob], normalizedPhotoName(file.name), { type: 'image/webp', lastModified: Date.now() });
}
