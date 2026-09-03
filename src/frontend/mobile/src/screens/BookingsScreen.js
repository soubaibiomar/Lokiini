import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import { getUserBookings } from '../services/bookings';

const STATUS_LABELS = {
  en_attente_approbation: { label: 'En attente', color: '#D97706', bg: '#FEF3C7' },
  approuvee: { label: 'Approuvée', color: '#2563EB', bg: '#EFF6FF' },
  paiement_en_attente: { label: 'Paiement requis', color: '#D97706', bg: '#FEF3C7' },
  prete_remise: { label: 'Prête pour remise', color: '#059669', bg: '#ECFDF5' },
  en_cours: { label: 'En cours de location', color: '#0F6E56', bg: '#E6FCF5' },
  terminee: { label: 'Terminée', color: '#475569', bg: '#F1F5F9' },
  refusee: { label: 'Refusée', color: '#DC2626', bg: '#FEF2F2' },
  annulee: { label: 'Annulée', color: '#DC2626', bg: '#FEF2F2' },
  en_litige: { label: 'En litige', color: '#B91C1C', bg: '#FEE2E2' },
};

export default function BookingsScreen({ onOpenInspection }) {
  const [role, setRole] = useState('locataire'); // 'locataire' | 'loueur'
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchBookings = useCallback(async () => {
    setError(null);
    try {
      const data = await getUserBookings(role);
      const items = Array.isArray(data) ? data : data?.items || data?.reservations || [];
      setBookings(items);
    } catch (err) {
      setError(err.message || 'Impossible de charger vos réservations.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [role]);

  useEffect(() => {
    setLoading(true);
    fetchBookings();
  }, [fetchBookings]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchBookings();
  };

  const renderHeader = () => (
    <View style={styles.header}>
      <Text style={styles.headerTitle}>Mes Baux & Cautions Séquestrées</Text>
      <Text style={styles.headerSubtitle}>Suivi en temps réel conforme au Dahir des Obligations et Contrats</Text>

      {/* Role Switcher Tabs */}
      <View style={styles.roleTabs}>
        <TouchableOpacity
          style={[styles.roleTab, role === 'locataire' && styles.roleTabActive]}
          onPress={() => setRole('locataire')}
        >
          <Text style={[styles.roleTabText, role === 'locataire' && styles.roleTabTextActive]}>
            En tant que Locataire
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.roleTab, role === 'loueur' && styles.roleTabActive]}
          onPress={() => setRole('loueur')}
        >
          <Text style={[styles.roleTabText, role === 'loueur' && styles.roleTabTextActive]}>
            En tant que Propriétaire
          </Text>
        </TouchableOpacity>
      </View>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}
    </View>
  );

  const renderItem = ({ item: b }) => {
    const statusMeta = STATUS_LABELS[b.statut] || {
      label: b.statut || 'En cours',
      color: '#475569',
      bg: '#F1F5F9',
    };

    const isInspectionReady = ['approuvee', 'prete_remise', 'en_cours'].includes(b.statut);

    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.refText}>Réf: {String(b.id).slice(0, 8).toUpperCase()}</Text>
          <View style={[styles.statusBadge, { backgroundColor: statusMeta.bg }]}>
            <Text style={[styles.statusBadgeText, { color: statusMeta.color }]}>{statusMeta.label}</Text>
          </View>
        </View>

        <Text style={styles.titleText}>{b.article_titre || b.article?.titre || 'Équipement Lokiini'}</Text>
        <Text style={styles.periodText}>Du {b.date_debut} au {b.date_fin} ({b.total_days || 1} jours)</Text>

        <View style={styles.amountRow}>
          <Text style={styles.amountLabel}>
            Total location : <Text style={styles.amountVal}>{b.prix_total} MAD</Text>
          </Text>
          <Text style={styles.cautionLabel}>
            Caution séquestrée : <Text style={styles.cautionVal}>{b.montant_caution} MAD</Text>
          </Text>
        </View>

        {isInspectionReady && onOpenInspection ? (
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => onOpenInspection(b)}
          >
            <Text style={styles.actionButtonText}>Ouvrir l'État des Lieux</Text>
          </TouchableOpacity>
        ) : null}
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0F6E56" />
          <Text style={styles.loadingText}>Chargement des réservations...</Text>
        </View>
      ) : (
        <FlatList
          data={bookings}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderItem}
          ListHeaderComponent={renderHeader}
          contentContainerStyle={styles.content}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#0F6E56']} />}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>Aucune réservation</Text>
              <Text style={styles.emptySubtitle}>
                {role === 'locataire'
                  ? 'Vous n’avez aucune réservation active comme locataire.'
                  : 'Aucune demande de location reçue pour vos équipements.'}
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  content: { padding: 16 },
  header: { marginBottom: 12 },
  headerTitle: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  headerSubtitle: { fontSize: 11, color: '#64748B', marginBottom: 14, marginTop: 2 },
  roleTabs: { flexDirection: 'row', backgroundColor: '#E2E8F0', borderRadius: 10, padding: 3, marginBottom: 12 },
  roleTab: { flex: 1, paddingVertical: 8, alignItems: 'center', borderRadius: 8 },
  roleTabActive: { backgroundColor: '#FFFFFF', shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 2, elevation: 1 },
  roleTabText: { fontSize: 11, fontWeight: '600', color: '#64748B' },
  roleTabTextActive: { color: '#0F6E56', fontWeight: 'bold' },
  errorText: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 8, borderRadius: 8, marginBottom: 10, fontSize: 12 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, color: '#64748B', fontWeight: '600' },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  refText: { fontSize: 11, fontWeight: 'bold', color: '#0F6E56', fontFamily: 'monospace' },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6 },
  statusBadgeText: { fontSize: 10, fontWeight: 'bold' },
  titleText: { fontSize: 15, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  periodText: { fontSize: 11, color: '#64748B', marginBottom: 8 },
  amountRow: {
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 8,
    marginBottom: 10,
  },
  amountLabel: { fontSize: 11, color: '#64748B' },
  amountVal: { fontWeight: 'bold', color: '#0F6E56' },
  cautionLabel: { fontSize: 11, color: '#64748B', marginTop: 2 },
  cautionVal: { fontWeight: 'bold', color: '#D85A30' },
  actionButton: {
    backgroundColor: '#0F6E56',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  actionButtonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 12 },
  emptyContainer: { padding: 40, alignItems: 'center' },
  emptyTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  emptySubtitle: { fontSize: 12, color: '#64748B', textAlign: 'center' },
});
