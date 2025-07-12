import { defineStore } from 'pinia';
import apiClient from '@/services/api';

const API_URL = '/categorias/';

export const useCategoriaStore = defineStore('categoria', {
  state: () => ({
    categorias: [],
    loading: false,
    error: null,
  }),
  getters: {
    listaCategorias: (state) => state.categorias,
    isLoading: (state) => state.loading,
  },
  actions: {
    async fetchCategorias() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(API_URL);
        this.categorias = response.data.results || response.data;
      } catch (err) {
        this.error = 'Error al cargar las categorías.';
        console.error(this.error, err);
        throw err;
      } finally {
        this.loading = false;
      }
    },
  },
});
