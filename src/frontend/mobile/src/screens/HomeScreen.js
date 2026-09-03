import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Modal,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import { calculateBookingQuote, createBooking } from '../services/bookings';
import { getEquipmentList } from '../services/equipment';

const CITIES = ['Toutes les villes', 'Casablanca', 'Rabat', 'Marrakech', 'Tanger', 'Fès', 'Agadir'];

const CATEGORIES = [
  { id: 'all', label: 'Toutes' },
  { id: 'btp', label: 'BTP & Chantier' },
  { id: 'tools', label: 'Outillage' },
  { id: 'audiovisual', label: 'Audiovisuel' },
  { id: 'events', label: 'Événementiel' },
  { id: 'transport', label: 'Véhicules' },
];

export default function HomeScreen({ onSelectBooking, onStartKYC, onOpenConversation }) {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedCity, setSelectedCity] = useState('Toutes les villes');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [error, setError] = useState(null);

  // Booking Modal State
  const [selectedItem, setSelectedItem] = useState(null);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [quote, setQuote] = useState(null);
  const [quoteLoading, setQuoteLoading] = useState(false);
  const [quoteError, setQuoteError] = useState(null);
  const [bookingSubmitting, setBookingSubmitting] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState(null);

  const fetchEquipment = useCallback(async () => {
    setError(null);
    try {
      const data = await getEquipmentList({
        search: search.trim() || undefined,
        city: selectedCity !== 'Toutes les villes' ? selectedCity : undefined,
        category: selectedCategory !== 'all' ? selectedCategory : undefined,
      });
      // Handle both array response and paginated { items: [] } / { articles: [] }
      const items = Array.isArray(data) ? data : data?.items || data?.articles || [];
      setEquipment(items);
    } catch (err) {
      setError(err.message || 'Impossible de charger les équipements.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [search, selectedCity, selectedCategory]);

  useEffect(() => {
    setLoading(true);
    fetchEquipment();
  }, [fetchEquipment]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchEquipment();
  };

  const handleOpenBookingModal = (item) => {
    setSelectedItem(item);
    // Default dates: tomorrow to 3 days after tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const end = new Date();
    end.setDate(end.getDate() + 4);
    const startStr = tomorrow.toISOString().split('T')[0];
    const endStr = end.toISOString().split('T')[0];
    setStartDate(startStr);
    setEndDate(endStr);
    setQuote(null);
    setQuoteError(null);
    setBookingSuccess(null);
  };

  const handleCalculateQuote = async () => {
    if (!selectedItem || !startDate || !endDate) return;
    setQuoteLoading(true);
    setQuoteError(null);
    try {
      const breakdown = await calculateBookingQuote({
        articleId: selectedItem.id,
        startDate,
        endDate,
      });
      setQuote(breakdown);
    } catch (err) {
      setQuoteError(err.message || 'Calcul du devis indisponible.');
    } finally {
      setQuoteLoading(false);
    }
  };

  const handleConfirmBooking = async () => {
    if (!selectedItem || !startDate || !endDate) return;
    setBookingSubmitting(true);
    setQuoteError(null);
    try {
      const result = await createBooking({
        articleId: selectedItem.id,
        startDate,
        endDate,
      });
      setBookingSuccess(result);
    } catch (err) {
      setQuoteError(err.message || 'Échec de la réservation.');
    } finally {
      setBookingSubmitting(false);
    }
  };

  const renderHeader = () => (
    <View>
      {/* Banner */}
      <View style={styles.banner}>
        <Text style={styles.bannerTitle}>Location de Matériel Sécurisée</Text>
        <Text style={styles.bannerSubtitle}>
          Contrats conformes Dahir des Obligations • Caution CMI séquestrée • États des lieux contradictoires
        </Text>
        <TouchableOpacity style={styles.kycButton} onPress={onStartKYC}>
          <Text style={styles.kycButtonText}>Vérifier mon identité</Text>
        </TouchableOpacity>
      </View>

      {/* Search Input */}
      <View style={styles.searchContainer}>
        <TextInput
          style={styles.searchInput}
          placeholder="Rechercher une machine, outil, marque..."
          value={search}
          onChangeText={setSearch}
          returnKeyType="search"
          onSubmitEditing={fetchEquipment}
        />
        {search.length > 0 && (
          <TouchableOpacity onPress={() => setSearch('')} style={styles.clearBtn}>
            <Text style={styles.clearBtnText}>✕</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* City filter */}
      <FlatList
        horizontal
        showsHorizontalScrollIndicator={false}
        data={CITIES}
        keyExtractor={(city) => city}
        style={styles.filterScroll}
        renderItem={({ item: city }) => (
          <TouchableOpacity
            style={[styles.cityChip, selectedCity === city && styles.cityChipActive]}
            onPress={() => setSelectedCity(city)}
          >
            <Text style={[styles.cityChipText, selectedCity === city && styles.cityChipTextActive]}>
              {city}
            </Text>
          </TouchableOpacity>
        )}
      />

      {/* Category filter */}
      <FlatList
        horizontal
        showsHorizontalScrollIndicator={false}
        data={CATEGORIES}
        keyExtractor={(cat) => cat.id}
        style={styles.categoryScroll}
        renderItem={({ item: cat }) => (
          <TouchableOpacity
            style={[styles.categoryChip, selectedCategory === cat.id && styles.categoryChipActive]}
            onPress={() => setSelectedCategory(cat.id)}
          >
            <Text style={[styles.categoryChipText, selectedCategory === cat.id && styles.categoryChipTextActive]}>
              {cat.label}
            </Text>
          </TouchableOpacity>
        )}
      />

      <View style={styles.resultsHeader}>
        <Text style={styles.sectionTitle}>
          Équipements disponibles ({equipment.length})
        </Text>
      </View>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}
    </View>
  );

  const renderItem = ({ item }) => (
    <View style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.cardCategory}>{item.categorie || item.category || 'MATÉRIEL'}</Text>
        <Text style={styles.cardCity}>{item.ville || item.city || 'Maroc'}</Text>
      </View>
      <Text style={styles.cardTitle}>{item.titre || item.title}</Text>
      {item.description ? (
        <Text style={styles.cardDescription} numberOfLines={2}>
          {item.description}
        </Text>
      ) : null}

      <View style={styles.priceRow}>
        <View>
          <Text style={styles.priceLabel}>Tarif journalier</Text>
          <Text style={styles.priceValue}>{item.prix_par_jour || item.daily_price_mad} MAD/j</Text>
        </View>
        <View style={styles.depositColumn}>
          <Text style={styles.priceLabel}>Caution requise</Text>
          <Text style={styles.depositValue}>{item.montant_caution || item.deposit_amount_mad || 0} MAD</Text>
        </View>
      </View>

      <View style={styles.cardActions}>
        <TouchableOpacity
          style={styles.bookButton}
          onPress={() => handleOpenBookingModal(item)}
        >
          <Text style={styles.bookButtonText}>Réserver</Text>
        </TouchableOpacity>

        {onOpenConversation && item.loueur_id ? (
          <TouchableOpacity
            style={styles.contactButton}
            onPress={() => onOpenConversation({ recipientId: item.loueur_id, equipmentId: item.id })}
          >
            <Text style={styles.contactButtonText}>Message</Text>
          </TouchableOpacity>
        ) : null}
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0F6E56" />
          <Text style={styles.loadingText}>Chargement du catalogue...</Text>
        </View>
      ) : (
        <FlatList
          data={equipment}
          keyExtractor={(item) => String(item.id)}
          renderItem={renderItem}
          ListHeaderComponent={renderHeader}
          contentContainerStyle={styles.content}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#0F6E56']} />}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>Aucun matériel trouvé</Text>
              <Text style={styles.emptySubtitle}>Essayez de modifier votre recherche ou vos filtres de ville/catégorie.</Text>
            </View>
          }
        />
      )}

      {/* Booking / Quote Modal */}
      <Modal visible={!!selectedItem} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>{selectedItem?.titre || selectedItem?.title}</Text>
            <Text style={styles.modalSubtitle}>Tarif : {selectedItem?.prix_par_jour} MAD/j • Caution : {selectedItem?.montant_caution} MAD</Text>

            {bookingSuccess ? (
              <View style={styles.successBox}>
                <Text style={styles.successTitle}>✓ Demande de réservation envoyée</Text>
                <Text style={styles.successText}>Réf : {bookingSuccess.reservation_id}</Text>
                <Text style={styles.successText}>Total : {bookingSuccess.total_location_mad} MAD</Text>
                <TouchableOpacity
                  style={styles.modalPrimaryBtn}
                  onPress={() => {
                    const booking = { id: bookingSuccess.reservation_id, ...selectedItem };
                    setSelectedItem(null);
                    if (onSelectBooking) onSelectBooking(booking);
                  }}
                >
                  <Text style={styles.modalPrimaryBtnText}>Voir mes réservations</Text>
                </TouchableOpacity>
              </View>
            ) : (
              <View>
                <Text style={styles.fieldLabel}>Date de début (AAAA-MM-JJ)</Text>
                <TextInput
                  style={styles.modalInput}
                  value={startDate}
                  onChangeText={setStartDate}
                  placeholder="2026-09-05"
                />

                <Text style={styles.fieldLabel}>Date de fin (AAAA-MM-JJ)</Text>
                <TextInput
                  style={styles.modalInput}
                  value={endDate}
                  onChangeText={setEndDate}
                  placeholder="2026-09-08"
                />

                {quoteError ? <Text style={styles.modalError}>{quoteError}</Text> : null}

                {quote ? (
                  <View style={styles.quoteBox}>
                    <Text style={styles.quoteLine}>Nombre de jours : {quote.nombre_jours}</Text>
                    <Text style={styles.quoteLine}>Total location : <Text style={styles.bold}>{quote.total_location_mad} MAD</Text></Text>
                    <Text style={styles.quoteLine}>Caution séquestrée : <Text style={styles.bold}>{quote.montant_caution_mad} MAD</Text></Text>
                    {quote.taux_remise_duree > 0 ? (
                      <Text style={styles.discountText}>Remise longue durée appliquée : -{quote.taux_remise_duree * 100}%</Text>
                    ) : null}
                  </View>
                ) : (
                  <TouchableOpacity
                    style={styles.quoteBtn}
                    onPress={handleCalculateQuote}
                    disabled={quoteLoading}
                  >
                    {quoteLoading ? (
                      <ActivityIndicator color="#0F6E56" />
                    ) : (
                      <Text style={styles.quoteBtnText}>Calculer le devis officiel</Text>
                    )}
                  </TouchableOpacity>
                )}

                {quote ? (
                  <TouchableOpacity
                    style={styles.modalPrimaryBtn}
                    onPress={handleConfirmBooking}
                    disabled={bookingSubmitting}
                  >
                    {bookingSubmitting ? (
                      <ActivityIndicator color="#FFFFFF" />
                    ) : (
                      <Text style={styles.modalPrimaryBtnText}>Confirmer la réservation</Text>
                    )}
                  </TouchableOpacity>
                ) : null}

                <TouchableOpacity
                  style={styles.modalCloseBtn}
                  onPress={() => setSelectedItem(null)}
                >
                  <Text style={styles.modalCloseText}>Fermer</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  content: { padding: 16 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, color: '#64748B', fontWeight: '600' },
  banner: {
    backgroundColor: '#0F6E56',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
  },
  bannerTitle: { color: '#FFFFFF', fontSize: 19, fontWeight: '900', marginBottom: 4 },
  bannerSubtitle: { color: '#E6FCF5', fontSize: 11, lineHeight: 16, marginBottom: 12 },
  kycButton: {
    backgroundColor: '#D85A30',
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  kycButtonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 11 },
  searchContainer: {
    position: 'relative',
    marginBottom: 10,
  },
  searchInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 13,
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  clearBtn: { position: 'absolute', right: 12, top: 12 },
  clearBtnText: { color: '#94A3B8', fontWeight: 'bold' },
  filterScroll: { marginBottom: 8 },
  cityChip: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cityChipActive: {
    backgroundColor: '#0F6E56',
    borderColor: '#0F6E56',
  },
  cityChipText: { fontSize: 11, color: '#475569', fontWeight: '600' },
  cityChipTextActive: { color: '#FFFFFF' },
  categoryScroll: { marginBottom: 14 },
  categoryChip: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    marginRight: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  categoryChipActive: {
    backgroundColor: '#E6FCF5',
    borderColor: '#0F6E56',
  },
  categoryChipText: { fontSize: 11, color: '#64748B', fontWeight: '700' },
  categoryChipTextActive: { color: '#0F6E56' },
  resultsHeader: { marginBottom: 8 },
  sectionTitle: { fontSize: 15, fontWeight: '900', color: '#1E293B' },
  errorText: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 8, borderRadius: 8, marginBottom: 10, fontSize: 12 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  cardCategory: { fontSize: 10, fontWeight: 'bold', color: '#0F6E56', textTransform: 'uppercase' },
  cardCity: { fontSize: 10, color: '#64748B', fontWeight: '600' },
  cardTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  cardDescription: { fontSize: 11, color: '#64748B', marginBottom: 10, lineHeight: 15 },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderTopWidth: 1,
    borderTopColor: '#F1F5F9',
    marginBottom: 10,
  },
  priceLabel: { fontSize: 10, color: '#94A3B8' },
  priceValue: { fontSize: 15, fontWeight: '900', color: '#0F6E56' },
  depositColumn: { alignItems: 'flex-end' },
  depositValue: { fontSize: 12, fontWeight: 'bold', color: '#D85A30' },
  cardActions: { flexDirection: 'row', gap: 8 },
  bookButton: {
    flex: 1,
    backgroundColor: '#0F6E56',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  bookButtonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 12 },
  contactButton: {
    backgroundColor: '#F1F5F9',
    borderRadius: 8,
    paddingVertical: 10,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  contactButtonText: { color: '#475569', fontWeight: '700', fontSize: 12 },
  emptyContainer: { padding: 40, alignItems: 'center' },
  emptyTitle: { fontSize: 16, fontWeight: 'bold', color: '#1E293B', marginBottom: 6 },
  emptySubtitle: { fontSize: 12, color: '#64748B', textAlign: 'center' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', padding: 20 },
  modalContent: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 20 },
  modalTitle: { fontSize: 17, fontWeight: '900', color: '#1E293B', marginBottom: 4 },
  modalSubtitle: { fontSize: 12, color: '#64748B', marginBottom: 16 },
  fieldLabel: { fontSize: 11, fontWeight: 'bold', color: '#475569', marginBottom: 4 },
  modalInput: { backgroundColor: '#F8FAFC', borderWidth: 1, borderColor: '#CBD5E1', borderRadius: 8, padding: 10, marginBottom: 12, fontSize: 13 },
  quoteBox: { backgroundColor: '#F0FDFA', borderRadius: 10, padding: 12, marginBottom: 14, borderWidth: 1, borderColor: '#CCFBF1' },
  quoteLine: { fontSize: 12, color: '#0F6E56', marginBottom: 4 },
  bold: { fontWeight: '900' },
  discountText: { fontSize: 11, color: '#D85A30', fontWeight: 'bold', marginTop: 4 },
  quoteBtn: { borderWidth: 1, borderColor: '#0F6E56', borderRadius: 8, padding: 10, alignItems: 'center', marginBottom: 12 },
  quoteBtnText: { color: '#0F6E56', fontWeight: 'bold', fontSize: 12 },
  modalPrimaryBtn: { backgroundColor: '#0F6E56', borderRadius: 8, padding: 12, alignItems: 'center', marginBottom: 8 },
  modalPrimaryBtnText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 13 },
  modalCloseBtn: { padding: 10, alignItems: 'center' },
  modalCloseText: { color: '#64748B', fontWeight: '600', fontSize: 12 },
  modalError: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 8, borderRadius: 6, fontSize: 11, marginBottom: 10 },
  successBox: { backgroundColor: '#ECFDF5', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#A7F3D0', alignItems: 'center' },
  successTitle: { color: '#065F46', fontWeight: 'bold', fontSize: 15, marginBottom: 6 },
  successText: { color: '#047857', fontSize: 12, marginBottom: 4 },
});
