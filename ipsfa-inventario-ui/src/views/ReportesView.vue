<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-2">Generación de Reportes</h1>
        <p class="subtitle-1">Seleccione el tipo de reporte y aplique los filtros deseados.</p>
      </v-col>
    </v-row>

    <v-expansion-panels v-model="panelAbierto" multiple focusable>
      <v-expansion-panel
        v-for="(reporte, i) in tiposDeReportes"
        :key="i"
        :title="reporte.titulo"
        :value="reporte.id"
      >
        <v-expansion-panel-text>
          <p class="body-2 mb-4">{{ reporte.descripcion }}</p>
          <v-row dense>
            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeFecha">
              <v-menu
                v-model="reporte.filtrosUI.menuFechaDesde"
                :close-on-content-click="false"
                transition="scale-transition" offset-y min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="reporte.filtrosUI.fechaDesdeFormateada"
                    label="Fecha Desde"
                    prepend-icon="mdi-calendar"
                    readonly v-bind="props" outlined dense class="mb-2"
                  ></v-text-field>
                </template>
                <v-date-picker 
                    v-model="reporte.filtrosUI.fechaDesdePicker" 
                    @update:model-value="reporte.filtrosUI.menuFechaDesde = false"
                    locale="es-VE"
                ></v-date-picker>
              </v-menu>
            </v-col>
            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeFecha">
              <v-menu
                v-model="reporte.filtrosUI.menuFechaHasta"
                :close-on-content-click="false"
                transition="scale-transition" offset-y min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="reporte.filtrosUI.fechaHastaFormateada"
                    label="Fecha Hasta"
                    prepend-icon="mdi-calendar"
                    readonly v-bind="props" outlined dense class="mb-2"
                  ></v-text-field>
                </template>
                <v-date-picker 
                    v-model="reporte.filtrosUI.fechaHastaPicker"
                    @update:model-value="reporte.filtrosUI.menuFechaHasta = false"
                    locale="es-VE"
                ></v-date-picker>
              </v-menu>
            </v-col>

            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeCategoria">
              <v-select
                v-model="reporte.filtrosUI.categoria_id"
                :items="listaCategorias"
                item-title="nombre"
                item-value="id"
                label="Categoría del Bien"
                outlined dense clearable class="mb-2"
              ></v-select>
            </v-col>

            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeUnidad">
              <v-select
                v-model="reporte.filtrosUI.unidad_id"
                :items="listaUnidades"
                item-title="nombre"
                item-value="id"
                label="Unidad Administrativa / Sede"
                outlined dense clearable class="mb-2"
              ></v-select>
            </v-col>

            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeEstadoBien">
              <v-select
                v-model="reporte.filtrosUI.estado_bien"
                :items="mockEstadosBien"
                label="Estado del Bien"
                outlined dense clearable class="mb-2"
              ></v-select>
            </v-col>

          </v-row>
          <v-divider class="my-3"></v-divider>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="secondary" variant="outlined" @click="limpiarFiltros(reporte)" class="mr-2">
                <v-icon left>mdi-filter-remove-outline</v-icon> Limpiar Filtros
            </v-btn>
            <v-btn
              color="primary"
              @click="generarReporte(reporte, 'PDF')"
              class="mr-2"
              :loading="reporteEnProgreso"
              :disabled="reporteEnProgreso"
            >
              <v-icon left>mdi-file-pdf-box</v-icon>Generar PDF
            </v-btn>
            <v-btn color="green" dark @click="generarReporte(reporte, 'Excel')">
              <v-icon left>mdi-file-excel-box</v-icon>Generar Excel
            </v-btn>
          </v-card-actions>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script>
import { useReporteStore } from '@/stores/reporteStore';
import { useCategoriaStore } from '@/stores/categoriaStore';
import { useUnidadAdministrativaStore } from '@/stores/unidadAdministrativaStore';
import { mapState, mapActions } from 'pinia';
export default {
  name: 'ReportesView',
  data() {
    return {
      panelAbierto: [],
      tiposDeReportes: [
        {
          id: 'invGeneral',
          titulo: 'Inventario General de Bienes',
          descripcion: 'Lista detallada de todos los bienes muebles e inmuebles registrados.',
          filtros: { incluyeFecha: true, incluyeCategoria: false, incluyeUnidad: false, incluyeEstadoBien: false },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'bienesPorCat',
          titulo: 'Bienes por Categoría',
          descripcion: 'Agrupación de bienes según su categoría asignada.',
          filtros: { incluyeFecha: true, incluyeCategoria: true, incluyeUnidad: false, incluyeEstadoBien: false },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'bienesPorSede',
          titulo: 'Bienes por Unidad Administrativa / Sede',
          descripcion: 'Detalle de bienes asignados a cada unidad o sede específica.',
          filtros: { incluyeFecha: true, incluyeCategoria: false, incluyeUnidad: true, incluyeEstadoBien: false },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'depAcumulada',
          titulo: 'Reporte de Depreciación Acumulada',
          descripcion: 'Cálculo de la depreciación de los activos hasta una fecha determinada.',
          filtros: { incluyeFecha: true, incluyeCategoria: false, incluyeUnidad: false, incluyeEstadoBien: false },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
         {
          id: 'bienesDesinc',
          titulo: 'Bienes Desincorporados',
          descripcion: 'Listado de bienes que han sido dados de baja en un período específico.',
          filtros: { incluyeFecha: true, incluyeCategoria: false, incluyeUnidad: false, incluyeEstadoBien: false },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'bienesTrasl',
          titulo: 'Bienes Trasladados',
          descripcion: 'Registro de los traslados de bienes entre unidades en un período.',
          filtros: { incluyeFecha: true, incluyeCategoria: false, incluyeUnidad: true, incluyeEstadoBien: false },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
      ],
      // Datos Mock para los selectores de filtros
      mockUnidades: [ // Puedes copiar/reutilizar de TrasladoFormView.vue
        { id: 1, nombre: 'Presidencia' },
        { id: 2, nombre: 'Gerencia General' },
        { id: 3, nombre: 'Gerencia de Tecnologías de Información' },
        { id: 4, nombre: 'Gerencia de Administración y Finanzas' },
      ],
      mockEstadosBien: [ // Puedes copiar/reutilizar de BienFormView.vue (o definir aquí)
        'Nuevo', 'Bueno', 'Regular', 'Malo', 'En Reparación', 'Obsoleto', 'Desincorporado'
      ],
      reporteEnProgreso: false, // Para el estado de carga del botón
    };
  },
  computed: {
    ...mapState(useCategoriaStore, { listaCategorias: 'categorias' }),
    ...mapState(useUnidadAdministrativaStore, { listaUnidades: 'unidades' }),
  },
  methods: {
    ...mapActions(useReporteStore, [
      'generarReporteInventarioGeneral',
      'generarReporteInventarioExcel',
      'generarReportePorCategoriaPDF',
      'generarReportePorCategoriaExcel',
      'generarReportePorUnidadPDF',
      'generarReportePorUnidadExcel',
      'generarReporteDesincorporadosPDF',
      'generarReporteDesincorporadosExcel',
      'generarReporteTrasladadosPDF',
      'generarReporteTrasladadosExcel',
      'generarReporteDepreciacionPDF', // <-- NUEVO
      'generarReporteDepreciacionExcel' // <-- NUEVO
    ]),
    ...mapActions(useCategoriaStore, ['fetchCategorias']),
    ...mapActions(useUnidadAdministrativaStore, ['fetchUnidades']),
    async generarReporte(reporte, formato) {
      const reporteStore = useReporteStore();
      const filtros = {
        fecha_desde: reporte.filtrosUI.fechaDesdePicker ? new Date(reporte.filtrosUI.fechaDesdePicker).toISOString().split('T')[0] : '',
        fecha_hasta: reporte.filtrosUI.fechaHastaPicker ? new Date(reporte.filtrosUI.fechaHastaPicker).toISOString().split('T')[0] : '',
      };
      
      // Validar fechas para reportes que las requieren
      if (reporte.filtros.incluyeFecha && (!filtros.fecha_desde || !filtros.fecha_hasta)) {
        this.$emit('show-snackbar', { message: 'Por favor, seleccione un rango de fechas para este reporte.', color: 'warning' });
        return;
      }
      
      if (reporte.id === 'bienesPorCat') {
        if (!reporte.filtrosUI.categoria_id) {
          this.$emit('show-snackbar', { message: 'Por favor, seleccione una categoría para generar este reporte.', color: 'warning' });
          return;
        }
        filtros.categoria_id = reporte.filtrosUI.categoria_id;
        const categoria = this.listaCategorias.find(cat => cat.id === reporte.filtrosUI.categoria_id);
        if (categoria) filtros.categoria_nombre = categoria.nombre.replace(/\s+/g, '_');
      }
      
      if (reporte.id === 'bienesPorSede') {
        if (!reporte.filtrosUI.unidad_id) {
          this.$emit('show-snackbar', { message: 'Por favor, seleccione una unidad para generar este reporte.', color: 'warning' });
          return;
        }
        filtros.unidad_id = reporte.filtrosUI.unidad_id;
      }
      
      if (reporte.id === 'bienesTrasl') {
        if (reporte.filtrosUI.unidad_id) {
          filtros.unidad_id = reporte.filtrosUI.unidad_id;
        }
      }
      
      this.reporteEnProgreso = true;
      this.$emit('show-snackbar', { message: `Generando reporte en ${formato}, por favor espere...`, color: 'info' });
      
      try {
        if (reporte.id === 'invGeneral' && formato === 'PDF') {
          await reporteStore.generarReporteInventarioGeneral(filtros);
        } else if (reporte.id === 'invGeneral' && formato === 'Excel') {
          await reporteStore.generarReporteInventarioExcel(filtros);
        } else if (reporte.id === 'bienesPorCat' && formato === 'PDF') {
          await reporteStore.generarReportePorCategoriaPDF(filtros);
        } else if (reporte.id === 'bienesPorCat' && formato === 'Excel') {
          await reporteStore.generarReportePorCategoriaExcel(filtros);
        } else if (reporte.id === 'bienesPorSede' && formato === 'PDF') {
          await reporteStore.generarReportePorUnidadPDF(filtros);
        } else if (reporte.id === 'bienesPorSede' && formato === 'Excel') {
          await reporteStore.generarReportePorUnidadExcel(filtros);
        } else if (reporte.id === 'bienesDesinc') {
          if (formato === 'PDF') await reporteStore.generarReporteDesincorporadosPDF(filtros);
          if (formato === 'Excel') await reporteStore.generarReporteDesincorporadosExcel(filtros);
        } else if (reporte.id === 'bienesTrasl') {
          if (formato === 'PDF') await reporteStore.generarReporteTrasladadosPDF(filtros);
          if (formato === 'Excel') await reporteStore.generarReporteTrasladadosExcel(filtros);
        } else if (reporte.id === 'depAcumulada') {
          filtros.fecha_hasta = filtros.fecha_hasta || new Date().toISOString().split('T')[0];
          if (formato === 'PDF') await reporteStore.generarReporteDepreciacionPDF(filtros);
          if (formato === 'Excel') await reporteStore.generarReporteDepreciacionExcel(filtros);
        } else {
          this.$emit('show-snackbar', {
            message: `Funcionalidad para generar "${reporte.titulo}" en ${formato} no implementada.`,
            color: 'warning'
          });
        }
      } catch (error) {
        this.$emit('show-snackbar', {
          message: reporteStore.error || `No se pudo generar el reporte en ${formato}.`,
          color: 'error'
        });
      } finally {
        this.reporteEnProgreso = false;
      }
    },
    limpiarFiltros(reporte) {
      reporte.filtrosUI.fechaDesdePicker = null;
      reporte.filtrosUI.fechaDesdeFormateada = null;
      reporte.filtrosUI.fechaHastaPicker = null;
      reporte.filtrosUI.fechaHastaFormateada = null;
      reporte.filtrosUI.categoria_id = null;
      reporte.filtrosUI.unidad_id = null;
      reporte.filtrosUI.estado_bien = null;
    }
  },
  async mounted() {
    try {
      await Promise.all([
        this.fetchCategorias(),
        this.fetchUnidades()
      ]);
    } catch (e) {
      this.$emit('show-snackbar', { message: 'No se pudieron cargar los datos para los filtros.', color: 'error' });
    }
  },
  watch: {
    'tiposDeReportes': {
        handler(newVal) {
            newVal.forEach(reporte => {
                if (reporte.filtrosUI.fechaDesdePicker) {
                    const d = new Date(reporte.filtrosUI.fechaDesdePicker);
                    reporte.filtrosUI.fechaDesdeFormateada = d.toLocaleDateString('es-VE', { year: 'numeric', month: '2-digit', day: '2-digit' });
                } else {
                    reporte.filtrosUI.fechaDesdeFormateada = null;
                }

                if (reporte.filtrosUI.fechaHastaPicker) {
                    const d = new Date(reporte.filtrosUI.fechaHastaPicker);
                    reporte.filtrosUI.fechaHastaFormateada = d.toLocaleDateString('es-VE', { year: 'numeric', month: '2-digit', day: '2-digit' });
                } else {
                    reporte.filtrosUI.fechaHastaFormateada = null;
                }
            });
        },
        deep: true // Necesario para observar cambios dentro de los objetos del array
    }
  }
};
</script>

<style scoped>
.v-expansion-panel-title {
  font-weight: 500; /* Hacer el título del panel un poco más notable */
}
</style>