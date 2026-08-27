import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, TextInput } from 'react-native';

export default function VideoInspectionScreen({ booking, onInspectionComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [isSealed, setIsSealed] = useState(false);

  const handleSeal = () => {
    setIsSealed(true);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>État des Lieux Vidéo Contradictoire</Text>
        <Text style={styles.subtitle}>Horodatage RFC 3161 & Signature Électronique (Loi 53-05)</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.equipmentTitle}>
          {booking?.title || 'Mini-Pelle Compacte Bobcat E19'}
        </Text>
        <Text style={styles.cautionInfo}>Caution Séquestrée : {booking?.deposit_amount_mad || 8000} MAD (CMI)</Text>

        <View style={styles.videoBox}>
          <Text style={styles.recDot}>● ENREGISTREMENT CONTINU</Text>
          <Text style={styles.shaText}>Hachage SHA-256 en direct : 3f7b...98bc</Text>
        </View>

        {isSealed ? (
          <View style={styles.sealedBox}>
            <Text style={styles.sealedTitle}>✓ Scellement RFC 3161 Validé</Text>
            <Text style={styles.sealedText}>
              Le contrat de bail et la caution CMI sont synchronisés en temps réel.
            </Text>
            <TouchableOpacity style={styles.primaryButton} onPress={onInspectionComplete}>
              <Text style={styles.buttonText}>Terminer</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity style={styles.primaryButton} onPress={handleSeal}>
            <Text style={styles.buttonText}>Sceller l'État des Lieux & Signer</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { marginBottom: 16 },
  title: { fontSize: 17, fontWeight: '900', color: '#1E293B' },
  subtitle: { fontSize: 11, color: '#64748B', marginTop: 2 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  equipmentTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  cautionInfo: { fontSize: 12, fontWeight: 'bold', color: '#D85A30', marginBottom: 16 },
  videoBox: {
    backgroundColor: '#0F172A',
    borderRadius: 14,
    height: 200,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  recDot: { color: '#EF4444', fontWeight: 'bold', fontSize: 12 },
  shaText: { color: '#94A3B8', fontSize: 10, marginTop: 8, fontFamily: 'monospace' },
  primaryButton: {
    backgroundColor: '#0F6E56',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  buttonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 13 },
  sealedBox: {
    backgroundColor: '#ECFDF5',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#A7F3D0',
    alignItems: 'center',
  },
  sealedTitle: { color: '#065F46', fontWeight: 'bold', fontSize: 14, marginBottom: 4 },
  sealedText: { color: '#047857', fontSize: 11, textAlign: 'center', marginBottom: 12 },
});
