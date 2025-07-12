<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col cols="12">
        <h1>Logs de Auditoría del Sistema</h1>
        <p>Registro de acciones importantes realizadas por los usuarios.</p>
      </v-col>
    </v-row>
    <v-card>
      <v-card-title>Filtros de Búsqueda</v-card-title>
      <v-card-text>
        <v-row dense class="align-center">
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filtros.usuario"
              label="Filtrar por Usuario (username)"
              prepend-inner-icon="mdi-account-search-outline"
              clearable hide-details dense outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filtros.accion"
              label="Filtrar por Acción"
              prepend-inner-icon="mdi-flash-outline"
              clearable hide-details dense outlined
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="2">
            <v-btn @click="aplicarFiltros" color="primary" :loading="isLoading">
              <v-icon left>mdi-filter-variant</v-icon>
              Filtrar
            </v-btn>
            <v-btn icon @click="limpiarFiltros" class="ml-2" title="Limpiar filtros">
              <v-icon>mdi-filter-remove-outline</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-card-text>
      <v-data-table
        :headers="headers"
        :items="listaLogs"
        :items-per-page="15"
        class="elevation-1"
        item-value="id"
        hover
        :loading="isLoading"
        loading-text="Cargando logs desde el servidor..."
        no-data-text="No hay logs que coincidan con la búsqueda."
      >
        <template v-slot:item.timestamp="{ item }">
          {{ formatDateTime(item.timestamp) }}
        </template>
        <template v-slot:item.detalles="{ item }">
            <div class="text-truncate" style="max-width: 400px;" :title="item.detalles">
                {{ item.detalles }}
            </div>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script>
import { useAuditLogStore } from '@/stores/auditLogStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'AuditLogView',
  data() {
    return {
      headers: [
        { title: 'Fecha y Hora', key: 'timestamp', align: 'start', width: '180px' },
        { title: 'Usuario', key: 'usuario_username', width: '150px' },
        { title: 'Acción', key: 'accion', width: '200px' },
        { title: 'Dirección IP', key: 'ip_address', width: '150px' },
        { title: 'Detalles', key: 'detalles', sortable: false },
      ],
      filtros: {
        usuario: '',
        accion: '',
        // fechaDesde: null,
        // fechaHasta: null,
      },
    };
  },
  computed: {
    ...mapState(useAuditLogStore, ['listaLogs', 'isLoading', 'error']),
  },
  methods: {
    ...mapActions(useAuditLogStore, ['fetchLogs']),
    formatDateTime(dateTimeString) {
      if (!dateTimeString) return '';
      const options = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' };
      return new Date(dateTimeString).toLocaleString('es-VE', options);
    },
    async aplicarFiltros() {
      try {
        // Creamos un objeto de filtros limpios para no enviar valores vacíos
        const filtrosActivos = {};
        if (this.filtros.usuario) filtrosActivos.usuario = this.filtros.usuario;
        if (this.filtros.accion) filtrosActivos.accion = this.filtros.accion;
        await this.fetchLogs(filtrosActivos);
      } catch (error) {
        this.$emit('show-snackbar', { message: this.error || 'Error al aplicar filtros.', color: 'error' });
      }
    },
    limpiarFiltros() {
      this.filtros = { usuario: '', accion: '' };
      this.aplicarFiltros(); // Vuelve a cargar todos los logs sin filtros
    }
  },
  async mounted() {
    await this.aplicarFiltros(); // Carga inicial de logs sin filtros
  }
};
</script>

<style scoped>
.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>