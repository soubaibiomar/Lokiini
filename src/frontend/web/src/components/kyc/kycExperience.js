export const KYC_STATUS = Object.freeze({
  not_started: {
    key: 'not_started', label: 'Vérification à commencer', tone: 'warning',
    description: 'Vous n’avez pas encore commencé la vérification de votre identité.',
    guidance: 'Préparez une pièce d’identité valide avant d’ouvrir la session sécurisée.',
    actionLabel: 'Commencer la vérification',
  },
  pending: {
    key: 'pending', label: 'Vérification en attente', tone: 'warning',
    description: 'Une session a été créée, mais la vérification n’est pas encore terminée.',
    guidance: 'Le statut sera mis à jour lorsque le fournisseur aura reçu et traité les étapes demandées.',
    actionLabel: null,
  },
  in_review: {
    key: 'in_review', label: 'Dossier en cours d’examen', tone: 'info',
    description: 'Le fournisseur de vérification examine actuellement votre dossier.',
    guidance: 'Aucune nouvelle session n’est nécessaire pendant cet examen.',
    actionLabel: null,
  },
  verified: {
    key: 'verified', label: 'Identité vérifiée', tone: 'success',
    description: 'Le fournisseur a confirmé la vérification de votre identité.',
    guidance: 'Votre compte utilise maintenant ce statut pour les parcours qui exigent une identité vérifiée.',
    actionLabel: null,
  },
  rejected: {
    key: 'rejected', label: 'Vérification non aboutie', tone: 'error',
    description: 'Le fournisseur n’a pas pu valider la vérification transmise.',
    guidance: 'Vérifiez que votre pièce est valide, lisible et correspond à vos informations avant de réessayer.',
    actionLabel: 'Réessayer',
  },
  requires_action: {
    key: 'requires_action', label: 'Une action est nécessaire', tone: 'warning',
    description: 'Des informations ou une nouvelle étape sont nécessaires pour terminer la vérification.',
    guidance: 'Ouvrez une nouvelle session sécurisée et suivez les indications du fournisseur.',
    actionLabel: 'Continuer la vérification',
  },
});

export const UNKNOWN_KYC_STATUS = Object.freeze({
  key: 'unknown', label: 'Statut indisponible', tone: 'neutral',
  description: 'Lokiini ne reconnaît pas le statut renvoyé par le service de vérification.',
  guidance: 'Actualisez le statut avant de poursuivre.', actionLabel: null,
});

export const KYC_REASONS = Object.freeze([
  'Réduire les tentatives de fraude',
  'Protéger les locataires',
  'Protéger les propriétaires',
  'Associer l’identité aux contrats',
  'Fournir un repère lors du traitement des litiges',
]);

export function normalizeKycStatus(value) {
  if (value == null || value === '') return 'not_started';
  const normalized = String(value).trim().toLowerCase().replace(/[\s-]+/g, '_');
  return Object.hasOwn(KYC_STATUS, normalized) ? normalized : 'unknown';
}

export function getKycStatus(value) {
  const key = normalizeKycStatus(value);
  return key === 'unknown' ? UNKNOWN_KYC_STATUS : KYC_STATUS[key];
}

export function canInitiateKyc(value) {
  return ['not_started', 'rejected', 'requires_action'].includes(normalizeKycStatus(value));
}

export function isKycProcessing(value) {
  return ['pending', 'in_review'].includes(normalizeKycStatus(value));
}
