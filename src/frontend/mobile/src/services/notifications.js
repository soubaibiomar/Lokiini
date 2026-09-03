import { apiClient } from './apiClient';

export async function getNotifications() {
  return apiClient.get('/notifications');
}

export async function markAllNotificationsAsRead() {
  return apiClient.patch('/notifications/tout-lire');
}

export async function markNotificationAsRead(notificationId) {
  return apiClient.patch(`/notifications/${encodeURIComponent(String(notificationId))}`);
}
