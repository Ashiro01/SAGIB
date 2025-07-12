// src/stores/auditLogStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const useAuditLogStore = defineStore('auditLog', {
  state: () => ({
    logs: [],
    loading: false,
    error: null,
    // Podríamos añadir metadatos de paginación si el backend los envía
    // count: 0,
    // next: null,
    // previous: null,
  }),
  getters: {
    listaLogs: (state) => state.logs,
    isLoading: (state) => state.loading,
  },
  actions: {
    async fetchLogs(filtros = {}) {
      this.loading = true;
      this.error = null;
      try {
        // Construir los parámetros de la URL a partir del objeto de filtros
        const params = new URLSearchParams();
        if (filtros.usuario) params.append('usuario__username__icontains', filtros.usuario);
        if (filtros.accion) params.append('accion', filtros.accion);
        // Para fechas, Django Filter espera campos como 'timestamp__gte' y 'timestamp__lte'
        if (filtros.fechaDesde) params.append('timestamp__gte', filtros.fechaDesde); // Formato YYYY-MM-DD
        if (filtros.fechaHasta) params.append('timestamp__lte', filtros.fechaHasta); // Formato YYYY-MM-DD

        const response = await apiClient.get('/audit-logs/', { params });
        this.logs = response.data.results || response.data;
      } catch (err) {
        this.error = 'Error al cargar los logs de auditoría.';
        console.error('Error en fetchLogs:', err);
        throw err;
      } finally {
        this.loading = false;
      }
    },
  },
});