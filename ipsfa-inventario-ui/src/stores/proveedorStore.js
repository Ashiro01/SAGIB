import { defineStore } from 'pinia';
import apiClient from '@/services/api';

const API_ENTITY_URL = '/proveedores/';

export const useProveedorStore = defineStore('proveedor', {
  state: () => ({
    proveedores: [],
    proveedorActual: null,
    loading: false,
    error: null,
  }),

  getters: {
    listaProveedores: (state) => state.proveedores,
    getProveedorActual: (state) => state.proveedorActual,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
  },

  actions: {
    formatApiErrors(errors) {
      let formattedError = 'Error al procesar la solicitud: ';
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

    async fetchProveedores() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(API_ENTITY_URL);
        this.proveedores = response.data.results || response.data;
        console.log('Proveedores cargados desde API:', this.proveedores);
      } catch (err) {
        this.error = 'Error al cargar los proveedores.';
        console.error('Error en fetchProveedores:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchProveedorById(id) {
      this.loading = true;
      this.error = null;
      this.proveedorActual = null;
      try {
        const response = await apiClient.get(`${API_ENTITY_URL}${id}/`);
        this.proveedorActual = response.data;
        return this.proveedorActual;
      } catch (err) {
        this.error = `Error al cargar el proveedor con ID ${id}.`;
        console.error('Error en fetchProveedorById:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async crearProveedor(datosDelProveedor) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post(API_ENTITY_URL, datosDelProveedor);
        await this.fetchProveedores();
        return response.data;
      } catch (err) {
        this.error = 'Error al crear el proveedor.';
        if (err.response && err.response.data) this.error = this.formatApiErrors(err.response.data);
        else this.error = err.message;
        console.error('Error en crearProveedor:', this.error);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async actualizarProveedor(id, datosDelProveedor) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`${API_ENTITY_URL}${id}/`, datosDelProveedor);
        await this.fetchProveedores();
        if (this.proveedorActual && this.proveedorActual.id === id) {
          this.proveedorActual = response.data;
        }
        return response.data;
      } catch (err) {
        this.error = 'Error al actualizar el proveedor.';
        if (err.response && err.response.data) this.error = this.formatApiErrors(err.response.data);
        else this.error = err.message;
        console.error('Error en actualizarProveedor:', this.error);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async eliminarProveedor(idProveedor) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`${API_ENTITY_URL}${idProveedor}/`);
        await this.fetchProveedores();
        if (this.proveedorActual && this.proveedorActual.id === idProveedor) {
          this.proveedorActual = null;
        }
        return { success: true, message: 'Proveedor eliminado.' };
      } catch (err) {
        this.error = `Error al eliminar el proveedor con ID ${idProveedor}.`;
        if (err.response && err.response.data) this.error = this.formatApiErrors(err.response.data);
        else this.error = err.message;
        console.error('Error en eliminarProveedor:', this.error);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
  },
});
