<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Dashboard de Control Patrimonial</h1>
        <p class="subtitle-1">Resumen del estado actual de los activos del IPSFANB.</p>
      </v-col>
    </v-row>

    <v-row v-if="isLoading" justify="center">
      <v-col cols="auto" class="text-center">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
        <p class="mt-4">Cargando estadísticas...</p>
      </v-col>
    </v-row>

    <div v-if="!isLoading && stats">
      <v-row>
        <v-col cols="12" sm="6" md="3">
          <v-card color="primary" dark>
            <v-card-title class="text-subtitle-1">
              <v-icon left>mdi-currency-usd</v-icon>
              Valor Patrimonial Total
            </v-card-title>
            <v-card-text class="text-h5 font-weight-bold">
              {{ formatCurrency(stats.valor_patrimonial_total) }}
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card color="blue-grey" dark>
            <v-card-title class="text-subtitle-1">
              <v-icon left>mdi-calculator-variant-outline</v-icon>
              Depreciación Acumulada
            </v-card-title>
            <v-card-text class="text-h5 font-weight-bold">
              {{ formatCurrency(stats.depreciacion_acumulada) }}
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card color="orange darken-2" dark>
            <v-card-title class="text-subtitle-1">
              <v-icon left>mdi-archive-alert-outline</v-icon>
              Bienes Obsoletos
            </v-card-title>
            <v-card-text class="text-h5 font-weight-bold">
              {{ stats.bienes_obsoletos_count }} Unidades
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" sm="6" md="3">
          <v-card color="green darken-1" dark>
            <v-card-title class="text-subtitle-1">
              <v-icon left>mdi-map-marker-multiple</v-icon>
              Total de Unidades Activas
            </v-card-title>
            <v-card-text class="text-h5 font-weight-bold">
              {{ stats.unidades_activas_count }} Unidades
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <v-row class="mt-4">
        <v-col cols="12" md="4">
          <v-card>
            <v-card-title>Distribución por Estado</v-card-title>
            <v-card-text>
               <v-list dense>
                 <v-list-item v-for="item in stats.distribucion_por_estado" :key="item.estado_bien">
                   <v-list-item-title>{{ item.estado_bien }}</v-list-item-title>
                   <template v-slot:append>
                     <v-chip color="primary" small>{{ item.count }}</v-chip>
                   </template>
                 </v-list-item>
               </v-list>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col cols="12" md="8">
          <v-card>
              <v-card-title>Inventario por Sede/Unidad</v-card-title>
              <v-table dense>
                  <thead>
                      <tr>
                      <th class="text-left">Sede/Unidad</th>
                      <th class="text-right">N° de Bienes</th>
                      <th class="text-right">Valor Estimado (Bs.)</th>
                      </tr>
                  </thead>
                  <tbody>
                      <tr v-for="sede in stats.inventario_por_sede" :key="sede.nombre">
                      <td>{{ sede.nombre }}</td>
                      <td class="text-right">{{ sede.cantidad_bienes }}</td>
                      <td class="text-right">{{ formatCurrency(sede.valor_estimado) }}</td>
                      </tr>
                  </tbody>
              </v-table>
          </v-card>
        </v-col>
      </v-row>
    </div>
    
    <v-row v-if="!isLoading && error">
        <v-col>
            <v-alert type="error" prominent border="left">
                No se pudieron cargar las estadísticas del dashboard. Por favor, intente recargar la página o contacte al administrador. <br>
                <small>Detalle: {{ error }}</small>
            </v-alert>
        </v-col>
    </v-row>

  </v-container>
</template>

<script>
import { useDashboardStore } from '@/stores/dashboardStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'DashboardView',
  data: () => ({
    // Ya no necesitamos datos de ejemplo aquí
  }),
  computed: {
    // Mapeamos el estado del dashboardStore al componente
    ...mapState(useDashboardStore, ['stats', 'isLoading', 'error']),
  },
  methods: {
    // Mapeamos la acción para poder llamarla con this.fetchDashboardStats()
    ...mapActions(useDashboardStore, ['fetchDashboardStats']),

    formatCurrency(value) {
      if (value === null || typeof value === 'undefined') return 'Bs. 0,00';
      const numValue = parseFloat(value);
      if (isNaN(numValue)) return 'N/A';
      return `Bs. ${numValue.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }
  },
  async mounted() {
    // Cuando el componente se monta, llamamos a la acción para cargar los datos
    try {
      await this.fetchDashboardStats();
    } catch (e) {
      // El error ya está en el store, pero podemos mostrar un snackbar si queremos
      this.$emit('show-snackbar', { 
        message: 'Error crítico al cargar datos del dashboard.', 
        color: 'error' 
      });
    }
  }
};
</script>

<style scoped>
.v-card-title {
  font-size: 1rem; /* Ajusta el tamaño si es necesario */
}
.v-card-text.text-h5 {
    line-height: 1.5; /* Asegura que el texto grande no se corte */
}
/* Podrías añadir más estilos si lo deseas */
</style>