import React, { useState } from 'react';
import { StyleSheet, Text, View, SafeAreaView, TouchableOpacity, ScrollView } from 'react-native';
import HomeScreen from './src/screens/HomeScreen';
import KYCCameraScreen from './src/screens/KYCCameraScreen';
import VideoInspectionScreen from './src/screens/VideoInspectionScreen';
import BookingsScreen from './src/screens/BookingsScreen';

export default function App() {
  const [currentTab, setCurrentTab] = useState('home'); // 'home' | 'kyc' | 'inspection' | 'bookings'
  const [activeBooking, setActiveBooking] = useState(null);

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
          />
        );
      case 'kyc':
        return (
          <KYCCameraScreen
            onVerificationComplete={() => setCurrentTab('home')}
          />
        );
      case 'inspection':
        return (
          <VideoInspectionScreen
            booking={activeBooking}
            onInspectionComplete={() => setCurrentTab('bookings')}
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
          <Text style={styles.brandTitle}>Lokiini Maroc</Text>
          <View style={styles.cndpBadge}>
            <Text style={styles.cndpText}>CNDP 09-08</Text>
          </View>
        </View>
      </View>

      {/* Main Screen Content */}
      <View style={styles.content}>
        {renderContent()}
      </View>

      {/* Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={[styles.navItem, currentTab === 'home' && styles.navItemActive]}
          onPress={() => setCurrentTab('home')}
        >
          <Text style={[styles.navText, currentTab === 'home' && styles.navTextActive]}>Catalogue</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, currentTab === 'kyc' && styles.navItemActive]}
          onPress={() => setCurrentTab('kyc')}
        >
          <Text style={[styles.navText, currentTab === 'kyc' && styles.navTextActive]}>KYC Caméra</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, currentTab === 'inspection' && styles.navItemActive]}
          onPress={() => setCurrentTab('inspection')}
        >
          <Text style={[styles.navText, currentTab === 'inspection' && styles.navTextActive]}>État des Lieux</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.navItem, currentTab === 'bookings' && styles.navItemActive]}
          onPress={() => setCurrentTab('bookings')}
        >
          <Text style={[styles.navText, currentTab === 'bookings' && styles.navTextActive]}>Mes Baux</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F7F4EE',
  },
  topBar: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  logoBadge: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: '#0F6E56',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  logoText: {
    color: '#FFFFFF',
    fontWeight: '900',
    fontSize: 18,
  },
  brandTitle: {
    fontSize: 18,
    fontWeight: '900',
    color: '#0F6E56',
  },
  cndpBadge: {
    marginLeft: 'auto',
    backgroundColor: '#E6FCF5',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#0F6E56',
  },
  cndpText: {
    color: '#0F6E56',
    fontSize: 10,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
  },
  bottomNav: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    paddingVertical: 10,
    paddingHorizontal: 8,
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 6,
    borderRadius: 8,
  },
  navItemActive: {
    backgroundColor: '#E6FCF5',
  },
  navText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748B',
  },
  navTextActive: {
    color: '#0F6E56',
    fontWeight: 'bold',
  },
});
