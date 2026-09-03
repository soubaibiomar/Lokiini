import * as ImagePicker from 'expo-image-picker';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import {
  confirmInspection,
  getBookingInspections,
  submitStructuredInspection,
  uploadInspectionEvidence,
} from '../services/inspections';

export default function VideoInspectionScreen({ booking, onInspectionComplete }) {
  const [inspectionType, setInspectionType] = useState('check_in'); // 'check_in' | 'check_out'
  const [condition, setCondition] = useState('good'); // 'good' | 'fair' | 'damaged'
  const [serialNumber, setSerialNumber] = useState('');
  const [meterReading, setMeterReading] = useState('');
  const [notes, setNotes] = useState('');
  const [photos, setPhotos] = useState([]); // [{ uri, evidenceId, uploading }]
  const [existingInspections, setExistingInspections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const bookingId = booking?.id || booking?.reservation_id;

  const loadInspections = useCallback(async () => {
    if (!bookingId) return;
    setLoading(true);
    try {
      const list = await getBookingInspections(bookingId);
      setExistingInspections(Array.isArray(list) ? list : []);
    } catch {
      // Quiet fallback
    } finally {
      setLoading(false);
    }
  }, [bookingId]);

  useEffect(() => {
    loadInspections();
  }, [loadInspections]);

  const handlePickImage = async () => {
    try {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'Accès à la galerie photo requis pour l’état des lieux.');
        return;
      }

      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 0.8,
      });

      if (!result.canceled && result.assets?.[0]) {
        const asset = result.assets[0];
        await handleUploadPhoto(asset.uri);
      }
    } catch (err) {
      setError(err.message || 'Erreur lors de la sélection de photo.');
    }
  };

  const handleTakePhoto = async () => {
    try {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission requise', 'Accès caméra requis pour prendre une photo d’état des lieux.');
        return;
      }

      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 0.8,
      });

      if (!result.canceled && result.assets?.[0]) {
        const asset = result.assets[0];
        await handleUploadPhoto(asset.uri);
      }
    } catch (err) {
      setError(err.message || 'Erreur lors de la prise de photo.');
    }
  };

  const handleUploadPhoto = async (uri) => {
    if (!bookingId) {
      setError('Veuillez sélectionner une réservation avant d’ajouter des photos.');
      return;
    }
    const tempId = String(Date.now());
    setPhotos((prev) => [...prev, { id: tempId, uri, uploading: true }]);
    setError(null);

    try {
      const evidence = await uploadInspectionEvidence({
        bookingId,
        inspectionType,
        fileUri: uri,
        filename: `inspection-${inspectionType}-${Date.now()}.jpg`,
      });

      setPhotos((prev) => prev.map((p) => (p.id === tempId ? { ...p, uploading: false, evidenceId: evidence.id } : p)));
    } catch (err) {
      setError(err.message || 'Échec de l’envoi de la photo.');
      setPhotos((prev) => prev.filter((p) => p.id !== tempId));
    }
  };

  const handleSubmit = async () => {
    if (!bookingId) {
      setError('Réservation introuvable.');
      return;
    }

    const uploadedEvidenceIds = photos.filter((p) => p.evidenceId).map((p) => p.evidenceId);
    if (uploadedEvidenceIds.length === 0) {
      setError('Veuillez ajouter au moins une photo pour sceller l’état des lieux.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const result = await submitStructuredInspection({
        bookingId,
        inspectionType,
        evidenceIds: uploadedEvidenceIds,
        condition,
        serialNumber: serialNumber.trim() || null,
        meterType: meterReading.trim() ? 'hours' : null,
        meterReading: meterReading.trim() ? parseFloat(meterReading) : null,
        notes: notes.trim() || null,
        confirmed: true,
      });
      setSuccess(result);
      await loadInspections();
    } catch (err) {
      setError(err.message || 'Échec de l’enregistrement de l’état des lieux.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmExisting = async (inspectionId) => {
    setSubmitting(true);
    setError(null);
    try {
      await confirmInspection(inspectionId, { confirmed: true });
      await loadInspections();
      Alert.alert('Succès', 'État des lieux contradictoire validé par les deux parties.');
    } catch (err) {
      setError(err.message || 'Impossible de confirmer cet état des lieux.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>État des Lieux Contradictoire</Text>
        <Text style={styles.subtitle}>Enregistrement certifié des photos et observations du matériel</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.equipmentTitle}>
          {booking?.article_titre || booking?.title || 'Matériel sélectionné'}
        </Text>
        {bookingId ? (
          <Text style={styles.refInfo}>Bail : {String(bookingId).slice(0, 8).toUpperCase()}</Text>
        ) : null}

        {/* Existing inspections if any */}
        {existingInspections.length > 0 ? (
          <View style={styles.existingBox}>
            <Text style={styles.existingTitle}>États des lieux enregistrés :</Text>
            {existingInspections.map((insp) => (
              <View key={insp.id} style={styles.existingItem}>
                <View style={styles.existingRow}>
                  <Text style={styles.existingType}>
                    {insp.inspection_type === 'check_in' ? 'Départ (Check-in)' : 'Retour (Check-out)'}
                  </Text>
                  <Text style={styles.existingStatus}>{insp.statut || 'Enregistré'}</Text>
                </View>
                <Text style={styles.existingDetail}>
                  État : {insp.condition || 'Bon'} • Photos : {insp.photos?.length || 0}
                </Text>
                {insp.statut === 'pending_counterparty' ? (
                  <TouchableOpacity
                    style={styles.confirmButton}
                    onPress={() => handleConfirmExisting(insp.id)}
                    disabled={submitting}
                  >
                    <Text style={styles.confirmButtonText}>Valider et Contresigner</Text>
                  </TouchableOpacity>
                ) : null}
              </View>
            ))}
          </View>
        ) : null}

        {/* New Inspection Form */}
        {success ? (
          <View style={styles.successBox}>
            <Text style={styles.successTitle}>✓ État des lieux enregistré avec succès</Text>
            <Text style={styles.successText}>Réf : {success.id}</Text>
            <Text style={styles.successText}>Statut : {success.statut}</Text>
            <TouchableOpacity style={styles.primaryButton} onPress={onInspectionComplete}>
              <Text style={styles.buttonText}>Retour aux baux</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View>
            {/* Step 1: Type Selection */}
            <Text style={styles.sectionLabel}>Type d’état des lieux</Text>
            <View style={styles.typeSelector}>
              <TouchableOpacity
                style={[styles.typeOption, inspectionType === 'check_in' && styles.typeOptionActive]}
                onPress={() => setInspectionType('check_in')}
              >
                <Text style={[styles.typeText, inspectionType === 'check_in' && styles.typeTextActive]}>
                  Remise / Départ
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.typeOption, inspectionType === 'check_out' && styles.typeOptionActive]}
                onPress={() => setInspectionType('check_out')}
              >
                <Text style={[styles.typeText, inspectionType === 'check_out' && styles.typeTextActive]}>
                  Restitution / Retour
                </Text>
              </TouchableOpacity>
            </View>

            {/* Step 2: Photo Evidence Capture */}
            <Text style={styles.sectionLabel}>Preuves photographiques (Caméra / Galerie)</Text>
            <View style={styles.photoActions}>
              <TouchableOpacity style={styles.cameraBtn} onPress={handleTakePhoto}>
                <Text style={styles.cameraBtnText}>📷 Prendre une photo</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.galleryBtn} onPress={handlePickImage}>
                <Text style={styles.galleryBtnText}>🖼 Galerie</Text>
              </TouchableOpacity>
            </View>

            {/* Photos Preview Grid */}
            <View style={styles.photoGrid}>
              {photos.map((p) => (
                <View key={p.id} style={styles.photoThumbWrapper}>
                  <Image source={{ uri: p.uri }} style={styles.photoThumb} />
                  {p.uploading && (
                    <View style={styles.uploadOverlay}>
                      <ActivityIndicator size="small" color="#FFFFFF" />
                    </View>
                  )}
                  {p.evidenceId && <Text style={styles.checkIcon}>✓</Text>}
                </View>
              ))}
            </View>

            {/* Step 3: Condition */}
            <Text style={styles.sectionLabel}>État général du matériel</Text>
            <View style={styles.typeSelector}>
              <TouchableOpacity
                style={[styles.typeOption, condition === 'good' && styles.typeOptionActive]}
                onPress={() => setCondition('good')}
              >
                <Text style={[styles.typeText, condition === 'good' && styles.typeTextActive]}>Bon état</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.typeOption, condition === 'fair' && styles.typeOptionActive]}
                onPress={() => setCondition('fair')}
              >
                <Text style={[styles.typeText, condition === 'fair' && styles.typeTextActive]}>Usure normale</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.typeOption, condition === 'damaged' && styles.typeOptionActive]}
                onPress={() => setCondition('damaged')}
              >
                <Text style={[styles.typeText, condition === 'damaged' && styles.typeTextActive]}>Endommagé</Text>
              </TouchableOpacity>
            </View>

            {/* Serial Number & Meter */}
            <Text style={styles.sectionLabel}>Numéro de série / Châssis (optionnel)</Text>
            <TextInput
              style={styles.input}
              value={serialNumber}
              onChangeText={setSerialNumber}
              placeholder="Ex: LK-892347-MA"
            />

            <Text style={styles.sectionLabel}>Compteur horaire / kilométrique (optionnel)</Text>
            <TextInput
              style={styles.input}
              value={meterReading}
              onChangeText={setMeterReading}
              keyboardType="numeric"
              placeholder="Ex: 145"
            />

            <Text style={styles.sectionLabel}>Remarques & observations contradictoires</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={notes}
              onChangeText={setNotes}
              multiline
              numberOfLines={3}
              placeholder="Ex: Légère rayure sur le carter droit, accessoires vérifiés..."
            />

            {error ? <Text style={styles.errorText}>{error}</Text> : null}

            <TouchableOpacity
              style={styles.primaryButton}
              onPress={handleSubmit}
              disabled={submitting || loading}
            >
              {submitting ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <Text style={styles.buttonText}>Enregistrer l'État des Lieux</Text>
              )}
            </TouchableOpacity>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  content: { padding: 16 },
  header: { marginBottom: 14 },
  title: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  subtitle: { fontSize: 11, color: '#64748B', marginTop: 2 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  equipmentTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E293B' },
  refInfo: { fontSize: 11, color: '#0F6E56', fontWeight: 'bold', marginBottom: 12, marginTop: 2 },
  sectionLabel: { fontSize: 11, fontWeight: 'bold', color: '#475569', marginTop: 12, marginBottom: 6 },
  typeSelector: { flexDirection: 'row', gap: 6, marginBottom: 8 },
  typeOption: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    backgroundColor: '#F8FAFC',
  },
  typeOptionActive: {
    backgroundColor: '#E6FCF5',
    borderColor: '#0F6E56',
  },
  typeText: { fontSize: 11, color: '#64748B', fontWeight: '600' },
  typeTextActive: { color: '#0F6E56', fontWeight: 'bold' },
  photoActions: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  cameraBtn: {
    flex: 1,
    backgroundColor: '#0F6E56',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
  },
  cameraBtnText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 11 },
  galleryBtn: {
    flex: 1,
    backgroundColor: '#F1F5F9',
    borderRadius: 8,
    paddingVertical: 10,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#CBD5E1',
  },
  galleryBtnText: { color: '#475569', fontWeight: '700', fontSize: 11 },
  photoGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 10 },
  photoThumbWrapper: { position: 'relative', width: 68, height: 68, borderRadius: 8, overflow: 'hidden' },
  photoThumb: { width: '100%', height: '100%' },
  uploadOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkIcon: {
    position: 'absolute',
    right: 4,
    bottom: 4,
    backgroundColor: '#059669',
    color: '#FFFFFF',
    fontSize: 10,
    paddingHorizontal: 4,
    borderRadius: 6,
    fontWeight: 'bold',
  },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 8,
    padding: 10,
    fontSize: 12,
    marginBottom: 6,
  },
  textArea: { height: 64, textAlignVertical: 'top' },
  primaryButton: {
    backgroundColor: '#0F6E56',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 14,
  },
  buttonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 13 },
  errorText: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 8, borderRadius: 6, fontSize: 11, marginTop: 8 },
  existingBox: { backgroundColor: '#F8FAFC', borderRadius: 10, padding: 10, marginBottom: 14, borderWidth: 1, borderColor: '#E2E8F0' },
  existingTitle: { fontSize: 11, fontWeight: 'bold', color: '#1E293B', marginBottom: 6 },
  existingItem: { backgroundColor: '#FFFFFF', padding: 8, borderRadius: 8, marginBottom: 6, borderWidth: 1, borderColor: '#E2E8F0' },
  existingRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 2 },
  existingType: { fontSize: 11, fontWeight: 'bold', color: '#0F6E56' },
  existingStatus: { fontSize: 10, color: '#64748B', fontWeight: '600' },
  existingDetail: { fontSize: 10, color: '#475569' },
  confirmButton: { backgroundColor: '#0F6E56', borderRadius: 6, paddingVertical: 6, alignItems: 'center', marginTop: 6 },
  confirmButtonText: { color: '#FFFFFF', fontSize: 10, fontWeight: 'bold' },
  successBox: { backgroundColor: '#ECFDF5', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#A7F3D0', alignItems: 'center' },
  successTitle: { color: '#065F46', fontWeight: 'bold', fontSize: 14, marginBottom: 4 },
  successText: { color: '#047857', fontSize: 11, marginBottom: 4 },
});
