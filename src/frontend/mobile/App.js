import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Modal,
  SafeAreaView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import AuthScreen from './src/screens/AuthScreen';
import BookingsScreen from './src/screens/BookingsScreen';
import HomeScreen from './src/screens/HomeScreen';
import KYCCameraScreen from './src/screens/KYCCameraScreen';
import MessagesScreen from './src/screens/MessagesScreen';
import NotificationsScreen from './src/screens/NotificationsScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import VideoInspectionScreen from './src/screens/VideoInspectionScreen';
import { getBackendProfile, observeIdentity } from './src/services/auth';
import { getNotifications } from './src/services/notifications';

export default function App() {
  const [currentTab, setCurrentTab] = useState('home'); // 'home' | 'bookings' | 'inspection' | 'messages' | 'profile' | 'kyc'
  const [activeBooking, setActiveBooking] = useState(null);
  const [activeConversation, setActiveConversation] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [showNotificationsModal, setShowNotificationsModal] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    const unsubscribe = observeIdentity(async (firebaseUser) => {
      if (!firebaseUser) {
        setCurrentUser(null);
        setAuthLoading(false);
        return;
      }
      try {
        const profile = await getBackendProfile(firebaseUser);
        setCurrentUser(profile);
      } catch {
        setCurrentUser(null);
      } finally {
        setAuthLoading(false);
      }
    });
    return () => unsubscribe();
  }, []);

  // Poll notifications unread count
  useEffect(() => {
    if (!currentUser) return;
    const checkNotifications = async () => {
      try {
        const data = await getNotifications();
        const list = Array.isArray(data) ? data : data?.items || [];
        const unread = list.filter((n) => !n.lu && !n.est_lu).length;
        setUnreadCount(unread);
      } catch {
        // Quiet fallback
      }
    };
    checkNotifications();
    const interval = setInterval(checkNotifications, 15000);
    return () => clearInterval(interval);
  }, [currentUser]);

  if (authLoading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#0F6E56" />
        <Text style={styles.loadingText}>Initialisation de Lokiini...</Text>
      </View>
    );
  }

  if (!currentUser) {
    return <AuthScreen onAuthenticated={setCurrentUser} />;
  }

  const handleNavigateSection = (section, resourceId) => {
    setShowNotificationsModal(false);
    if (section === 'bookings' || section === 'reservations') {
      setCurrentTab('bookings');
    } else if (section === 'messages' || section === 'conversations') {
      if (resourceId) {
        setActiveConversation({ id: resourceId });
      }
      setCurrentTab('messages');
    } else if (section === 'verification' || section === 'kyc') {
      setCurrentTab('kyc');
    } else {
      setCurrentTab('home');
    }
  };

  const renderContent = () => {
    switch (currentTab) {
      case 'home':
        return (
          <HomeScreen
            onSelectBooking={(booking) => {
              setActiveBooking(booking);
              setCurrentTab('inspection');
            }}
            onStartKYC={() => setCurrentTab('kyc')}
            onOpenConversation={({ recipientId, equipmentId }) => {
              setActiveConversation({ recipientId, equipmentId });
              setCurrentTab('messages');
            }}
          />
        );
      case 'bookings':
        return (
          <BookingsScreen
            onOpenInspection={(booking) => {
              setActiveBooking(booking);
              setCurrentTab('inspection');
            }}
          />
        );
      case 'inspection':
        return (
          <VideoInspectionScreen
            booking={activeBooking}
            onInspectionComplete={() => setCurrentTab('bookings')}
          />
        );
      case 'messages':
        return (
          <MessagesScreen
            initialConversation={activeConversation}
            currentUserId={currentUser.id}
          />
        );
      case 'kyc':
        return (
          <KYCCameraScreen
            currentStatus={currentUser.statut_verification}
            currentUserId={currentUser.id}
            onVerificationComplete={async () => {
              try {
                const refreshed = await getBackendProfile();
                setCurrentUser(refreshed);
              } finally {
                setCurrentTab('profile');
              }
            }}
          />
        );
      case 'profile':
        return (
          <ProfileScreen
            user={currentUser}
            onStartKYC={() => setCurrentTab('kyc')}
            onLogout={() => setCurrentUser(null)}
          />
        );
      default:
        return <HomeScreen onStartKYC={() => setCurrentTab('kyc')} />;
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* App Top Bar */}
      <View style={styles.topBar}>
        <View style={styles.brandRow}>
          <View style={styles.logoBadge}>
            <Text style={styles.logoText}>L</Text>
          </View>
          <View>
            <Text style={styles.brandTitle}>Lokiini Maroc</Text>
            <Text style={styles.brandSub}>Location de Matériel Sécurisée</Text>
          </View>
          <View style={styles.topRightActions}>
            <TouchableOpacity
              style={styles.notifBtn}
              onPress={() => setShowNotificationsModal(true)}
            >
              <Text style={styles.notifIcon}>🔔</Text>
              {unreadCount > 0 ? (
                <View style={styles.notifBadge}>
                  <Text style={styles.notifBadgeText}>{unreadCount > 9 ? '9+' : unreadCount}</Text>
                </View>
              ) : null}
            </TouchableOpacity>
          </View>
        </View>
      </View>

      {/* Main Screen Content */}
      <View style={styles.content}>{renderContent()}</View>

      {/* Notifications Modal */}
      <Modal visible={showNotificationsModal} animationType="slide">
        <SafeAreaView style={styles.container}>
          <NotificationsScreen
            onNavigateSection={handleNavigateSection}
            onClose={() => setShowNotificationsModal(false)}
          />
        </SafeAreaView>
      </Modal>

      {/* Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={[styles.navItem, currentTab === 'home' && styles.navItemActive]}
          onPress={() => setCurrentTab('home')}
        >
          <Text style={styles.navIcon}>🔍</Text>
          <Text style={[styles.navText, currentTab === 'home' && styles.navTextActive]}>Catalogue</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, currentTab === 'bookings' && styles.navItemActive]}
          onPress={() => setCurrentTab('bookings')}
        >
          <Text style={styles.navIcon}>📋</Text>
          <Text style={[styles.navText, currentTab === 'bookings' && styles.navTextActive]}>Mes Baux</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, currentTab === 'inspection' && styles.navItemActive]}
          onPress={() => setCurrentTab('inspection')}
        >
          <Text style={styles.navIcon}>📷</Text>
          <Text style={[styles.navText, currentTab === 'inspection' && styles.navTextActive]}>État Lieux</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, currentTab === 'messages' && styles.navItemActive]}
          onPress={() => {
            setActiveConversation(null);
            setCurrentTab('messages');
          }}
        >
          <Text style={styles.navIcon}>💬</Text>
          <Text style={[styles.navText, currentTab === 'messages' && styles.navTextActive]}>Messages</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, (currentTab === 'profile' || currentTab === 'kyc') && styles.navItemActive]}
          onPress={() => setCurrentTab('profile')}
        >
          <Text style={styles.navIcon}>👤</Text>
          <Text style={[styles.navText, (currentTab === 'profile' || currentTab === 'kyc') && styles.navTextActive]}>Profil</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  loading: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: '#F7F4EE' },
  loadingText: { marginTop: 10, color: '#64748B', fontWeight: '600' },
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  topBar: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  brandRow: { flexDirection: 'row', alignItems: 'center' },
  logoBadge: {
    width: 34,
    height: 34,
    borderRadius: 8,
    backgroundColor: '#0F6E56',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 10,
  },
  logoText: { color: '#FFFFFF', fontWeight: '900', fontSize: 18 },
  brandTitle: { fontSize: 16, fontWeight: '900', color: '#0F6E56' },
  brandSub: { fontSize: 9, color: '#64748B', fontWeight: '600' },
  topRightActions: { marginLeft: 'auto', flexDirection: 'row', alignItems: 'center' },
  notifBtn: { position: 'relative', padding: 6 },
  notifIcon: { fontSize: 18 },
  notifBadge: {
    position: 'absolute',
    top: 2,
    right: 2,
    backgroundColor: '#D85A30',
    borderRadius: 8,
    paddingHorizontal: 4,
    paddingVertical: 1,
    minWidth: 16,
    alignItems: 'center',
  },
  notifBadgeText: { color: '#FFFFFF', fontSize: 9, fontWeight: 'bold' },
  content: { flex: 1 },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingVertical: 8,
    paddingHorizontal: 6,
  },
  navItem: { flex: 1, alignItems: 'center', paddingVertical: 4, borderRadius: 8 },
  navItemActive: { backgroundColor: '#E6FCF5' },
  navIcon: { fontSize: 15, marginBottom: 2 },
  navText: { fontSize: 10, fontWeight: '600', color: '#64748B' },
  navTextActive: { color: '#0F6E56', fontWeight: 'bold' },
});
