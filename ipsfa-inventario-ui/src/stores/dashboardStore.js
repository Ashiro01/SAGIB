import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Tu instancia de Axios

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    stats: null, // Almacenará el objeto completo de estadísticas
    loading: false,
    error: null,
  }),
  getters: {
    getStats: (state) => state.stats,
    isLoading: (state) => state.loading,
  },
  actions: {
    async fetchDashboardStats() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/dashboard/stats/');
        this.stats = response.data;
        console.log('Estadísticas del Dashboard cargadas desde API:', this.stats);
      } catch (err) {
        this.error = 'Error al cargar las estadísticas del dashboard.';
        console.error('Error en fetchDashboardStats:', err);
        // No lanzamos el error para no detener la carga de la página,
        // el componente verificará el estado de error.
      } finally {
        this.loading = false;
      }
    },
  },
}); 