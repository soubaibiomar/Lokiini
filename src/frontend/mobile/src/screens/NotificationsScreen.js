import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from 'react-native';

import {
  getNotifications,
  markAllNotificationsAsRead,
  markNotificationAsRead,
} from '../services/notifications';

export default function NotificationsScreen({ onNavigateSection, onClose }) {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  const fetchNotifications = useCallback(async () => {
    setError(null);
    try {
      const data = await getNotifications();
      const list = Array.isArray(data) ? data : data?.items || [];
      setNotifications(list);
    } catch (err) {
      setError(err.message || 'Impossible de charger vos notifications.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchNotifications();
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, lu: true, est_lu: true })));
    } catch (err) {
      setError(err.message || 'Impossible de marquer les notifications.');
    }
  };

  const handleNotificationPress = async (n) => {
    if (!n.lu && !n.est_lu) {
      markNotificationAsRead(n.id).catch(() => {});
      setNotifications((prev) => prev.map((item) => (item.id === n.id ? { ...item, lu: true, est_lu: true } : item)));
    }
    const section = n.destination?.section || n.section;
    if (section && onNavigateSection) {
      onNavigateSection(section, n.destination?.resource_id || n.resource_id);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerTop}>
          <Text style={styles.headerTitle}>Centre de Notifications</Text>
          {onClose ? (
            <TouchableOpacity onPress={onClose} style={styles.closeBtn}>
              <Text style={styles.closeBtnText}>Fermer</Text>
            </TouchableOpacity>
          ) : null}
        </View>
        <Text style={styles.headerSubtitle}>Alertes de réservation, paiements, identité et messages</Text>

        {notifications.some((n) => !n.lu && !n.est_lu) ? (
          <TouchableOpacity style={styles.markAllBtn} onPress={handleMarkAllRead}>
            <Text style={styles.markAllText}>Tout marquer comme lu</Text>
          </TouchableOpacity>
        ) : null}
      </View>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0F6E56" />
          <Text style={styles.loadingText}>Chargement des notifications...</Text>
        </View>
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => String(item.id)}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#0F6E56']} />}
          contentContainerStyle={styles.listContent}
          renderItem={({ item: n }) => {
            const isRead = n.lu || n.est_lu;
            return (
              <TouchableOpacity
                style={[styles.notifCard, !isRead && styles.notifCardUnread]}
                onPress={() => handleNotificationPress(n)}
              >
                <View style={styles.notifHeader}>
                  <Text style={styles.notifType}>
                    {n.event_type || n.type || 'LOKIINI'}
                  </Text>
                  <Text style={styles.notifDate}>
                    {n.cree_le ? new Date(n.cree_le).toLocaleDateString() : ''}
                  </Text>
                </View>
                <Text style={styles.notifTitle}>{n.titre || n.title}</Text>
                <Text style={styles.notifMessage}>{n.corps || n.message}</Text>
                {!isRead ? <View style={styles.unreadDot} /> : null}
              </TouchableOpacity>
            );
          }}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>Aucune notification</Text>
              <Text style={styles.emptySubtitle}>Vous êtes à jour ! Aucune nouvelle alerte pour le moment.</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  header: { padding: 16, borderBottomWidth: 1, borderBottomColor: '#E2E8F0', backgroundColor: '#FFFFFF' },
  headerTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  headerTitle: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  closeBtn: { padding: 4 },
  closeBtnText: { color: '#0F6E56', fontWeight: 'bold' },
  headerSubtitle: { fontSize: 11, color: '#64748B', marginTop: 2 },
  markAllBtn: { marginTop: 8, alignSelf: 'flex-start' },
  markAllText: { color: '#0F6E56', fontSize: 11, fontWeight: 'bold' },
  listContent: { padding: 16 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, color: '#64748B' },
  errorText: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 8, marginHorizontal: 16, borderRadius: 8, fontSize: 11 },
  notifCard: {
    position: 'relative',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
  },
  notifCardUnread: {
    borderColor: '#0F6E56',
    backgroundColor: '#F0FDFA',
  },
  notifHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 },
  notifType: { fontSize: 10, fontWeight: 'bold', color: '#0F6E56', textTransform: 'uppercase' },
  notifDate: { fontSize: 10, color: '#94A3B8' },
  notifTitle: { fontSize: 14, fontWeight: 'bold', color: '#1E293B', marginBottom: 2 },
  notifMessage: { fontSize: 12, color: '#475569', lineHeight: 16 },
  unreadDot: { position: 'absolute', top: 12, right: 12, width: 8, height: 8, borderRadius: 4, backgroundColor: '#D85A30' },
  emptyContainer: { padding: 40, alignItems: 'center' },
  emptyTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  emptySubtitle: { fontSize: 12, color: '#64748B', textAlign: 'center' },
});
