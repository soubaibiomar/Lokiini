import React, { useState } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';

const MOCK_EQUIPMENT = [
  {
    id: 'e1',
    title: 'Tente Caïdale Royale 50m²',
    city: 'Marrakech',
    category: 'Événementiel',
    daily_price_mad: 1200,
    deposit_amount_mad: 4000
  },
  {
    id: 'e2',
    title: 'Caméra Sony FX3 4K + Drones',
    city: 'Casablanca',
    category: 'Audiovisuel',
    daily_price_mad: 450,
    deposit_amount_mad: 5000
  },
  {
    id: 'e3',
    title: 'Fourgon Utilitaire Renault Master',
    city: 'Casablanca',
    category: 'Véhicules',
    daily_price_mad: 450,
    deposit_amount_mad: 3500
  },
  {
    id: 'e4',
    title: 'Pack Casque VR Meta Quest 3',
    city: 'Rabat',
    category: 'High-Tech',
    daily_price_mad: 200,
    deposit_amount_mad: 2000
  },
  {
    id: 'e5',
    title: 'Nettoyeur Haute Pression Kärcher Pro',
    city: 'Tanger',
    category: 'Outillage',
    daily_price_mad: 150,
    deposit_amount_mad: 1200
  }
];

export default function HomeScreen({ onSelectBooking, onStartKYC }) {
  const [selectedCity, setSelectedCity] = useState('Toutes les villes');

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Banner */}
      <View style={styles.banner}>
        <Text style={styles.bannerTitle}>Location de Matériel Sécurisée</Text>
        <Text style={styles.bannerSubtitle}>
          Caution bloquée non débitée (CMI) • Contrats DOC Loi 53-05
        </Text>
        <TouchableOpacity style={styles.kycButton} onPress={onStartKYC}>
          <Text style={styles.kycButtonText}>Vérifier mon identité CNDP</Text>
        </TouchableOpacity>
      </View>

      {/* Equipment List */}
      <Text style={styles.sectionTitle}>Machines & Équipements Disponibles</Text>
      {MOCK_EQUIPMENT.map((item) => (
        <View key={item.id} style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardCategory}>{item.category}</Text>
            <Text style={styles.cardCity}>{item.city}</Text>
          </View>
          <Text style={styles.cardTitle}>{item.title}</Text>
          <View style={styles.priceRow}>
            <View>
              <Text style={styles.priceLabel}>Tarif journalier</Text>
              <Text style={styles.priceValue}>{item.daily_price_mad} MAD/j</Text>
            </View>
            <View style={{ alignItems: 'flex-end' }}>
              <Text style={styles.priceLabel}>Caution CMI (Séquestre)</Text>
              <Text style={styles.depositValue}>{item.deposit_amount_mad} MAD</Text>
            </View>
          </View>
          <TouchableOpacity
            style={styles.bookButton}
            onPress={() => onSelectBooking(item)}
          >
            <Text style={styles.bookButtonText}>Réserver & Sceller l'État des Lieux</Text>
          </TouchableOpacity>
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1 },
  content: { padding: 16 },
  banner: {
    backgroundColor: '#0F6E56',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
  },
  bannerTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '900',
    marginBottom: 4,
  },
  bannerSubtitle: {
    color: '#E6FCF5',
    fontSize: 12,
    marginBottom: 12,
    lineHeight: 18,
  },
  kycButton: {
    backgroundColor: '#D85A30',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 10,
    alignSelf: 'flex-start',
  },
  kycButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 12,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '900',
    color: '#1E293B',
    marginBottom: 12,
  },
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
    marginBottom: 6,
  },
  cardCategory: {
    fontSize: 10,
    fontWeight: 'bold',
    color: '#0F6E56',
    textTransform: 'uppercase',
  },
  cardCity: {
    fontSize: 10,
    color: '#64748B',
    fontWeight: '600',
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#1E293B',
    marginBottom: 12,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    marginBottom: 12,
  },
  priceLabel: {
    fontSize: 10,
    color: '#94A3B8',
  },
  priceValue: {
    fontSize: 16,
    fontWeight: '900',
    color: '#0F6E56',
  },
  depositValue: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#D85A30',
  },
  bookButton: {
    backgroundColor: '#0F6E56',
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: 'center',
  },
  bookButtonText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 12,
  },
});
