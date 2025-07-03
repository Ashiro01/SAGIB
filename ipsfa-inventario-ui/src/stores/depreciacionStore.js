// src/stores/depreciacionStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api';

export const useDepreciacionStore = defineStore('depreciacion', {
  state: () => ({
    loading: false,
    error: null,
    ultimoResultado: null, // Para almacenar el resumen del último cálculo
  }),
  getters: {
    isLoading: (state) => state.loading,
    getUltimoResultado: (state) => state.ultimoResultado,
  },
  actions: {
    async ejecutarCalculoDepreciacion(periodo) { // periodo será un objeto { mes, anio }
      this.loading = true;
      this.error = null;
      this.ultimoResultado = null;

      try {
        // Hacemos la petición POST al endpoint del backend
        const response = await apiClient.post('/depreciacion/calcular/', periodo);
        this.ultimoResultado = response.data;
        console.log('Respuesta del cálculo de depreciación:', response.data);
        return response.data; // Devolvemos el resultado al componente
      } catch (err) {
        const errorMessage = err.response?.data?.error || 'Ocurrió un error inesperado durante el cálculo.';
        this.error = errorMessage;
        console.error('Error en ejecutarCalculoDepreciacion:', err);
        throw new Error(errorMessage);
      } finally {
        this.loading = false;
      }
    }
  }
});