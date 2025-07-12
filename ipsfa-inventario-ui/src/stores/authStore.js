// src/stores/authStore.js
import { defineStore } from 'pinia';
import router from '@/router'; // Importamos el router para la redirección

// Definimos el store con un ID único 'auth'
export const useAuthStore = defineStore('auth', {
  // STATE: Aquí definimos las variables reactivas del store (equivalente a 'data' en un componente)
  state: () => ({
    isAuthenticated: !!localStorage.getItem('accessToken'),
    usuario: null,
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
  }),

  // GETTERS: Son como las propiedades computadas para los stores.
  // Permiten obtener datos derivados del estado.
  getters: {
    isUserAuthenticated: (state) => state.isAuthenticated,
    getCurrentUser: (state) => state.usuario,
    getUserRole: (state) => state.usuario ? state.usuario.rol : null,
    getToken: (state) => state.accessToken,
  },

  // ACTIONS: Son como los métodos en los componentes.
  // Se usan para modificar el estado (mutaciones) o realizar operaciones asíncronas.
  actions: {
    // Acción para simular el inicio de sesión
    async login(credenciales) {
      try {
        // Usar axios en vez de fetch para evitar problemas de CORS y formato
        const axios = (await import('axios')).default;
        const response = await axios.post('http://127.0.0.1:8000/api/token/', {
          username: credenciales.username,
          password: credenciales.password
        });
        const data = response.data;
        this.accessToken = data.access;
        this.refreshToken = data.refresh;
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        this.isAuthenticated = true;
        // Obtener datos del usuario
        const userResp = await axios.get('http://127.0.0.1:8000/api/users/me/', {
          headers: { 'Authorization': `Bearer ${data.access}` }
        });
        this.usuario = userResp.data;
        return { success: true };
      } catch (error) {
        this.isAuthenticated = false;
        this.usuario = null;
        this.accessToken = null;
        this.refreshToken = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        // Mejorar mensaje de error para mostrar detalle de DRF si existe
        let msg = error.response && error.response.data && error.response.data.detail
          ? error.response.data.detail
          : error.message;
        return { success: false, message: msg };
      }
    },

    // Acción para cerrar sesión
    logout() {
      this.isAuthenticated = false;
      this.usuario = null;
      this.accessToken = null;
      this.refreshToken = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      router.push('/login');
    },

    // Acción para inicializar el estado de autenticación al cargar la app
    async initialize() {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
      this.isAuthenticated = !!accessToken;
      if (accessToken) {
        try {
          const axios = (await import('axios')).default;
          const userResp = await axios.get('http://127.0.0.1:8000/api/users/me/', {
            headers: { 'Authorization': `Bearer ${accessToken}` }
          });
          this.usuario = userResp.data;
        } catch (error) {
          this.isAuthenticated = false;
          this.usuario = null;
          this.accessToken = null;
          this.refreshToken = null;
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
        }
      } else {
        this.usuario = null;
      }
    },

    // (Opcional) Acción para chequear el estado de autenticación al cargar la app
    // checkAuthStatus() {
    //   const token = localStorage.getItem('authToken');
    //   if (token) {
    //     // Aquí normalmente validarías el token con el backend
    //     // Por ahora, si hay token, asumimos que está autenticado (simulación)
    //     this.isAuthenticated = true;
    //     this.token = token;
    //     // Deberías también cargar los datos del usuario aquí
    //     this.usuario = { nombre_completo: 'Usuario Restaurado', rol: 'Administrador (Restaurado)' }; 
    //   } else {
    //     this.isAuthenticated = false;
    //     this.usuario = null;
    //     this.token = null;
    //   }
    // },
  },
});