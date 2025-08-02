<template>
  <v-container>
    <v-card>
      <v-card-title>
        <span class="text-h5">Registrar Desincorporación de Bien</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formDesincorporacion" v-model="validForm">
          <v-row>
            <v-col cols="12">
              <v-autocomplete
                v-model="bienSeleccionadoId"
                :items="listaBienesDelStore"
                item-title="displayText"
                item-value="id"
                label="Seleccionar Bien a Desincorporar"
                placeholder="Escriba para buscar código o descripción..."
                :rules="[rules.required]"
                outlined
                dense
                @update:model-value="alSeleccionarBien"
                :loading="isLoadingBienes"
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props" :title="null">
                    <div>
                      <v-list-item-title>{{ item.raw.codigo_patrimonial }} - {{ item.raw.descripcion }}</v-list-item-title>
                      <v-list-item-subtitle>Estado Actual: {{ item.raw.estado_bien }} | Ubicación: {{ item.raw.ubicacion_fisica }}</v-list-item-subtitle>
                    </div>
                  </v-list-item>
                </template>
                <template v-slot:selection="{ item }">
                    <span>{{ item.raw.codigo_patrimonial }} - {{ item.raw.descripcion }}</span>
                </template>
              </v-autocomplete>
            </v-col>

            <v-col cols="12" v-if="bienSeleccionadoObjeto">
              <v-subheader>Información del Bien Seleccionado</v-subheader>
              <v-row dense>
                <v-col cols="12" md="4">
                  <v-text-field :model-value="bienSeleccionadoObjeto.codigo_patrimonial" label="Código Patrimonial" readonly outlined dense></v-text-field>
                </v-col>
                <v-col cols="12" md="8">
                  <v-text-field :model-value="bienSeleccionadoObjeto.descripcion" label="Descripción" readonly outlined dense></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-text-field :model-value="bienSeleccionadoObjeto.marca" label="Marca" readonly outlined dense></v-text-field>
                </v-col>
                 <v-col cols="12" md="4">
                  <v-text-field :model-value="bienSeleccionadoObjeto.modelo" label="Modelo" readonly outlined dense></v-text-field>
                </v-col>
                <v-col cols="12" md="4">
                  <v-text-field :model-value="bienSeleccionadoObjeto.estado_bien" label="Estado Actual" readonly outlined dense></v-text-field>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12"><v-divider class="my-3"></v-divider></v-col>

            <v-col cols="12">
              <v-subheader>Detalles de la Desincorporación</v-subheader>
            </v-col>
            <v-col cols="12" md="6">
              <v-menu
                ref="menuFechaDesincorporacion"
                v-model="menuFechaDesincorporacion"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="desincorporacion.fecha_movimiento_formateada"
                    label="Fecha de Desincorporación"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    :rules="[rules.required]"
                    outlined
                    dense
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="desincorporacion.fecha_movimiento_picker"
                  no-title
                  @update:model-value="actualizarFechaDesincorporacion"
                  locale="es-VE"
                ></v-date-picker>
              </v-menu>
            </v-col>

            <v-col cols="12" md="6">
              <v-select
                v-model="desincorporacion.motivo_desincorporacion"
                :items="motivosDesincorporacion"
                label="Motivo de Desincorporación"
                :rules="[rules.required]"
                outlined
                dense
              ></v-select>
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="desincorporacion.numero_oficio_referencia"
                label="N° Oficio/Acta de Desincorporación"
                :rules="[rules.required]"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="desincorporacion.observaciones_movimiento"
                label="Destino Final del Bien / Observaciones Adicionales"
                outlined
                dense
              ></v-text-field>
            </v-col>

          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" text @click="cancelar">Cancelar</v-btn>
        <v-btn color="error" :disabled="!validForm || procesandoDesincorporacion" :loading="procesandoDesincorporacion" @click="registrarDesincorporacionLocal">
          Registrar Desincorporación
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import { useMovimientoStore } from '@/stores/movimientoStore';
import { useBienesStore } from '@/stores/bienesStore';

export default {
  name: 'DesincorporacionFormView',
  data: () => ({
    validForm: false,
    menuFechaDesincorporacion: false,
    procesandoDesincorporacion: false,
    bienSeleccionadoId: null,
    bienSeleccionadoObjeto: null,
    desincorporacion: {
      tipo_movimiento: 'DESINCORPORACION',
      fecha_movimiento_picker: new Date(),
      fecha_movimiento_formateada: new Date().toLocaleDateString('es-VE', { year: 'numeric', month: '2-digit', day: '2-digit'}),
      motivo_desincorporacion: null,
      numero_oficio_referencia: '',
      observaciones_movimiento: '',
    },
    motivosDesincorporacion: [
      'Obsoleto por avance tecnológico',
      'Dañado / Fin de vida útil irreparable',
      'Siniestro (Robo, Hurto, Incendio, Inundación)',
      'Venta autorizada',
      'Donación autorizada',
      'Extraviado / No localizado',
      'Otro (especificar en observaciones)',
    ],
    rules: {
      required: value => !!value || 'Este campo es requerido.',
    },
  }),
  computed: {
    listaBienesDelStore() {
      const bienesStore = useBienesStore();
      return bienesStore.listaBienes
        .filter(b => b.estado_bien !== 'DESINCORPORADO')
        .map(bien => ({
          ...bien,
          displayText: `${bien.codigo_patrimonial} - ${bien.descripcion} (Estado: ${bien.estado_bien})`
        }));
    },
    isLoadingBienes() {
      const bienesStore = useBienesStore();
      return bienesStore.isLoading;
    }
  },
  methods: {
    async cargarBienesParaSelector() {
      this.procesandoDesincorporacion = true;
      const bienesStore = useBienesStore();
      try {
        if (bienesStore.listaBienes.length === 0) { // Cargar solo si no están ya en el store
            await bienesStore.fetchBienes();
        }
      } catch (error) {
        this.$emit('show-snackbar', { message: 'Error al cargar bienes para el selector.', color: 'error' });
      } finally {
        this.procesandoDesincorporacion = false;
      }
    },
    alSeleccionarBien(bienId) {
      this.bienSeleccionadoId = bienId;
      if (bienId) {
        const bienesStore = useBienesStore();
        this.bienSeleccionadoObjeto = bienesStore.listaBienes.find(b => b.id === bienId);
      } else {
        this.bienSeleccionadoObjeto = null;
      }
    },
    actualizarFechaDesincorporacion() {
      if (this.desincorporacion.fecha_movimiento_picker) {
        const d = new Date(this.desincorporacion.fecha_movimiento_picker);
        this.desincorporacion.fecha_movimiento_formateada = d.toLocaleDateString('es-VE', {
          year: 'numeric', month: '2-digit', day: '2-digit'
        });
      } else {
        this.desincorporacion.fecha_movimiento_formateada = null;
      }
      this.menuFechaDesincorporacion = false;
    },
    async registrarDesincorporacionLocal() {
      const { valid } = await this.$refs.formDesincorporacion.validate();
      if (!valid) {
        this.$emit('show-snackbar', { message: 'Formulario inválido. Revise los campos.', color: 'error' });
        return;
      }
      if (!this.bienSeleccionadoId) {
        this.$emit('show-snackbar', { message: 'Debe seleccionar un bien a desincorporar.', color: 'warning' });
        return;
      }
      if (this.bienSeleccionadoObjeto && this.bienSeleccionadoObjeto.estado_bien === 'DESINCORPORADO') {
        this.$emit('show-snackbar', { message: 'Este bien ya se encuentra desincorporado.', color: 'warning' });
        return;
      }

      this.procesandoDesincorporacion = true;
      const movimientoStore = useMovimientoStore();

      const payload = {
        bien: this.bienSeleccionadoId,
        tipo_movimiento: 'DESINCORPORACION',
        fecha_movimiento: this.desincorporacion.fecha_movimiento_picker
                            ? new Date(this.desincorporacion.fecha_movimiento_picker).toISOString()
                            : new Date().toISOString(),
        motivo_desincorporacion: this.desincorporacion.motivo_desincorporacion,
        numero_oficio_referencia: this.desincorporacion.numero_oficio_referencia,
        observaciones_movimiento: this.desincorporacion.observaciones_movimiento,
      };

      try {
        await movimientoStore.registrarMovimiento(payload);
        this.$emit('show-snackbar', {
          message: `Desincorporación del bien "${this.bienSeleccionadoObjeto?.descripcion || 'seleccionado'}" registrada exitosamente.`,
          color: 'success'
        });
        const bienesStore = useBienesStore();
        await bienesStore.fetchBienes();
        this.resetForm();
        this.$router.push('/');
      } catch (error) {
        this.$emit('show-snackbar', {
          message: movimientoStore.getError || 'Error al registrar la desincorporación.',
          color: 'error'
        });
      } finally {
        this.procesandoDesincorporacion = false;
      }
    },
    resetForm() {
      this.bienSeleccionadoId = null;
      this.bienSeleccionadoObjeto = null;
      this.desincorporacion = {
        tipo_movimiento: 'DESINCORPORACION',
        fecha_movimiento_picker: new Date(),
        fecha_movimiento_formateada: new Date().toLocaleDateString('es-VE', { year: 'numeric', month: '2-digit', day: '2-digit'}),
        motivo_desincorporacion: null,
        numero_oficio_referencia: '',
        observaciones_movimiento: '',
      };
      if (this.$refs.formDesincorporacion) {
        this.$refs.formDesincorporacion.resetValidation();
      }
    },
    cancelar() {
      this.resetForm();
      this.$router.push('/');
    },
  },
  watch: {
    'desincorporacion.fecha_movimiento_picker'() {
        this.actualizarFechaDesincorporacion();
    }
  },
  async mounted() {
    await this.cargarBienesParaSelector();
    this.actualizarFechaDesincorporacion();
  },
};
</script>