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

    // NUEVA ACCIÓN para actualizar datos del perfil y foto
    async updateUserProfile(userData) {
      this.loading = true;
      this.error = null;
      try {
        const axios = (await import('axios')).default;
        const formData = new FormData();
        formData.append('first_name', userData.first_name);
        formData.append('last_name', userData.last_name);
        formData.append('email', userData.email);

        // Añadir la foto solo si el usuario seleccionó una nueva
        if (userData.foto_perfil instanceof File) {
          formData.append('perfil.foto_perfil', userData.foto_perfil);
        }

        // Usamos PATCH para una actualización parcial
        await axios.patch('http://127.0.0.1:8000/api/perfil/me/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
            'Authorization': `Bearer ${this.accessToken}`
          },
        });

        // Volver a obtener los datos frescos del usuario
        const userResp = await axios.get('http://127.0.0.1:8000/api/users/me/', {
          headers: { 'Authorization': `Bearer ${this.accessToken}` }
        });
        this.usuario = userResp.data;
        console.log('Perfil de usuario actualizado:', userResp.data);
        return userResp.data;
      } catch (err) {
        const errorMessage = err.response?.data ? this.formatApiErrors(err.response.data) : 'Error al actualizar el perfil.';
        this.error = errorMessage;
        console.error('Error en updateUserProfile:', err.response?.data || err.message);
        throw new Error(errorMessage);
      } finally {
        this.loading = false;
      }
    },

    // NUEVA ACCIÓN para cambiar la contraseña
    async changePassword(passwordData) {
      this.loading = true;
      this.error = null;
      try {
        const axios = (await import('axios')).default;
        // Asegurarse de que los tres campos estén presentes y sean string
        const payload = {
          old_password: passwordData.old_password ? String(passwordData.old_password) : '',
          new_password: passwordData.new_password ? String(passwordData.new_password) : '',
          new_password_confirm: passwordData.new_password_confirm ? String(passwordData.new_password_confirm) : ''
        };
        const response = await axios.put('http://127.0.0.1:8000/api/perfil/change-password/', payload, {
          headers: {
            'Authorization': `Bearer ${this.accessToken}`
          }
        });
        console.log('Contraseña cambiada:', response.data);
        return response.data;
      } catch (err) {
        // Mejor manejo de errores: mostrar mensaje del backend si existe
        let errorMessage = 'Error al cambiar la contraseña.';
        if (err.response && err.response.data) {
          if (typeof err.response.data === 'string') {
            errorMessage = err.response.data;
          } else if (typeof err.response.data === 'object') {
            // Concatenar todos los mensajes de error
            errorMessage = Object.values(err.response.data).flat().join(' ');
          }
        }
        this.error = errorMessage;
        console.error('Error en changePassword:', err.response?.data || err.message);
        throw new Error(errorMessage);
      } finally {
        this.loading = false;
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