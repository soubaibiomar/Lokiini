import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  RefreshControl,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

import {
  getConversationMessages,
  getConversations,
  markConversationAsRead,
  sendMessage,
} from '../services/messaging';

export default function MessagesScreen({ initialConversation, currentUserId }) {
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(initialConversation || null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  const fetchConversations = useCallback(async () => {
    setError(null);
    try {
      const data = await getConversations();
      const list = Array.isArray(data) ? data : data?.items || [];
      setConversations(list);
    } catch (err) {
      setError(err.message || 'Impossible de charger vos conversations.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  const fetchMessages = useCallback(async (convId) => {
    if (!convId) return;
    try {
      const data = await getConversationMessages(convId);
      const list = Array.isArray(data) ? data : data?.messages || [];
      setMessages(list);
      await markConversationAsRead(convId).catch(() => {});
    } catch (err) {
      setError(err.message || 'Erreur lors du chargement des messages.');
    }
  }, []);

  useEffect(() => {
    fetchConversations();
  }, [fetchConversations]);

  useEffect(() => {
    if (activeConversation?.id) {
      fetchMessages(activeConversation.id);
      // Optional polling every 5 seconds for active conversation
      const interval = setInterval(() => fetchMessages(activeConversation.id), 5000);
      return () => clearInterval(interval);
    }
  }, [activeConversation, fetchMessages]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchConversations();
  };

  const handleSend = async () => {
    if (!inputText.trim() || sending) return;
    const content = inputText.trim();
    setInputText('');
    setSending(true);

    try {
      const payload = {
        content,
      };
      if (activeConversation?.id) {
        payload.conversationId = activeConversation.id;
      }
      if (activeConversation?.recipientId) {
        payload.recipientId = activeConversation.recipientId;
      }
      if (activeConversation?.equipmentId) {
        payload.equipmentId = activeConversation.equipmentId;
      }
      if (activeConversation?.bookingId) {
        payload.bookingId = activeConversation.bookingId;
      }

      await sendMessage(payload);
      if (activeConversation?.id) {
        await fetchMessages(activeConversation.id);
      } else {
        await fetchConversations();
      }
    } catch (err) {
      setError(err.message || 'Échec de l’envoi du message.');
    } finally {
      setSending(false);
    }
  };

  if (activeConversation) {
    return (
      <KeyboardAvoidingView
        style={styles.container}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        <View style={styles.chatHeader}>
          <TouchableOpacity onPress={() => setActiveConversation(null)} style={styles.backBtn}>
            <Text style={styles.backBtnText}>‹ Retour</Text>
          </TouchableOpacity>
          <View style={styles.chatHeaderCenter}>
            <Text style={styles.chatHeaderTitle}>
              {activeConversation.titre || activeConversation.nom_interlocuteur || 'Discussion Lokiini'}
            </Text>
            {activeConversation.article_titre ? (
              <Text style={styles.chatHeaderSub}>{activeConversation.article_titre}</Text>
            ) : null}
          </View>
        </View>

        {error ? <Text style={styles.errorText}>{error}</Text> : null}

        <FlatList
          data={messages}
          keyExtractor={(item) => String(item.id || item.cree_le)}
          renderItem={({ item: m }) => {
            const isMe = m.expediteur_id === currentUserId;
            return (
              <View style={[styles.bubbleWrapper, isMe ? styles.bubbleRight : styles.bubbleLeft]}>
                <View style={[styles.bubble, isMe ? styles.bubbleMe : styles.bubbleThem]}>
                  <Text style={[styles.bubbleText, isMe ? styles.bubbleTextMe : styles.bubbleTextThem]}>
                    {m.contenu || m.content}
                  </Text>
                  <Text style={[styles.bubbleTime, isMe ? styles.bubbleTimeMe : styles.bubbleTimeThem]}>
                    {m.cree_le ? new Date(m.cree_le).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                  </Text>
                </View>
              </View>
            );
          }}
          contentContainerStyle={styles.messagesList}
          ListEmptyComponent={
            <View style={styles.emptyMessages}>
              <Text style={styles.emptyText}>Aucun message échangé pour l’instant.</Text>
            </View>
          }
        />

        <View style={styles.inputRow}>
          <TextInput
            style={styles.chatInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Écrire un message..."
            multiline
          />
          <TouchableOpacity
            style={[styles.sendBtn, (!inputText.trim() || sending) && styles.sendBtnDisabled]}
            onPress={handleSend}
            disabled={!inputText.trim() || sending}
          >
            {sending ? <ActivityIndicator size="small" color="#FFFFFF" /> : <Text style={styles.sendBtnText}>Envoyer</Text>}
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Messagerie Inter-utilisateurs</Text>
        <Text style={styles.headerSubtitle}>Échangez en direct avec vos loueurs et locataires</Text>
      </View>

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#0F6E56" />
          <Text style={styles.loadingText}>Chargement des conversations...</Text>
        </View>
      ) : (
        <FlatList
          data={conversations}
          keyExtractor={(item) => String(item.id)}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#0F6E56']} />}
          contentContainerStyle={styles.listContent}
          renderItem={({ item: c }) => (
            <TouchableOpacity style={styles.convCard} onPress={() => setActiveConversation(c)}>
              <View style={styles.convAvatar}>
                <Text style={styles.convAvatarText}>
                  {(c.nom_interlocuteur || c.titre || 'U')[0].toUpperCase()}
                </Text>
              </View>
              <View style={styles.convInfo}>
                <View style={styles.convTopRow}>
                  <Text style={styles.convName}>{c.nom_interlocuteur || c.titre || 'Utilisateur Lokiini'}</Text>
                  {c.non_lus > 0 ? (
                    <View style={styles.unreadBadge}>
                      <Text style={styles.unreadBadgeText}>{c.non_lus}</Text>
                    </View>
                  ) : null}
                </View>
                {c.article_titre ? <Text style={styles.convArticle}>Matériel : {c.article_titre}</Text> : null}
                <Text style={styles.convLastMsg} numberOfLines={1}>
                  {c.dernier_message || 'Démarrer la discussion...'}
                </Text>
              </View>
            </TouchableOpacity>
          )}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyTitle}>Aucune discussion</Text>
              <Text style={styles.emptySubtitle}>Vous n'avez pas encore envoyé ou reçu de messages.</Text>
            </View>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F7F4EE' },
  header: { paddingHorizontal: 16, paddingTop: 16, paddingBottom: 8 },
  headerTitle: { fontSize: 18, fontWeight: '900', color: '#1E293B' },
  headerSubtitle: { fontSize: 11, color: '#64748B', marginTop: 2 },
  listContent: { padding: 16 },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { marginTop: 10, color: '#64748B' },
  errorText: { color: '#B91C1C', backgroundColor: '#FEF2F2', padding: 8, marginHorizontal: 16, borderRadius: 8, fontSize: 11 },
  convCard: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E2E8F0',
    alignItems: 'center',
  },
  convAvatar: {
    width: 42,
    height: 42,
    borderRadius: 21,
    backgroundColor: '#E6FCF5',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  convAvatarText: { color: '#0F6E56', fontWeight: 'bold', fontSize: 16 },
  convInfo: { flex: 1 },
  convTopRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  convName: { fontSize: 14, fontWeight: 'bold', color: '#1E293B' },
  unreadBadge: { backgroundColor: '#D85A30', paddingHorizontal: 6, paddingVertical: 2, borderRadius: 10 },
  unreadBadgeText: { color: '#FFFFFF', fontSize: 10, fontWeight: 'bold' },
  convArticle: { fontSize: 11, color: '#0F6E56', fontWeight: '600', marginTop: 1 },
  convLastMsg: { fontSize: 12, color: '#64748B', marginTop: 3 },
  emptyContainer: { padding: 40, alignItems: 'center' },
  emptyTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E293B', marginBottom: 4 },
  emptySubtitle: { fontSize: 12, color: '#64748B', textAlign: 'center' },
  chatHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E2E8F0',
  },
  backBtn: { paddingRight: 10 },
  backBtnText: { color: '#0F6E56', fontSize: 15, fontWeight: 'bold' },
  chatHeaderCenter: { flex: 1 },
  chatHeaderTitle: { fontSize: 14, fontWeight: 'bold', color: '#1E293B' },
  chatHeaderSub: { fontSize: 10, color: '#0F6E56' },
  messagesList: { padding: 16 },
  bubbleWrapper: { marginBottom: 10, maxWidth: '80%' },
  bubbleRight: { alignSelf: 'flex-end' },
  bubbleLeft: { alignSelf: 'flex-start' },
  bubble: { borderRadius: 14, padding: 10 },
  bubbleMe: { backgroundColor: '#0F6E56' },
  bubbleThem: { backgroundColor: '#FFFFFF', borderWidth: 1, borderColor: '#E2E8F0' },
  bubbleText: { fontSize: 13, lineHeight: 18 },
  bubbleTextMe: { color: '#FFFFFF' },
  bubbleTextThem: { color: '#1E293B' },
  bubbleTime: { fontSize: 9, marginTop: 4, alignSelf: 'flex-end' },
  bubbleTimeMe: { color: '#CCFBF1' },
  bubbleTimeThem: { color: '#94A3B8' },
  emptyMessages: { padding: 40, alignItems: 'center' },
  emptyText: { color: '#94A3B8', fontSize: 12 },
  inputRow: {
    flexDirection: 'row',
    padding: 10,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E2E8F0',
    alignItems: 'center',
  },
  chatInput: {
    flex: 1,
    backgroundColor: '#F8FAFC',
    borderWidth: 1,
    borderColor: '#CBD5E1',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
    fontSize: 13,
    maxHeight: 80,
  },
  sendBtn: {
    backgroundColor: '#0F6E56',
    borderRadius: 20,
    paddingVertical: 9,
    paddingHorizontal: 14,
    marginLeft: 8,
  },
  sendBtnDisabled: { opacity: 0.5 },
  sendBtnText: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 12 },
});
