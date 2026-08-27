import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';

const MOCK_BOOKINGS = [
  {
    id: 'LK-849201',
    title: 'Mini-Pelle Compacte Bobcat E19',
    period: '24 Août ➔ 31 Août 2026',
    total_mad: 7168,
    deposit_mad: 8000,
    status: 'En cours (Check-in scellé)',
    cmi_status: 'Caution Bloquée CMI'
  },
  {
    id: 'LK-394812',
    title: 'Bétonnière Chantier 160L',
    period: '26 Août ➔ 29 Août 2026',
    total_mad: 459,
    deposit_mad: 1500,
    status: 'Confirmée (En attente check-in)',
    cmi_status: 'Caution Bloquée CMI'
  }
];

export default function BookingsScreen({ onOpenInspection }) {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.headerTitle}>Mes Baux & Cautions Séquestrées</Text>
      <Text style={styles.headerSubtitle}>Suivi en temps réel sous Dahir des Obligations et Contrats</Text>

      {MOCK_BOOKINGS.map((b) => (
        <View key={b.id} style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.refText}>{b.id}</Text>
            <Text style={styles.statusBadge}>{b.status}</Text>
          </View>

          <Text style={styles.titleText}>{b.title}</Text>
          <Text style={styles.periodText}>Période : {b.period}</Text>

          <View style={styles.amountRow}>
            <Text style={styles.amountLabel}>Montant Location : <Text style={styles.amountVal}>{b.total_mad} MAD</Text></Text>
            <Text style={styles.cautionLabel}>Caution CMI : <Text style={styles.cautionVal}>{b.deposit_mad} MAD</Text></Text>
          </View>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => onOpenInspection(b)}
          >
            <Text style={styles.actionButtonText}>Ouvrir l'État des Lieux Vidéo</Text>
          </TouchableOpacity>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 16 },
  headerTitle: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  headerSubtitle: { fontSize: 11, color: '#64748B', marginBottom: 16, marginTop: 2 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  refText: { fontSize: 12, fontWeight: 'bold', color: '#0F6E56', fontFamily: 'monospace' },
  statusBadge: { fontSize: 10, fontWeight: 'bold', color: '#059669', backgroundColor: '#ECFDF5', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  titleText: { fontSize: 14, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  periodText: { fontSize: 11, color: '#64748B', marginBottom: 10 },
  amountRow: {
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    paddingTop: 8,
    marginBottom: 12,
  },
  amountLabel: { fontSize: 11, color: '#64748B' },
  amountVal: { fontWeight: 'bold', color: '#0F6E56' },
  cautionLabel: { fontSize: 11, color: '#64748B', marginTop: 2 },
  cautionVal: { fontWeight: 'bold', color: '#D85A30' },
  actionButton: {
    backgroundColor: '#0F6E56',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  actionButtonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 12 },
});
