import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator, Linking, StyleSheet, Text, TouchableOpacity, View,
} from 'react-native';

import { getKYCStatus, initiateKYC } from '../services/kyc';

const KYC_STATES = {
  not_started: { label: 'Vérification à commencer', detail: 'Préparez une pièce d’identité valide.', action: 'Commencer la vérification' },
  pending: { label: 'Vérification en attente', detail: 'Une session existe et la vérification n’est pas encore terminée.' },
  in_review: { label: 'Dossier en cours d’examen', detail: 'Le fournisseur examine actuellement votre dossier.' },
  verified: { label: 'Identité vérifiée', detail: 'Le fournisseur a confirmé la vérification de votre identité.' },
  rejected: { label: 'Vérification non aboutie', detail: 'Vérifiez votre pièce et vos informations avant de réessayer.', action: 'Réessayer' },
  requires_action: { label: 'Une action est nécessaire', detail: 'Une nouvelle étape est nécessaire pour terminer la vérification.', action: 'Continuer la vérification' },
};

const REASONS = [
  'Réduire les tentatives de fraude',
  'Protéger les locataires',
  'Protéger les propriétaires',
  'Associer l’identité aux contrats',
  'Aider au traitement des litiges',
];

function normalizeStatus(value) {
  if (value == null || value === '') return 'not_started';
  const normalized = String(value).trim().toLowerCase().replace(/[\s-]+/g, '_');
  return KYC_STATES[normalized] ? normalized : 'unknown';
}

export default function KYCCameraScreen({
  onVerificationComplete, currentStatus = 'not_started', currentUserId,
}) {
  const [status, setStatus] = useState(normalizeStatus(currentStatus));
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const statusInfo = KYC_STATES[status] || {
    label: 'Statut indisponible', detail: 'Actualisez votre statut avant de poursuivre.', action: null,
  };

  const refreshStatus = async () => {
    if (!currentUserId) return;
    setIsRefreshing(true);
    setError(null);
    try {
      const response = await getKYCStatus(currentUserId);
      setStatus(normalizeStatus(response?.status));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    setStatus(normalizeStatus(currentStatus));
  }, [currentStatus]);

  useEffect(() => {
    if (currentUserId) refreshStatus();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentUserId]);

  const handleStart = async () => {
    setIsProcessing(true);
    setError(null);
    try {
      const session = await initiateKYC();
      const supported = await Linking.canOpenURL(session.verification_url);
      if (!supported) throw new Error('Le lien sécurisé du fournisseur ne peut pas être ouvert.');
      setStatus(normalizeStatus(session.status));
      await Linking.openURL(session.verification_url);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const canStart = ['not_started', 'rejected', 'requires_action'].includes(status);
  const canRefresh = currentUserId && ['pending', 'in_review', 'unknown'].includes(status);

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Vérification d’identité</Text>
        <View style={styles.statusCard} accessibilityRole="summary">
          <Text style={styles.eyebrow}>VOTRE STATUT ACTUEL</Text>
          <Text style={styles.status}>{statusInfo.label}</Text>
          <Text style={styles.statusDetail}>{statusInfo.detail}</Text>
        </View>

        <Text style={styles.sectionTitle}>Pourquoi cette vérification ?</Text>
        {REASONS.map((reason) => <Text key={reason} style={styles.reason}>— {reason}</Text>)}

        <View style={styles.dataCard}>
          <Text style={styles.dataTitle}>Vos données</Text>
          <Text style={styles.dataText}>
            La pièce d’identité et le contrôle de présence sont recueillis dans le parcours hébergé du fournisseur.
            Lokiini conserve le statut et les références nécessaires au suivi de la vérification.
          </Text>
        </View>

        {error ? <Text accessibilityRole="alert" style={styles.error}>{error}</Text> : null}
        {canStart ? (
          <TouchableOpacity style={styles.primaryButton} onPress={handleStart} disabled={isProcessing}>
            {isProcessing ? <ActivityIndicator color="#FFFFFF" /> : <Text style={styles.buttonText}>{statusInfo.action}</Text>}
          </TouchableOpacity>
        ) : null}
        {canRefresh ? (
          <TouchableOpacity style={styles.refreshButton} onPress={refreshStatus} disabled={isRefreshing}>
            {isRefreshing ? <ActivityIndicator color="#0F6E56" /> : <Text style={styles.refreshText}>Actualiser le statut</Text>}
          </TouchableOpacity>
        ) : null}
        <TouchableOpacity style={styles.secondaryButton} onPress={onVerificationComplete}>
          <Text style={styles.secondaryText}>Retour</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16, justifyContent: 'center', backgroundColor: '#F8FAFC' },
  card: { backgroundColor: '#FFFFFF', borderRadius: 18, padding: 20, borderWidth: 1, borderColor: '#E2E8F0' },
  title: { fontSize: 21, fontWeight: '900', color: '#1E293B', marginBottom: 16 },
  statusCard: { backgroundColor: '#F0FDFA', borderRadius: 12, padding: 14, borderWidth: 1, borderColor: '#CCFBF1' },
  eyebrow: { color: '#64748B', fontSize: 10, fontWeight: '800', letterSpacing: 0.8 },
  status: { color: '#0F6E56', fontSize: 16, fontWeight: '900', marginTop: 5 },
  statusDetail: { color: '#475569', fontSize: 12, lineHeight: 18, marginTop: 5 },
  sectionTitle: { color: '#1E293B', fontSize: 14, fontWeight: '900', marginTop: 20, marginBottom: 8 },
  reason: { color: '#475569', fontSize: 12, lineHeight: 20 },
  dataCard: { backgroundColor: '#F8FAFC', borderRadius: 12, padding: 14, marginTop: 16 },
  dataTitle: { color: '#1E293B', fontSize: 13, fontWeight: '800' },
  dataText: { color: '#64748B', fontSize: 11, lineHeight: 17, marginTop: 4 },
  error: { color: '#B91C1C', backgroundColor: '#FEF2F2', fontSize: 12, lineHeight: 18, padding: 10, borderRadius: 8, marginTop: 14 },
  primaryButton: { backgroundColor: '#0F6E56', minHeight: 48, borderRadius: 10, alignItems: 'center', justifyContent: 'center', marginTop: 16 },
  buttonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 13 },
  refreshButton: { minHeight: 46, borderRadius: 10, borderWidth: 1, borderColor: '#99F6E4', alignItems: 'center', justifyContent: 'center', marginTop: 12 },
  refreshText: { color: '#0F6E56', fontWeight: '800', fontSize: 13 },
  secondaryButton: { minHeight: 44, alignItems: 'center', justifyContent: 'center', marginTop: 8 },
  secondaryText: { color: '#475569', fontWeight: '700' },
});
