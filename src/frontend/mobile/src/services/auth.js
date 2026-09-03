import AsyncStorage from '@react-native-async-storage/async-storage';
import { getApp, getApps, initializeApp } from 'firebase/app';
import {
  createUserWithEmailAndPassword,
  getAuth,
  getReactNativePersistence,
  initializeAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
} from 'firebase/auth';

const config = {
  apiKey: process.env.EXPO_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.EXPO_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.EXPO_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.EXPO_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.EXPO_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.EXPO_PUBLIC_FIREBASE_APP_ID,
};

export const isAuthConfigured = Object.values(config).every(Boolean);
const firebaseApp = isAuthConfigured ? (getApps().length ? getApp() : initializeApp(config)) : null;

let auth = null;
if (firebaseApp) {
  try {
    auth = initializeAuth(firebaseApp, { persistence: getReactNativePersistence(AsyncStorage) });
  } catch {
    auth = getAuth(firebaseApp);
  }
}
export { auth };

const apiBase = process.env.EXPO_PUBLIC_API_URL || 'http://10.0.2.2:8000/api/v1';

export const observeIdentity = (callback) => {
  if (!auth) {
    callback(null);
    return () => {};
  }
  return onAuthStateChanged(auth, callback);
};

export async function getBackendProfile(firebaseUser = auth?.currentUser) {
  if (!firebaseUser || !apiBase) throw new Error('Session mobile indisponible.');
  const idToken = await firebaseUser.getIdToken();
  const response = await fetch(`${apiBase.replace(/\/+$/, '')}/auth/me`, {
    headers: {
      Authorization: `Bearer ${idToken}`,
      Accept: 'application/json',
    },
  });
  if (!response.ok) {
    throw new Error(`Authentification backend refusée (${response.status}).`);
  }
  return response.json();
}

export async function login(email, password) {
  if (!auth) throw new Error("Firebase d'authentification mobile n'est pas configuré.");
  const credential = await signInWithEmailAndPassword(auth, email, password);
  return getBackendProfile(credential.user);
}

export async function register({ email, password, fullName, phone, role = 'renter' }) {
  if (!auth) throw new Error("Firebase d'authentification mobile n'est pas configuré.");
  const credential = await createUserWithEmailAndPassword(auth, email, password);
  if (fullName && credential.user) {
    await updateProfile(credential.user, { displayName: fullName });
  }
  // Initialize profile on FastAPI backend
  const idToken = await credential.user.getIdToken();
  try {
    await fetch(`${apiBase.replace(/\/+$/, '')}/auth/session`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${idToken}`,
      },
      body: JSON.stringify({
        id_token: idToken,
        nom_complet: fullName,
        telephone: phone,
        role,
      }),
    });
  } catch {
    // Session registration fallback
  }
  return getBackendProfile(credential.user);
}

export async function logout() {
  if (auth) await signOut(auth);
}
