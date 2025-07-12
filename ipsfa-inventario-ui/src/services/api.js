// src/services/api.js (Ejemplo)
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api', // Tu URL base de API
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para añadir el token de autenticación a las peticiones
apiClient.interceptors.request.use(config => {
  const authStore = useAuthStore();
  const token = authStore.getToken; // Asumiendo que tienes un getter getToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`; // O 'Token ' + token
  }
  return config;
}, error => {
  return Promise.reject(error);
});

export default apiClient;