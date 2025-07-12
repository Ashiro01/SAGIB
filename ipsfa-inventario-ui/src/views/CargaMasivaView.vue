<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-2">Carga Masiva de Bienes</h1>
        <p class="subtitle-1">
          Utilice esta sección para importar múltiples bienes al sistema desde un archivo CSV o Excel.
        </p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Instrucciones y Selección de Archivo</v-card-title>
          <v-card-text>
            <p>
              Asegúrese de que su archivo cumpla con el formato esperado. Las columnas requeridas son:
              <strong>FECHA_ADQUISICION, DESCRIPCION, CANTIDAD, MARCA, MODELO, SERIAL, CODIGO_ANTERIOR,
              N_ORDEN_COMPRA_FACTURA, PROVEEDOR, VALOR_UNITARIO_BS, VALOR_UNITARIO_USD, RESPONSABLE_AREA,
              CARGO_RESPONSABLE, UBICACION_FISICA, ESTADO_BIEN, OBSERVACIONES.</strong>
            </p>
            <p>
              Formatos permitidos: <code>.csv</code> (delimitado por comas o punto y coma), <code>.xlsx</code> (Excel).
            </p>

            <v-btn color="info" variant="outlined" @click="descargarPlantilla" class="mb-6">
              <v-icon left>mdi-file-download-outline</v-icon>
              Descargar Plantilla de Ejemplo (CSV)
            </v-btn>

            <v-file-input
              v-model="archivoSeleccionado"
              label="Seleccione el archivo para la carga masiva"
              placeholder="Haga clic aquí para buscar el archivo"
              accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
              show-size
              outlined
              dense
              prepend-icon="mdi-paperclip"
              @change="manejarSeleccionArchivo"
              :loading="procesando"
              :disabled="procesando"
            ></v-file-input>

            <div v-if="archivoInfo.nombre" class="mt-2">
              <p class="font-weight-medium">Archivo seleccionado:</p>
              <p>
                <v-icon small class="mr-1">mdi-file-document-outline</v-icon>
                {{ archivoInfo.nombre }} ({{ archivoInfo.tamanoKB }} KB, Tipo: {{ archivoInfo.tipo }})
              </p>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn 
              color="primary" 
              @click="procesarArchivo" 
              :disabled="!archivoSeleccionado || procesando"
              :loading="procesando"
              large
            >
              <v-icon left>mdi-cogs</v-icon>
              Cargar y Procesar Archivo
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Resultado del Procesamiento</v-card-title>
          <v-card-text>
            <div v-if="!resultadoProceso.mensaje && !procesando">
              <p class="text-center grey--text">
                <v-icon large color="grey">mdi-information-outline</v-icon><br>
                Los resultados de la carga se mostrarán aquí.
              </p>
            </div>
            <div v-if="procesando" class="text-center">
                <v-progress-circular indeterminate color="primary" size="64" class="mb-3"></v-progress-circular>
                <p>Procesando archivo, por favor espere...</p>
            </div>
            <div v-if="resultadoProceso.mensaje && !procesando">
              <v-alert :type="resultadoProceso.tipoAlerta" prominent border="left" dense>
                <h6 class="text-h6">{{ resultadoProceso.titulo }}</h6>
                <div>{{ resultadoProceso.mensaje }}</div>
                <ul v-if="resultadoProceso.detalles && resultadoProceso.detalles.length > 0" class="mt-2 text-body-2">
                  <li v-for="(detalle, idx) in resultadoProceso.detalles" :key="`det-${idx}`">
                    {{ detalle }}
                  </li>
                </ul>
                <v-list v-if="resultadoProceso.errors && resultadoProceso.errors.length > 0" dense class="mt-2">
                  <v-list-subheader>DETALLE DE ERRORES</v-list-subheader>
                  <v-list-item v-for="(err, idx) in resultadoProceso.errors" :key="`err-${idx}`">
                    <v-list-item-title class="font-weight-bold">Fila {{ err.fila }}:</v-list-item-title>
                    <v-list-item-subtitle>
                      <span v-for="(msg, field) in err.errores" :key="field">
                        <strong>{{ field }}:</strong> {{ msg.join ? msg.join(', ') : msg }}
                      </span>
                    </v-list-item-subtitle>
                  </v-list-item>
                </v-list>
              </v-alert>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useBienesStore } from '@/stores/bienesStore';

export default {
  name: 'CargaMasivaView',
  data() {
    return {
      archivoSeleccionado: null,
      archivoInfo: {
        nombre: '',
        tamanoKB: 0,
        tipo: '',
      },
      procesando: false,
      resultadoProceso: {
        titulo: '',
        mensaje: '',
        detalles: [],
        errors: [],
        tipoAlerta: 'info',
      },
    };
  },
  methods: {
    manejarSeleccionArchivo() {
      if (this.archivoSeleccionado) {
        const file = Array.isArray(this.archivoSeleccionado) ? this.archivoSeleccionado[0] : this.archivoSeleccionado;
        if (file) {
             this.archivoInfo.nombre = file.name;
             this.archivoInfo.tamanoKB = (file.size / 1024).toFixed(2);
             this.archivoInfo.tipo = file.type || 'Desconocido';
        } else {
            this.resetArchivoInfo();
        }
      } else {
        this.resetArchivoInfo();
      }
      this.resultadoProceso = { titulo: '', mensaje: '', detalles: [], errors: [], tipoAlerta: 'info' };
    },
    resetArchivoInfo() {
        this.archivoInfo.nombre = '';
        this.archivoInfo.tamanoKB = 0;
        this.archivoInfo.tipo = '';
        this.archivoSeleccionado = null;
    },
    descargarPlantilla() {
      const csvContent = "FECHA DE ADQUISICIÓN;DESCRIPCIÓN;CANTIDAD;MARCA;MODELO;SERIAL;CÓDIGO;N° ORDEN DE COMPRA O N° DE FACTURA;PROVEEDOR;VALOR UNITARIO Bs.;VALOR UNITARIO $;RESPONSABLE DEL ÁREA;CARGO DEL RESPONSABLE;UBICACIÓN FÍSICA;ESTADO DEL BIEN;OBSERVACIONES\n" +
                         "15/01/2025;Laptop de Ejemplo;1;HP;ProBook;SN12345;COD-ANT-001;FAC-2025-01;PROVEEDOR EJEMPLO C.A.;15000.50;400.00;JOHN DOE;ANALISTA;OFICINA DE TI;Nuevo;Asignado para desarrollo.\n";
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement("a");
      const url = URL.createObjectURL(blob);
      link.setAttribute("href", url);
      link.setAttribute("download", "plantilla_carga_bienes.csv");
      link.style.visibility = 'hidden';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },
    async procesarArchivo() {
      if (!this.archivoSeleccionado) {
        this.$emit('show-snackbar', { message: 'Por favor, seleccione un archivo primero.', color: 'warning' });
        return;
      }
      const file = Array.isArray(this.archivoSeleccionado) ? this.archivoSeleccionado[0] : this.archivoSeleccionado;
      this.procesando = true;
      this.resultadoProceso = { titulo: '', mensaje: '', detalles: [], errors: [], tipoAlerta: 'info' };
      const bienesStore = useBienesStore();
      try {
        const resultadoApi = await bienesStore.subirArchivoBienes(file);
        this.resultadoProceso.titulo = 'Procesamiento Exitoso';
        this.resultadoProceso.mensaje = resultadoApi.status || 'El archivo fue procesado.';
        this.resultadoProceso.detalles = [
          `Total de registros procesados: ${resultadoApi.total_procesados}`,
          `Bienes creados exitosamente: ${resultadoApi.bienes_creados}`,
        ];
        this.resultadoProceso.tipoAlerta = 'success';
        this.$emit('show-snackbar', { message: 'Archivo procesado con éxito.', color: 'success' });
      } catch (errorApi) {
        this.resultadoProceso.titulo = 'Error en el Procesamiento';
        this.resultadoProceso.mensaje = errorApi.status || errorApi.error || 'Ocurrieron errores al procesar el archivo.';
        this.resultadoProceso.detalles = [
          `Bienes creados antes del error (si aplica): ${errorApi.success_count || 0}`,
          `Número de errores encontrados: ${errorApi.error_count || 0}`,
        ];
        this.resultadoProceso.errors = errorApi.errors || [];
        this.resultadoProceso.tipoAlerta = 'error';
        this.$emit('show-snackbar', { message: 'Se encontraron errores en el archivo.', color: 'error' });
      } finally {
        this.procesando = false;
      }
    },
  },
  watch: {
    archivoSeleccionado(newVal) {
        if (!newVal) {
            this.resetArchivoInfo();
        }
    }
  }
};
</script>

<style scoped>
.font-weight-medium {
    font-weight: 500;
}
/* Puedes añadir más estilos si lo deseas */
</style>