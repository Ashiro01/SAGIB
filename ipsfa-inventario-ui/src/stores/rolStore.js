// src/stores/rolStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Tu instancia de Axios

const API_ROLES_URL = '/groups/'; // Endpoint para los Grupos de Django

export const useRolStore = defineStore('rol', {
  state: () => ({
    roles: [], // Aquí almacenaremos la lista de roles del backend
    rolActual: null, // Para un rol individual si fuera necesario
    loading: false,
    error: null,
  }),
  getters: {
    listaRoles: (state) => state.roles,
    getRolActual: (state) => state.rolActual,
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

    async fetchRoles() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(API_ROLES_URL);
        this.roles = response.data.results || response.data; // Manejar paginación si existe
        console.log('Roles (Grupos) cargados desde API:', this.roles);
      } catch (err) {
        this.error = 'Error al cargar los roles.';
        console.error('Error en fetchRoles:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // Nota: DRF para GroupSerializer por defecto no tiene un 'detail view' individual
    // a menos que lo configures explícitamente o uses el ID en la URL de lista.
    // Por ahora, no implementaremos fetchRolById a menos que sea necesario.

    async crearRol(datosDelRol) { // datosDelRol debería ser { name: 'Nombre del Rol' }
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post(API_ROLES_URL, datosDelRol);
        await this.fetchRoles(); // Refrescar la lista
        console.log('Rol (Grupo) creado vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al crear el rol.';
        if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data);
        }
        console.error('Error en crearRol:', err.response ? err.response.data : err.message, this.error);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async actualizarRol(id, datosDelRol) { // datosDelRol debería ser { name: 'Nuevo Nombre' }
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`${API_ROLES_URL}${id}/`, datosDelRol);
        await this.fetchRoles(); // Refrescar la lista
        console.log('Rol (Grupo) actualizado vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al actualizar el rol.';
        if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data);
        }
         console.error('Error en actualizarRol:', err.response ? err.response.data : err.message, this.error);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async eliminarRol(idRol) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`${API_ROLES_URL}${idRol}/`);
        await this.fetchRoles(); // Refrescar la lista
        console.log(`Rol (Grupo) con ID ${idRol} eliminado vía API.`);
        return { success: true, message: 'Rol eliminado.' };
      } catch (err) {
        this.error = `Error al eliminar el rol con ID ${idRol}.`;
         if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data);
        }
        console.error('Error en eliminarRol:', err.response ? err.response.data : err.message, this.error);
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },
  },
}); 