import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Tu instancia de Axios configurada

const API_USERS_URL = '/users/';
const API_GROUPS_URL = '/groups/';

export const useUsuarioStore = defineStore('usuario', {
  state: () => ({
    usuarios: [],
    usuarioActual: null,
    grupos: [],
    loading: false,
    error: null,
  }),
  getters: {
    listaUsuarios: (state) => state.usuarios,
    getUsuarioActual: (state) => state.usuarioActual,
    listaGrupos: (state) => state.grupos,
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

    async fetchUsuarios() {
      console.log('[usuarioStore] Iniciando fetchUsuarios...');
      this.loading = true;
      this.error = null;
      try {
        const timestamp = new Date().getTime();
        const url = `${API_USERS_URL}?timestamp=${timestamp}`;
        console.log(`[usuarioStore] GET ${url}`);
        const response = await apiClient.get(url);
        console.log('[usuarioStore] Respuesta de fetchUsuarios API:', response);

        if (response && response.data) {
          if (Array.isArray(response.data.results)) {
            this.usuarios = response.data.results;
            console.log('[usuarioStore] Usuarios actualizados desde response.data.results:', this.usuarios);
          } else if (Array.isArray(response.data)) {
            this.usuarios = response.data;
            console.log('[usuarioStore] Usuarios actualizados desde response.data (array directo):', this.usuarios);
          } else {
            console.warn('[usuarioStore] La respuesta de fetchUsuarios no tiene el formato esperado (ni results, ni array directo):', response.data);
            this.usuarios = []; // O manejar de otra forma, ej. no cambiar this.usuarios
          }
        } else {
          console.warn('[usuarioStore] Respuesta inválida o sin datos en fetchUsuarios:', response);
          this.usuarios = []; // Seguridad
        }
      } catch (err) {
        this.error = 'Error al cargar los usuarios.';
        console.error('[usuarioStore] Error en fetchUsuarios:', err.response ? err.response.data : err.message, err);
        // No lanzar el error aquí para permitir que el componente lo maneje si es necesario,
        // o para evitar interrumpir flujos si el error no es crítico para toda la app.
        // throw err; // Considera si relanzar el error es necesario para tu lógica de UI
      } finally {
        this.loading = false;
        console.log('[usuarioStore] fetchUsuarios finalizado.');
      }
    },

    async fetchUsuarioById(id) {
      this.loading = true;
      this.error = null;
      this.usuarioActual = null;
      try {
        const response = await apiClient.get(`${API_USERS_URL}${id}/`);
        this.usuarioActual = response.data;
        console.log('Usuario individual cargado:', this.usuarioActual);
        return this.usuarioActual;
      } catch (err) {
        this.error = `Error al cargar el usuario con ID ${id}.`;
        console.error('Error en fetchUsuarioById:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async crearUsuario(datosDelUsuario) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.post(API_USERS_URL, datosDelUsuario);
        // Se llama a fetchUsuarios para refrescar la lista completa
        await this.fetchUsuarios(); 
        console.log('Usuario creado vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al crear el usuario.';
        if (err.response && err.response.data) {
            console.error('Error en crearUsuario (datos):', err.response.data);
            this.error = this.formatApiErrors(err.response.data);
        } else {
            console.error('Error en crearUsuario (general):', err.message);
        }
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async actualizarUsuario(id, datosDelUsuario) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`${API_USERS_URL}${id}/`, datosDelUsuario);
        // Se llama a fetchUsuarios para refrescar la lista completa
        await this.fetchUsuarios();
         if (this.usuarioActual && this.usuarioActual.id === id) {
             // Actualiza el usuarioActual si está cargado, buscándolo en la nueva lista
             this.usuarioActual = this.usuarios.find(u => u.id === id) || null;
        }
        console.log('Usuario actualizado vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al actualizar el usuario.';
        if (err.response && err.response.data) {
            console.error('Error en actualizarUsuario (datos):', err.response.data);
            this.error = this.formatApiErrors(err.response.data);
        } else {
            console.error('Error en actualizarUsuario (general):', err.message);
        }
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    async eliminarUsuario(idUsuario) {
      console.log(`[usuarioStore] Iniciando eliminarUsuario para ID: ${idUsuario}`);
      this.loading = true;
      this.error = null;
      let resultado = { success: false, message: 'Error desconocido durante la eliminación.' };
      try {
        console.log(`[usuarioStore] DELETE ${API_USERS_URL}${idUsuario}/`);
        const response = await apiClient.delete(`${API_USERS_URL}${idUsuario}/`);
        console.log(`[usuarioStore] Respuesta de API delete para ID ${idUsuario}:`, response);
        
        // Asumimos éxito si no hay error y la API devuelve 2xx
        // El backend ahora devuelve 200 OK con un mensaje.
        console.log(`[usuarioStore] Usuario con ID ${idUsuario} eliminado, procediendo a fetchUsuarios.`);
        await this.fetchUsuarios(); // Refrescar la lista
        console.log(`[usuarioStore] fetchUsuarios completado después de eliminar ID ${idUsuario}.`);
        resultado = { success: true, message: response.data.detail || 'Usuario eliminado correctamente.' };
        return resultado;
      } catch (err) {
        console.error(`[usuarioStore] Error en eliminarUsuario para ID ${idUsuario}:`, err.response ? err.response.data : err.message, err);
        this.error = `Error al eliminar el usuario con ID ${idUsuario}.`;
        if (err.response && err.response.data) {
            this.error = this.formatApiErrors(err.response.data.detail || err.response.data);
        } else {
            // this.error ya tiene un mensaje genérico
        }
        resultado = { success: false, message: this.error };
        throw new Error(this.error); // Relanzar para que el componente lo capture
      } finally {
        this.loading = false;
        console.log(`[usuarioStore] eliminarUsuario para ID ${idUsuario} finalizado. Resultado:`, resultado);
      }
    },

    async fetchGrupos() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(API_GROUPS_URL);
        this.grupos = response.data.results || response.data;
        console.log('Grupos/Roles cargados desde API:', this.grupos);
      } catch (err) {
        this.error = 'Error al cargar los grupos/roles.';
        console.error('Error en fetchGrupos:', err.response ? err.response.data : err.message);
      } finally {
        this.loading = false;
      }
    }
  },
});
