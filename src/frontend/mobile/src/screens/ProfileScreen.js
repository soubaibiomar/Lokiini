import React from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { logout } from '../services/auth';

const KYC_BADGES = {
  verified: { label: '✓ Identité Vérifiée', bg: '#ECFDF5', color: '#059669' },
  pending: { label: 'En attente d’examen', bg: '#FEF3C7', color: '#D97706' },
  in_review: { label: 'Dossier en examen', bg: '#EFF6FF', color: '#2563EB' },
  requires_action: { label: 'Action requise', bg: '#FEF2F2', color: '#DC2626' },
  not_started: { label: 'Non vérifié', bg: '#F1F5F9', color: '#64748B' },
};

export default function ProfileScreen({ user, onStartKYC, onLogout }) {
  const kycStatus = user?.statut_verification || 'not_started';
  const badge = KYC_BADGES[kycStatus] || KYC_BADGES.not_started;

  const handleLogout = async () => {
    await logout();
    if (onLogout) onLogout();
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {(user?.nom_complet || user?.email || 'U')[0].toUpperCase()}
          </Text>
        </View>
        <Text style={styles.name}>{user?.nom_complet || 'Utilisateur Lokiini'}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        {user?.telephone ? <Text style={styles.phone}>📞 {user.telephone}</Text> : null}

        <View style={[styles.badge, { backgroundColor: badge.bg }]}>
          <Text style={[styles.badgeText, { color: badge.color }]}>{badge.label}</Text>
        </View>
      </View>

      {/* KYC Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Vérification d’identité</Text>
        <Text style={styles.cardText}>
          Vérification d'identité sécurisée par le fournisseur agréé. Elle renforce la confiance entre loueurs et locataires.
        </Text>
        <TouchableOpacity style={styles.kycBtn} onPress={onStartKYC}>
          <Text style={styles.kycBtnText}>
            {kycStatus === 'verified' ? 'Consulter le statut d’identité' : 'Compléter la vérification'}
          </Text>
        </TouchableOpacity>
      </View>

      {/* Account Info */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Détails du compte</Text>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Rôle :</Text>
          <Text style={styles.infoVal}>{user?.user_role === 'pro_owner' ? 'Propriétaire Pro' : 'Particulier / Professionnel'}</Text>
        </View>
        <View style={styles.infoRow}>
          <Text style={styles.infoLabel}>Identifiant :</Text>
          <Text style={styles.infoValMono}>{String(user?.id || '').slice(0, 12)}...</Text>
        </View>
      </View>

      {/* Security Notice */}
      <View style={styles.noticeBox}>
        <Text style={styles.noticeTitle}>Sécurité des transactions</Text>
        <Text style={styles.noticeText}>
          • Cautions sécurisées sans débit immédiat
          {'\n'}• Contrats de location clairs et documentés
          {'\n'}• Protection de la vie privée et des données personnelles
        </Text>
      </View>

      {/* Logout */}
      <TouchableOpacity style={styles.logoutBtn} onPress={handleLogout}>
        <Text style={styles.logoutBtnText}>Se déconnecter</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  content: { padding: 16 },
  header: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  avatar: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#0F6E56',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 10,
  },
  avatarText: { color: '#FFFFFF', fontSize: 24, fontWeight: 'bold' },
  name: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  email: { fontSize: 12, color: '#64748B', marginTop: 2 },
  phone: { fontSize: 12, color: '#0F6E56', marginTop: 4, fontWeight: '600' },
  badge: { marginTop: 10, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  badgeText: { fontSize: 11, fontWeight: 'bold' },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardTitle: { fontSize: 14, fontWeight: 'bold', color: '#1E293B', marginBottom: 6 },
  cardText: { fontSize: 11, color: '#64748B', lineHeight: 16, marginBottom: 12 },
  kycBtn: {
    backgroundColor: '#0F6E56',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  kycBtnText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 12 },
  infoRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 6, borderBottomWidth: 1, borderBottomColor: '#F1F5F9' },
  infoLabel: { fontSize: 12, color: '#64748B' },
  infoVal: { fontSize: 12, fontWeight: 'bold', color: '#1E293B' },
  infoValMono: { fontSize: 11, fontFamily: 'monospace', color: '#475569' },
  noticeBox: { backgroundColor: '#F0FDFA', borderRadius: 12, padding: 14, marginBottom: 16, borderWidth: 1, borderColor: '#CCFBF1' },
  noticeTitle: { fontSize: 12, fontWeight: 'bold', color: '#0F6E56', marginBottom: 4 },
  noticeText: { fontSize: 11, color: '#047857', lineHeight: 16 },
  logoutBtn: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: '#FEE2E2',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 20,
  },
  logoutBtnText: { color: '#DC2626', fontWeight: 'bold', fontSize: 13 },
});
