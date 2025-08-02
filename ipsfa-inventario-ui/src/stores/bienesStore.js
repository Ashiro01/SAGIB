// src/stores/bienesStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Importamos nuestra instancia de Axios configurada

export const useBienesStore = defineStore('bienes', {
  state: () => ({
    bienes: [], // Aquí almacenaremos la lista de bienes del backend
    bienActual: null, // Para almacenar un bien individual (ej: para vista de detalle o edición)
    loading: false, // Para indicar si se está cargando datos
    error: null,    // Para almacenar mensajes de error de la API
  }),

  getters: {
    listaBienes: (state) => state.bienes,
    getBienActual: (state) => state.bienActual,
    isLoading: (state) => state.loading,
    getError: (state) => state.error,
  },

  actions: {
    // Acción para obtener todos los bienes del backend
    async fetchBienes() {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get('/bienes/');
        // Si la respuesta está paginada (DRF por defecto), usa response.data.results
        if (Array.isArray(response.data)) {
          this.bienes = response.data;
        } else if (response.data && Array.isArray(response.data.results)) {
          this.bienes = response.data.results;
        } else {
          this.bienes = [];
        }
        console.log('Bienes cargados desde API:', this.bienes);
      } catch (err) {
        this.error = 'Error al cargar los bienes desde la API.';
        console.error('Error en fetchBienes:', err.response ? err.response.data : err.message);
        throw err; 
      } finally {
        this.loading = false;
      }
    },

    // Acción para obtener un bien específico por ID
    async fetchBienById(id) {
      this.loading = true;
      this.error = null;
      this.bienActual = null;
      try {
        const response = await apiClient.get(`/bienes/${id}/`);
        this.bienActual = response.data;
        console.log('Bien individual cargado:', this.bienActual);
        return this.bienActual;
      } catch (err) {
        this.error = `Error al cargar el bien con ID ${id}.`;
        console.error('Error en fetchBienById:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // Acción para crear un nuevo bien
    async crearBien(datosDelBien) {
      this.loading = true;
      this.error = null;

      try {
        // Hacemos la petición POST a la API de Django
        // La API de Django espera los datos en el formato definido por BienSerializer
        // Asegúrate que `datosDelBien` coincida con los campos esperados por el backend.
        // Por ejemplo, la fecha podría necesitar un formato específico (YYYY-MM-DD).
        // Los valores numéricos deben ser números, no strings.
        const response = await apiClient.post('/bienes/', datosDelBien);

        // Si la creación es exitosa, el backend usualmente devuelve el objeto creado.
        // Podríamos añadirlo a nuestra lista local de bienes o recargar la lista.
        // Por ahora, solo registramos el éxito y devolvemos los datos.
        this.bienes.push(response.data); // Añade el nuevo bien a la lista local (opcional, fetchBienes lo haría)
        console.log('Bien creado vía API:', response.data);
        return response.data; // Devuelve el bien creado
      } catch (err) {
        this.error = 'Error al crear el bien.';
        if (err.response && err.response.data) {
            // DRF devuelve errores de validación detallados
            console.error('Error en crearBien (datos):', err.response.data);
            // Podríamos formatear estos errores para mostrarlos al usuario
            this.error = this.formatApiErrors(err.response.data);
        } else {
            console.error('Error en crearBien (general):', err.message);
        }
        throw new Error(this.error); // Propagar el error formateado o el mensaje general
      } finally {
        this.loading = false;
      }
    },

    // Acción para actualizar un bien existente
    async actualizarBien(id, datosDelBien) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.put(`/bienes/${id}/`, datosDelBien);
        // Actualiza el bien en la lista local
        const index = this.bienes.findIndex(b => b.id === id);
        if (index !== -1) {
          this.bienes[index] = response.data;
        }
        // Actualiza bienActual si corresponde
        if (this.bienActual && this.bienActual.id === id) {
          this.bienActual = response.data;
        }
        console.log('Bien actualizado vía API:', response.data);
        return response.data;
      } catch (err) {
        this.error = 'Error al actualizar el bien.';
        if (err.response && err.response.data) {
          console.error('Error en actualizarBien (datos):', err.response.data);
          this.error = this.formatApiErrors(err.response.data);
        } else {
          console.error('Error en actualizarBien (general):', err.message);
        }
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    // Acción para eliminar un bien existente
    async eliminarBien(idBien) {
      this.loading = true;
      this.error = null;
      try {
        await apiClient.delete(`/bienes/${idBien}/`);
        this.bienes = this.bienes.filter(bien => bien.id !== idBien);
        if (this.bienActual && this.bienActual.id === idBien) {
          this.bienActual = null;
        }
        console.log(`Bien con ID ${idBien} eliminado vía API.`);
        return { success: true, message: 'Bien eliminado correctamente.' };
      } catch (err) {
        this.error = `Error al eliminar el bien con ID ${idBien}.`;
        if (err.response && err.response.data) {
          console.error('Error en eliminarBien (datos):', err.response.data);
          this.error = this.formatApiErrors(err.response.data);
        } else {
          console.error('Error en eliminarBien (general):', err.message);
        }
        throw new Error(this.error);
      } finally {
        this.loading = false;
      }
    },

    // NUEVA ACCIÓN PARA CARGA MASIVA
    async subirArchivoBienes(archivo) {
      this.loading = true;
      this.error = null;

      const formData = new FormData();
      formData.append('file', archivo);

      try {
        const response = await apiClient.post('/bienes/upload/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        console.log('Respuesta de la carga masiva:', response.data);
        await this.fetchBienes();
        return response.data;
      } catch (err) {
        this.error = 'Error durante la carga masiva.';
        if (err.response && err.response.data) {
          console.error('Error en subirArchivoBienes (API):', err.response.data);
          throw err.response.data;
        } else {
          console.error('Error en subirArchivoBienes (General):', err.message);
          throw new Error(this.error);
        }
      } finally {
        this.loading = false;
      }
    },

    // Helper para formatear errores de API (si DRF devuelve un objeto de errores por campo)
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

    // Acción para obtener el siguiente código patrimonial disponible
    async obtenerSiguienteCodigoPatrimonial(codigoUnidad) {
      this.loading = true;
      this.error = null;
      try {
        const response = await apiClient.get(`/bienes/siguiente-codigo/${codigoUnidad}/`);
        console.log('Siguiente código patrimonial obtenido:', response.data);
        return response.data.siguiente_numero;
      } catch (err) {
        this.error = 'Error al obtener el siguiente código patrimonial.';
        console.error('Error en obtenerSiguienteCodigoPatrimonial:', err.response ? err.response.data : err.message);
        throw err;
      } finally {
        this.loading = false;
      }
    },
  },
});