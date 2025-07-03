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
                    locale="es-ES"
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
                    locale="es-ES"
                ></v-date-picker>
              </v-menu>
            </v-col>

            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeCategoria">
              <v-select
                v-model="reporte.filtrosUI.categoria_id"
                :items="mockCategorias"
                item-title="nombre"
                item-value="id"
                label="Categoría del Bien"
                outlined dense clearable class="mb-2"
              ></v-select>
            </v-col>

            <v-col cols="12" md="6" v-if="reporte.filtros.incluyeUnidad">
              <v-select
                v-model="reporte.filtrosUI.unidad_id"
                :items="mockUnidades"
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
            <v-btn color="primary" @click="generarReporte(reporte, 'PDF')" class="mr-2">
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
export default {
  name: 'ReportesView',
  data() {
    return {
      panelAbierto: [], // Controla qué paneles están abiertos, puede ser un array para 'multiple'
      tiposDeReportes: [ // Definición de los reportes y sus filtros
        {
          id: 'invGeneral',
          titulo: 'Inventario General de Bienes',
          descripcion: 'Lista detallada de todos los bienes muebles e inmuebles registrados.',
          filtros: { incluyeFecha: false, incluyeCategoria: true, incluyeUnidad: true, incluyeEstadoBien: true },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'bienesPorCat',
          titulo: 'Bienes por Categoría',
          descripcion: 'Agrupación de bienes según su categoría asignada.',
          filtros: { incluyeFecha: false, incluyeCategoria: true, incluyeUnidad: false, incluyeEstadoBien: true },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'bienesPorSede',
          titulo: 'Bienes por Unidad Administrativa / Sede',
          descripcion: 'Detalle de bienes asignados a cada unidad o sede específica.',
          filtros: { incluyeFecha: false, incluyeCategoria: false, incluyeUnidad: true, incluyeEstadoBien: true },
          filtrosUI: { fechaDesdePicker: null, fechaDesdeFormateada: null, menuFechaDesde: false, fechaHastaPicker: null, fechaHastaFormateada: null, menuFechaHasta: false, categoria_id: null, unidad_id: null, estado_bien: null }
        },
        {
          id: 'depAcumulada',
          titulo: 'Reporte de Depreciación Acumulada',
          descripcion: 'Cálculo de la depreciación de los activos hasta una fecha determinada.',
          filtros: { incluyeFecha: true, incluyeCategoria: true, incluyeUnidad: false, incluyeEstadoBien: false },
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
      mockCategorias: [
        { id: 1, nombre: 'Mobiliario de Oficina' },
        { id: 2, nombre: 'Equipos de Computación' },
        { id: 3, nombre: 'Vehículos' },
        { id: 4, nombre: 'Maquinaria y Equipos' },
        { id: 5, nombre: 'Bienes Inmuebles' },
      ],
      mockUnidades: [ // Puedes copiar/reutilizar de TrasladoFormView.vue
        { id: 1, nombre: 'Presidencia' },
        { id: 2, nombre: 'Gerencia General' },
        { id: 3, nombre: 'Gerencia de Tecnologías de Información' },
        { id: 4, nombre: 'Gerencia de Administración y Finanzas' },
      ],
      mockEstadosBien: [ // Puedes copiar/reutilizar de BienFormView.vue (o definir aquí)
        'Nuevo', 'Bueno', 'Regular', 'Malo', 'En Reparación', 'Obsoleto', 'Desincorporado'
      ],
    };
  },
  methods: {
    generarReporte(reporte, formato) {
      const filtrosAplicados = {
        fechaDesde: reporte.filtrosUI.fechaDesdeFormateada,
        fechaHasta: reporte.filtrosUI.fechaHastaFormateada,
        categoria: this.mockCategorias.find(c => c.id === reporte.filtrosUI.categoria_id)?.nombre,
        unidad: this.mockUnidades.find(u => u.id === reporte.filtrosUI.unidad_id)?.nombre,
        estado: reporte.filtrosUI.estado_bien,
      };

      // Limpiamos los filtros que no aplican o no fueron seleccionados
      for (const key in filtrosAplicados) {
        if (filtrosAplicados[key] === null || typeof filtrosAplicados[key] === 'undefined') {
          delete filtrosAplicados[key];
        }
      }

      alert(
        `Simulando generación del reporte:\n"${reporte.titulo}" en formato ${formato}.\n` +
        `Filtros Aplicados: ${JSON.stringify(filtrosAplicados, null, 2) || 'Ninguno'}`
      );
    },
    limpiarFiltros(reporte) {
        reporte.filtrosUI.fechaDesdePicker = null;
        reporte.filtrosUI.fechaDesdeFormateada = null;
        reporte.filtrosUI.fechaHastaPicker = null;
        reporte.filtrosUI.fechaHastaFormateada = null;
        reporte.filtrosUI.categoria_id = null;
        reporte.filtrosUI.unidad_id = null;
        reporte.filtrosUI.estado_bien = null;
        // Esto limpiará los v-model, y los campos de texto deberían reflejarlo.
    }
  },
  watch: {
    // Watchers para actualizar las fechas formateadas cuando cambian los pickers
    // Esto es un poco repetitivo; en un proyecto más grande, se podría crear un componente de filtro de fecha reutilizable.
    'tiposDeReportes': {
        handler(newVal) {
            newVal.forEach(reporte => {
                if (reporte.filtrosUI.fechaDesdePicker) {
                    const d = new Date(reporte.filtrosUI.fechaDesdePicker);
                    reporte.filtrosUI.fechaDesdeFormateada = d.toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' });
                } else {
                    reporte.filtrosUI.fechaDesdeFormateada = null;
                }

                if (reporte.filtrosUI.fechaHastaPicker) {
                    const d = new Date(reporte.filtrosUI.fechaHastaPicker);
                    reporte.filtrosUI.fechaHastaFormateada = d.toLocaleDateString('es-ES', { year: 'numeric', month: '2-digit', day: '2-digit' });
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