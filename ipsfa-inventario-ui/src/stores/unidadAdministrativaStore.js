// src/stores/unidadAdministrativaStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Asegúrate que esta ruta a tu apiClient sea correcta

const API_ENTITY_URL = '/unidades-administrativas/'; // Relativo a la baseURL de apiClient

export const useUnidadAdministrativaStore = defineStore('unidadAdministrativa', {
  state: () => ({
    unidades: [],
    unidadActual: null, // Para el formulario de edición o vista de detalle
    loading: false,
    error: null,
  }),
  getters: {
    getUnidadById: (state) => (id) => state.unidades.find(u => u.id === id),
    todasLasUnidades: (state) => state.unidades,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
  },
  actions: {
    formatApiErrors(errors) {
      let formattedError = "Error al procesar la solicitud: ";
      if (typeof errors === 'object' && errors !== null) {
        const errorMessages = [];
        for (const field in errors) {
          errorMessages.push(`${field}: ${errors[field].join ? errors[field].join(', ') : errors[field]}`);
        }
        formattedError += errorMessages.join('; ');
      } else if (typeof errors === 'string') {
        formattedError = errors;
      }
      return formattedError;
    },

    async fetchUnidades() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(API_ENTITY_URL);
        this.unidades = response.data.results || response.data;
        console.log('Unidades Administrativas cargadas desde API:', this.unidades);
      } catch (err) {
        this.error = 'Error al cargar las Unidades Administrativas.';
        console.error('Error en fetchUnidades:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchUnidadById(id) {
      this.loading = true;
      this.error = null;
      this.unidadActual = null;
      try {
        const response = await apiClient.get(`${API_ENTITY_URL}${id}/`);
        this.unidadActual = response.data;
        console.log('Unidad Administrativa individual cargada:', this.unidadActual);
        return this.unidadActual;
      } catch (err) {
        this.error = `Error al cargar la Unidad Administrativa con ID ${id}.`;
        console.error('Error en fetchUnidadById:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async agregarUnidad(datosDeLaUnidad) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post(API_ENTITY_URL, datosDeLaUnidad);
        await this.fetchUnidades();
        console.log('Unidad Administrativa creada vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al crear la Unidad Administrativa.';
        if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data);
        }
        console.error('Error en agregarUnidad:', this.error, err.response ? err.response.data : err.message);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async actualizarUnidad(id, datosDeLaUnidad) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`${API_ENTITY_URL}${id}/`, datosDeLaUnidad);
        await this.fetchUnidades();
        if (this.unidadActual && this.unidadActual.id === id) {
             await this.fetchUnidadById(id);
        }
        console.log('Unidad Administrativa actualizada vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al actualizar la Unidad Administrativa.';
        if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data);
        }
        console.error('Error en actualizarUnidad:', this.error, err.response ? err.response.data : err.message);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async eliminarUnidad(idUnidad) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`${API_ENTITY_URL}${idUnidad}/`);
        await this.fetchUnidades();
        console.log(`Unidad Administrativa con ID ${idUnidad} eliminada vía API.`);
        return { success: true, message: 'Unidad Administrativa eliminada.' };
      } catch (err) {
        this.error = `Error al eliminar la Unidad Administrativa con ID ${idUnidad}.`;
         if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data);
        }
        console.error('Error en eliminarUnidad:', this.error, err.response ? err.response.data : err.message);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
  },
});