import { apiClient } from './apiClient';

export async function initiateKYC() {
  return apiClient.post('/auth/kyc/initier', {});
}

export async function getKYCStatus(userId) {
  if (!userId) throw new Error('Identifiant utilisateur requis.');
  return apiClient.get(`/auth/kyc/statut/${encodeURIComponent(String(userId))}`);
}
