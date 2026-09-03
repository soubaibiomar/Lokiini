import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword,
  signInWithPopup, GoogleAuthProvider, signOut, onAuthStateChanged,
  sendPasswordResetEmail, updateProfile
} from 'firebase/auth';
import { createWebSession, deleteWebSession, getCurrentUser } from './api';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

export const isFirebaseConfigured = () => Object.values(firebaseConfig).every(Boolean);
const app = isFirebaseConfigured() ? (getApps().length ? getApp() : initializeApp(firebaseConfig)) : null;
export const auth = app ? getAuth(app) : null;
export const googleProvider = auth ? new GoogleAuthProvider() : null;
if (googleProvider) googleProvider.setCustomParameters({ prompt: 'select_account' });

const configurationError = () => ({
  ok: false,
  error: "L'authentification Firebase n'est pas configurée."
});

export function formatFirebaseError(error) {
  const code = error?.code || '';
  const messages = {
    'auth/invalid-email': "L'adresse e-mail n'est pas valide.",
    'auth/user-disabled': 'Ce compte utilisateur a été désactivé.',
    'auth/user-not-found': 'Aucun compte trouvé avec cette adresse e-mail.',
    'auth/wrong-password': 'Identifiant ou mot de passe incorrect.',
    'auth/invalid-credential': 'Identifiant ou mot de passe incorrect.',
    'auth/email-already-in-use': 'Un compte existe déjà avec cette adresse e-mail.',
    'auth/weak-password': 'Le mot de passe doit contenir au moins 6 caractères.',
    'auth/popup-closed-by-user': 'La fenêtre de connexion Google a été fermée.',
    'auth/popup-blocked': 'Le popup a été bloqué par votre navigateur.',
    'auth/network-request-failed': 'Erreur réseau. Vérifiez votre connexion Internet.',
    'auth/too-many-requests': 'Trop de tentatives. Veuillez patienter.',
    'auth/operation-not-allowed': "Cette méthode de connexion n'est pas activée."
  };
  return messages[code] || error?.message || "Erreur d'authentification.";
}

async function establishBackendSession(firebaseUser) {
  const idToken = await firebaseUser.getIdToken(true);
  // The token is exchanged once and is never persisted in localStorage/sessionStorage.
  return createWebSession(idToken);
}

export async function registerWithEmailPassword({ email, password, fullName }) {
  if (!auth) return configurationError();
  try {
    const credential = await createUserWithEmailAndPassword(auth, email, password);
    if (fullName) await updateProfile(credential.user, { displayName: fullName });
    const user = await establishBackendSession(credential.user);
    return { ok: true, user, firebaseUser: credential.user };
  } catch (error) {
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

export async function loginWithEmailPassword(email, password) {
  if (!auth) return configurationError();
  try {
    const credential = await signInWithEmailAndPassword(auth, email, password);
    const user = await establishBackendSession(credential.user);
    return { ok: true, user, firebaseUser: credential.user };
  } catch (error) {
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

export async function loginWithGoogle() {
  if (!auth || !googleProvider) return configurationError();
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = await establishBackendSession(result.user);
    return { ok: true, user, firebaseUser: result.user };
  } catch (error) {
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

export async function resetPassword(email) {
  if (!auth) return configurationError();
  try {
    if (!email) return { ok: false, error: "Veuillez renseigner votre adresse e-mail." };
    await sendPasswordResetEmail(auth, email);
    return { ok: true, message: 'Un e-mail de réinitialisation a été envoyé.' };
  } catch (error) {
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

export async function logoutUser() {
  let backendError = null;
  try {
    await deleteWebSession();
  } catch (error) {
    backendError = error;
  }
  if (auth) await signOut(auth);
  if (backendError) throw backendError;
}

export function subscribeToAuthState(callback, onError = (error) => console.error(error)) {
  if (!auth) {
    getCurrentUser().then(callback).catch((error) => {
      callback(null);
      if (error.status !== 401) onError(error);
    });
    return () => {};
  }
  return onAuthStateChanged(auth, async (firebaseUser) => {
    try {
      if (!firebaseUser) {
        callback(null);
        return;
      }
      try {
        callback(await getCurrentUser());
      } catch (error) {
        if (error.status !== 401) throw error;
        callback(await establishBackendSession(firebaseUser));
      }
    } catch (error) {
      callback(null);
      onError(error);
    }
  });
}
