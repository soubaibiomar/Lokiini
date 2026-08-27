import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, TextInput } from 'react-native';

export default function KYCCameraScreen({ onVerificationComplete }) {
  const [cin, setCin] = useState('BK849201');
  const [step, setStep] = useState(1); // 1: Info, 2: Camera Selfie, 3: Success
  const [isProcessing, setIsProcessing] = useState(false);

  const handleVerify = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setStep(3);
    }, 1200);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Vérification Biométrique CNDP</Text>
        <Text style={styles.subtitle}>Conforme à la Loi n° 09-08 (Royaume du Maroc)</Text>
      </View>

      {step === 1 && (
        <View style={styles.card}>
          <Text style={styles.label}>Numéro de CIN Marocaine</Text>
          <TextInput
            style={styles.input}
            value={cin}
            onChangeText={(t) => setCin(t.toUpperCase())}
            placeholder="Ex: BK123456"
          />

          <View style={styles.docBox}>
            <Text style={styles.docBoxText}>Scannez le Recto et Verso de votre CIN</Text>
          </View>

          <TouchableOpacity style={styles.primaryButton} onPress={() => setStep(2)}>
            <Text style={styles.buttonText}>Continuer vers le Selfie Vivant</Text>
          </TouchableOpacity>
        </View>
      )}

      {step === 2 && (
        <View style={styles.card}>
          <View style={styles.cameraPlaceholder}>
            <Text style={styles.cameraText}>CAMERA LIVE STREAM</Text>
            <Text style={styles.livenessHint}>Tournez la tête lentement pour le test anti-deepfake</Text>
          </View>

          <View style={styles.zkBadge}>
            <Text style={styles.zkText}>Zero-Knowledge : flux vidéo éphémère purgé de la RAM</Text>
          </View>

          <TouchableOpacity
            style={styles.primaryButton}
            onPress={handleVerify}
            disabled={isProcessing}
          >
            <Text style={styles.buttonText}>
              {isProcessing ? 'Validation algorithmique...' : 'Valider mon Liveness Check'}
            </Text>
          </TouchableOpacity>
        </View>
      )}

      {step === 3 && (
        <View style={styles.card}>
          <View style={styles.successBadge}>
            <Text style={styles.successIcon}>✓</Text>
          </View>
          <Text style={styles.successTitle}>Identité Certifiée CNDP</Text>
          <Text style={styles.successScore}>Score de vivacité : 96.8% (Conforme)</Text>
          <Text style={styles.auditHash}>Empreinte SHA-256 : d4b7...8092f9</Text>

          <TouchableOpacity style={styles.primaryButton} onPress={onVerificationComplete}>
            <Text style={styles.buttonText}>Accéder aux Réservations</Text>
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 16 },
  header: { marginBottom: 16 },
  title: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  subtitle: { fontSize: 11, color: '#64748B', marginTop: 2 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  label: { fontSize: 11, fontWeight: 'bold', color: '#475569', marginBottom: 6 },
  input: {
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontWeight: 'bold',
    fontSize: 14,
    marginBottom: 16,
  },
  docBox: {
    borderWidth: 2,
    borderColor: '#E2E8F0',
    borderStyle: 'dashed',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 20,
  },
  docBoxText: { fontSize: 12, color: '#64748B', fontWeight: '600' },
  cameraPlaceholder: {
    backgroundColor: '#0F172A',
    borderRadius: 16,
    height: 220,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  cameraText: { color: '#38BDF8', fontWeight: 'bold', fontSize: 13 },
  livenessHint: { color: '#94A3B8', fontSize: 10, marginTop: 6 },
  zkBadge: {
    backgroundColor: '#FEF3C7',
    padding: 10,
    borderRadius: 8,
    marginBottom: 16,
  },
  zkText: { color: '#92400E', fontSize: 10 },
  primaryButton: {
    backgroundColor: '#0F6E56',
    paddingVertical: 12,
    borderRadius: 10,
    alignItems: 'center',
  },
  buttonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 13 },
  successBadge: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#D1FAE5',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
    marginBottom: 12,
  },
  successIcon: { fontSize: 28, color: '#059669', fontWeight: 'bold' },
  successTitle: { fontSize: 16, fontWeight: '900', textAlign: 'center', color: '#1E293B' },
  successScore: { fontSize: 12, color: '#059669', textAlign: 'center', fontWeight: 'bold', marginTop: 4 },
  auditHash: { fontSize: 10, color: '#64748B', textAlign: 'center', marginVertical: 12, fontFamily: 'monospace' },
});
