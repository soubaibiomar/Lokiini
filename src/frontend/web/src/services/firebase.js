import { initializeApp, getApps, getApp } from 'firebase/app';
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  signOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  updateProfile
} from 'firebase/auth';

// Configuration Firebase chargée depuis les variables d'environnement Vite
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyDemoLokiiniKeyForDevelopment123",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "lokiini-dev.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "lokiini-dev",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "lokiini-dev.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "1234567890",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:1234567890:web:abcdef123456"
};

// Vérifie si la configuration Firebase réelle a été renseignée
export const isFirebaseConfigured = () => {
  const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
  return Boolean(apiKey && !apiKey.includes('AIzaSyDemoLokiiniKey'));
};

// Initialisation de Firebase App (singleton)
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApp();
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

/**
 * Traduction conviviale des erreurs Firebase en français
 */
export function formatFirebaseError(error) {
  if (!error) return "Une erreur inattendue s'est produite.";
  const code = error.code || '';

  switch (code) {
    case 'auth/invalid-email':
      return "L'adresse e-mail n'est pas valide.";
    case 'auth/user-disabled':
      return "Ce compte utilisateur a été désactivé.";
    case 'auth/user-not-found':
      return "Aucun compte trouvé avec cette adresse e-mail.";
    case 'auth/wrong-password':
    case 'auth/invalid-credential':
      return "Identifiant ou mot de passe incorrect.";
    case 'auth/email-already-in-use':
      return "Un compte existe déjà avec cette adresse e-mail.";
    case 'auth/weak-password':
      return "Le mot de passe doit contenir au moins 6 caractères.";
    case 'auth/popup-closed-by-user':
      return "La fenêtre de connexion Google a été fermée avant la validation.";
    case 'auth/popup-blocked':
      return "Le popup a été bloqué par votre navigateur. Veuillez autoriser les popups pour Lokiini.";
    case 'auth/network-request-failed':
      return "Erreur réseau. Vérifiez votre connexion Internet.";
    case 'auth/too-many-requests':
      return "Trop de tentatives infructueuses. Veuillez patienter un instant avant de réessayer.";
    case 'auth/operation-not-allowed':
      return "Cette méthode de connexion n'est pas activée dans la console Firebase.";
    default:
      return error.message || "Erreur d'authentification.";
  }
}

/**
 * Inscription avec Email et Mot de passe
 */
export async function registerWithEmailPassword({
  email,
  password,
  fullName,
  phoneNumber,
  city = 'Casablanca',
  role = 'renter',
  companyName = null,
  companyIce = null
}) {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Met à jour le profil de l'utilisateur Firebase
    if (fullName) {
      await updateProfile(user, { displayName: fullName });
    }

    const userData = {
      id: user.uid,
      uid: user.uid,
      full_name: fullName || user.displayName || email.split('@')[0],
      email: user.email,
      phone_number: phoneNumber || '+212600000000',
      city: city,
      user_role: role,
      company_name: role === 'pro_owner' ? companyName : null,
      company_ice: role === 'pro_owner' ? companyIce : null,
      is_kyc_verified: false,
      auth_provider: 'firebase_email'
    };

    localStorage.setItem('lokiini_user', JSON.stringify(userData));
    localStorage.setItem('lokiini_token', await user.getIdToken());

    return { ok: true, user: userData, firebaseUser: user };
  } catch (error) {
    // Si Firebase n'est pas configuré avec des clés réelles, fallback pour le dev
    if (!isFirebaseConfigured()) {
      console.warn("Firebase non configuré avec clés réelles. Mode simulation locale activé.", error);
      const mockUser = {
        id: `fb_sim_${Date.now()}`,
        uid: `fb_sim_${Date.now()}`,
        full_name: fullName || 'Utilisateur Lokiini',
        email: email,
        phone_number: phoneNumber || '+212661000001',
        city: city,
        user_role: role,
        company_name: companyName,
        company_ice: companyIce,
        is_kyc_verified: false,
        auth_provider: 'mock_simulation'
      };
      localStorage.setItem('lokiini_user', JSON.stringify(mockUser));
      return { ok: true, user: mockUser, isMock: true };
    }
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

/**
 * Connexion avec Email et Mot de passe
 */
export async function loginWithEmailPassword(email, password) {
  try {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    const user = userCredential.user;

    // Récupérer ou reconstituer les données utilisateur
    const savedUser = localStorage.getItem('lokiini_user');
    let userData = savedUser ? JSON.parse(savedUser) : null;

    if (!userData || userData.email !== email) {
      userData = {
        id: user.uid,
        uid: user.uid,
        full_name: user.displayName || email.split('@')[0],
        email: user.email,
        phone_number: '+212661000001',
        user_role: email.toLowerCase().includes('atlas') || email.toLowerCase().includes('pro') ? 'pro_owner' : 'renter',
        city: 'Casablanca',
        is_kyc_verified: true,
        auth_provider: 'firebase_email'
      };
    }

    localStorage.setItem('lokiini_user', JSON.stringify(userData));
    localStorage.setItem('lokiini_token', await user.getIdToken());

    return { ok: true, user: userData, firebaseUser: user };
  } catch (error) {
    if (!isFirebaseConfigured()) {
      console.warn("Firebase non configuré avec clés réelles. Mode simulation locale activé.", error);
      const mockUser = {
        id: 'a1111111-1111-1111-1111-111111111111',
        full_name: email.toLowerCase().includes('atlas') ? 'Atlas Location BTP Maroc' : 'Karim Tazi',
        email: email,
        phone_number: '+212661000001',
        user_role: email.toLowerCase().includes('atlas') ? 'pro_owner' : 'renter',
        company_name: email.toLowerCase().includes('atlas') ? 'Atlas Location BTP SARL' : null,
        company_ice: email.toLowerCase().includes('atlas') ? '002345678000045' : null,
        city: 'Casablanca',
        is_kyc_verified: true,
        auth_provider: 'mock_simulation'
      };
      localStorage.setItem('lokiini_user', JSON.stringify(mockUser));
      return { ok: true, user: mockUser, isMock: true };
    }
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

/**
 * Connexion / Inscription via Google OAuth (1-clic)
 */
export async function loginWithGoogle(preferredRole = 'renter') {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const user = result.user;

    const userData = {
      id: user.uid,
      uid: user.uid,
      full_name: user.displayName || user.email.split('@')[0],
      email: user.email,
      avatar_url: user.photoURL,
      phone_number: user.phoneNumber || '+212661000000',
      city: 'Casablanca',
      user_role: preferredRole,
      is_kyc_verified: true,
      auth_provider: 'firebase_google'
    };

    localStorage.setItem('lokiini_user', JSON.stringify(userData));
    localStorage.setItem('lokiini_token', await user.getIdToken());

    return { ok: true, user: userData, firebaseUser: user };
  } catch (error) {
    if (!isFirebaseConfigured()) {
      console.warn("Firebase non configuré avec clés réelles. Mode simulation Google activé.", error);
      const mockGoogleUser = {
        id: `google_user_${Date.now()}`,
        uid: `google_user_${Date.now()}`,
        full_name: 'Utilisateur Google Maroc',
        email: 'user.google@gmail.com',
        avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
        phone_number: '+212661000000',
        city: 'Casablanca',
        user_role: preferredRole,
        is_kyc_verified: true,
        auth_provider: 'mock_google'
      };
      localStorage.setItem('lokiini_user', JSON.stringify(mockGoogleUser));
      return { ok: true, user: mockGoogleUser, isMock: true };
    }
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

/**
 * Réinitialisation du mot de passe par Email
 */
export async function resetPassword(email) {
  try {
    if (!email) {
      return { ok: false, error: "Veuillez renseigner votre adresse e-mail." };
    }
    await sendPasswordResetEmail(auth, email);
    return { ok: true, message: "Un e-mail de réinitialisation a été envoyé." };
  } catch (error) {
    if (!isFirebaseConfigured()) {
      return { ok: true, message: "Un e-mail de réinitialisation fictif a été simulé avec succès." };
    }
    return { ok: false, error: formatFirebaseError(error), rawError: error };
  }
}

/**
 * Déconnexion Firebase
 */
export async function logoutUser() {
  try {
    await signOut(auth);
  } catch (err) {
    console.warn("Erreur lors de signOut Firebase:", err);
  } finally {
    localStorage.removeItem('lokiini_token');
    localStorage.removeItem('lokiini_user');
  }
}

/**
 * Écouteur d'état d'authentification persistant
 */
export function subscribeToAuthState(callback) {
  return onAuthStateChanged(auth, async (firebaseUser) => {
    if (firebaseUser) {
      const savedUser = localStorage.getItem('lokiini_user');
      let userData = savedUser ? JSON.parse(savedUser) : null;
      if (!userData) {
        userData = {
          id: firebaseUser.uid,
          uid: firebaseUser.uid,
          full_name: firebaseUser.displayName || firebaseUser.email.split('@')[0],
          email: firebaseUser.email,
          avatar_url: firebaseUser.photoURL,
          user_role: 'renter',
          city: 'Casablanca',
          is_kyc_verified: true
        };
      }
      callback(userData);
    } else {
      const savedUser = localStorage.getItem('lokiini_user');
      if (savedUser) {
        callback(JSON.parse(savedUser));
      } else {
        callback(null);
      }
    }
  });
}
