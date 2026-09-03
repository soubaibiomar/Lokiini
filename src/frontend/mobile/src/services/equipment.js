import { apiClient } from './apiClient';

export async function getEquipmentList(filters = {}) {
  const query = {
    search: filters.search || undefined,
    categorie: filters.category && filters.category !== 'all' ? filters.category : undefined,
    city: filters.city && filters.city !== 'Toutes les villes' ? filters.city : undefined,
    prix_min: filters.minPrice || undefined,
    prix_max: filters.maxPrice || undefined,
    page: filters.page || 1,
    page_size: filters.pageSize || 20,
  };
  return apiClient.get('/articles', query);
}

export async function getEquipmentDetail(id) {
  return apiClient.get(`/articles/${encodeURIComponent(String(id))}`);
}

export async function getEquipmentCategories() {
  return apiClient.get('/articles/categories');
}
