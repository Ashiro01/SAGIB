// src/stores/movimientoStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Tu instancia de Axios

const API_MOVIMIENTOS_URL = '/movimientos-bienes/';

export const useMovimientoStore = defineStore('movimiento', {
  state: () => ({
    movimientos: [], // Para listar movimientos si fuera necesario en otra vista
    movimientoActual: null,
    loading: false,
    error: null,
  }),
  getters: {
    listaMovimientos: (state) => state.movimientos,
    getMovimientoActual: (state) => state.movimientoActual,
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

    // Acción para registrar un nuevo movimiento (Traslado, Desincorporación, etc.)
    async registrarMovimiento(datosDelMovimiento) {
      this.loading = true;
      this.error = null;
      try {
        // El backend espera los IDs para las ForeignKey (bien, unidad_origen, unidad_destino)
        // El usuario_registra se setea en el backend (perform_create)
        const response = await apiClient.post(API_MOVIMIENTOS_URL, datosDelMovimiento);

        // Opcional: añadir a la lista local si se va a mostrar, o simplemente notificar éxito.
        // this.movimientos.unshift(response.data); 

        console.log('Movimiento registrado vía API:', response.data);
        return response.data; // Devuelve el movimiento creado
      } catch (err) {
        this.error = 'Error al registrar el movimiento.';
        if (err.response && err.response.data) {
            console.error('Error en registrarMovimiento (datos):', err.response.data);
            this.error = this.formatApiErrors(err.response.data);
        } else {
            console.error('Error en registrarMovimiento (general):', err.message);
        }
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    // Podríamos añadir una acción para listar movimientos de un bien específico si es necesario
    async fetchMovimientosPorBien(bienId) {
      this.loading = true;
      this.error = null;
      try {
        // El backend necesitaría un filtro para esto, ej: /api/movimientos-bienes/?bien_id=${bienId}
        // O un endpoint personalizado. Por ahora, no lo implementaremos en el backend.
        // Esta es solo una idea para el futuro.
        const response = await apiClient.get(`${API_MOVIMIENTOS_URL}?bien=${bienId}`);
        this.movimientos = response.data.results || response.data;
        console.log(`Movimientos para el bien ID ${bienId} cargados:`, this.movimientos);
        return this.movimientos;
      } catch (err) {
        this.error = `Error al cargar movimientos para el bien ID ${bienId}.`;
        console.error('Error en fetchMovimientosPorBien:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    }
  },
}); 