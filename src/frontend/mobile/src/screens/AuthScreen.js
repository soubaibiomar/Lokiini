import React, { useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import { login, register } from '../services/auth';

export default function AuthScreen({ onAuthenticated }) {
  const [mode, setMode] = useState('login'); // 'login' | 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState('renter'); // 'renter' | 'pro_owner'
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!email.trim() || !password.trim()) {
      setError('Veuillez renseigner votre e-mail et mot de passe.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      if (mode === 'login') {
        const user = await login(email.trim(), password);
        onAuthenticated(user);
      } else {
        const user = await register({
          email: email.trim(),
          password,
          fullName: fullName.trim() || undefined,
          phone: phone.trim() || undefined,
          role,
        });
        onAuthenticated(user);
      }
    } catch (err) {
      setError(err.message || 'Erreur lors de l’authentification.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Logo & Title */}
        <View style={styles.brandRow}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoText}>L</Text>
          </View>
          <Text style={styles.brandTitle}>Lokiini Maroc</Text>
        </View>

        <Text style={styles.subtitle}>Plateforme de location de matériel sécurisée</Text>

        {/* Mode Switcher */}
        <View style={styles.modeTabs}>
          <TouchableOpacity
            style={[styles.modeTab, mode === 'login' && styles.modeTabActive]}
            onPress={() => { setMode('login'); setError(null); }}
          >
            <Text style={[styles.modeTabText, mode === 'login' && styles.modeTabTextActive]}>
              Se connecter
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.modeTab, mode === 'register' && styles.modeTabActive]}
            onPress={() => { setMode('register'); setError(null); }}
          >
            <Text style={[styles.modeTabText, mode === 'register' && styles.modeTabTextActive]}>
              Créer un compte
            </Text>
          </TouchableOpacity>
        </View>

        {mode === 'register' && (
          <View>
            <Text style={styles.inputLabel}>Nom complet</Text>
            <TextInput
              style={styles.input}
              value={fullName}
              onChangeText={setFullName}
              placeholder="Ex: Karim Benjelloun"
            />

            <Text style={styles.inputLabel}>Numéro de téléphone marocain</Text>
            <TextInput
              style={styles.input}
              value={phone}
              onChangeText={setPhone}
              keyboardType="phone-pad"
              placeholder="+212 6 XX XX XX XX"
            />

            <Text style={styles.inputLabel}>Type d'activité</Text>
            <View style={styles.roleSelector}>
              <TouchableOpacity
                style={[styles.roleOption, role === 'renter' && styles.roleOptionActive]}
                onPress={() => setRole('renter')}
              >
                <Text style={[styles.roleText, role === 'renter' && styles.roleTextActive]}>
                  Particulier / Artisan
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.roleOption, role === 'pro_owner' && styles.roleOptionActive]}
                onPress={() => setRole('pro_owner')}
              >
                <Text style={[styles.roleText, role === 'pro_owner' && styles.roleTextActive]}>
                  Entreprise / Loueur Pro
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        )}

        <Text style={styles.inputLabel}>Adresse e-mail</Text>
        <TextInput
          style={styles.input}
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
          placeholder="nom@exemple.ma"
        />

        <Text style={styles.inputLabel}>Mot de passe</Text>
        <TextInput
          style={styles.input}
          secureTextEntry
          value={password}
          onChangeText={setPassword}
          placeholder="••••••••"
        />

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity style={styles.button} disabled={loading} onPress={submit}>
          {loading ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <Text style={styles.buttonText}>
              {mode === 'login' ? 'Accéder à mon espace' : 'Créer mon compte'}
            </Text>
          )}
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  scrollContent: { flexGrow: 1, justifyContent: 'center', padding: 24 },
  brandRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  logoBadge: {
    width: 38,
    height: 38,
    borderRadius: 10,
    backgroundColor: '#0F6E56',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  logoText: { color: '#FFFFFF', fontWeight: '900', fontSize: 22 },
  brandTitle: { fontSize: 24, fontWeight: '900', color: '#0F6E56' },
  subtitle: { color: '#64748B', fontSize: 12, marginBottom: 20 },
  modeTabs: { flexDirection: 'row', backgroundColor: '#E2E8F0', borderRadius: 10, padding: 3, marginBottom: 18 },
  modeTab: { flex: 1, paddingVertical: 8, alignItems: 'center', borderRadius: 8 },
  modeTabActive: { backgroundColor: '#FFFFFF' },
  modeTabText: { fontSize: 12, fontWeight: '600', color: '#64748B' },
  modeTabTextActive: { color: '#0F6E56', fontWeight: 'bold' },
  inputLabel: { fontSize: 11, fontWeight: 'bold', color: '#475569', marginBottom: 4 },
  input: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 10,
    padding: 12,
    fontSize: 13,
    marginBottom: 12,
  },
  roleSelector: { flexDirection: 'row', gap: 8, marginBottom: 12 },
  roleOption: {
    flex: 1,
    paddingVertical: 8,
    alignItems: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#CBD5E1',
    backgroundColor: '#FFFFFF',
  },
  roleOptionActive: { backgroundColor: '#E6FCF5', borderColor: '#0F6E56' },
  roleText: { fontSize: 11, color: '#64748B', fontWeight: '600' },
  roleTextActive: { color: '#0F6E56', fontWeight: 'bold' },
  error: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 10, borderRadius: 8, fontSize: 12, marginBottom: 12 },
  button: {
    backgroundColor: '#0F6E56',
    borderRadius: 10,
    minHeight: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 6,
  },
  buttonText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 14 },
});
