<template>
  <v-container>
    <v-card>
      <v-card-title>
        <span class="text-h5">Registrar Traslado de Bien</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formTraslado" v-model="validForm">
          <v-row>
            <v-col cols="12">
              <v-autocomplete
                v-model="bienSeleccionadoId" 
                :items="listaBienesDelStore" 
                item-title="displayText" 
                item-value="id"
                label="Seleccionar Bien a Trasladar (que no esté desincorporado)" 
                placeholder="Escriba para buscar código o descripción..."
                :rules="[rules.required]"
                outlined
                dense
                @update:model-value="alSeleccionarBien" 
                :loading="isLoadingStores"
              >
                 <!-- Slot de item personalizado si se quiere mostrar más detalle en la lista desplegable -->
                 <!-- <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props" :title="null">
                    <div>
                      <v-list-item-title>{{ item.raw.codigo_patrimonial }} - {{ item.raw.descripcion }}</v-list-item-title>
                      <v-list-item-subtitle>Marca: {{ item.raw.marca }} | Modelo: {{ item.raw.modelo }} | Ubicación: {{ item.raw.ubicacion_fisica_especifica }}</v-list-item-subtitle>
                    </div>
                  </v-list-item>
                </template> -->
                 <!-- Slot de selección para mostrar el texto formateado una vez seleccionado -->
                 <!-- <template v-slot:selection="{ item }">
                    <span>{{ item.raw.displayText }}</span>
                </template> -->
              </v-autocomplete>
            </v-col>

            <v-col cols="12" md="6" v-if="bienSeleccionadoObjeto">
              <v-subheader>Información de Origen</v-subheader>
              <v-text-field
                :model-value="bienSeleccionadoObjeto ? bienSeleccionadoObjeto.ubicacion_fisica_especifica : 'N/A'"
                label="Ubicación Actual (Origen)"
                readonly outlined dense
              ></v-text-field>
              <v-text-field
                :model-value="bienSeleccionadoObjeto ? bienSeleccionadoObjeto.responsable_asignado_nombre : 'N/A'"
                label="Responsable Actual (Origen)"
                readonly outlined dense
              ></v-text-field>
              <v-text-field
                :model-value="listaUnidadesDelStore.find(u => u.id === traslado.unidad_origen_id)?.nombre || (bienSeleccionadoObjeto && traslado.unidad_origen_id ? 'Cargando...' : (bienSeleccionadoObjeto && !traslado.unidad_origen_id ? 'No Asignada' : 'N/A'))"
                label="Unidad Administrativa Origen"
                readonly outlined dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" :md="bienSeleccionadoObjeto ? 6 : 12">
              <v-subheader>Información de Destino</v-subheader>
              <v-menu
                ref="menuFechaTraslado"
                v-model="menuFechaTraslado"
                :close-on-content-click="false"
                transition="scale-transition" offset-y min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="traslado.fecha_movimiento_formateada"
                    label="Fecha del Traslado"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    :rules="[rules.required]" outlined dense
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="traslado.fecha_movimiento_picker" 
                  no-title locale="es-VE"
                  @update:model-value="actualizarFechaTraslado" 
                ></v-date-picker> 
              </v-menu>

              <v-select
                v-model="traslado.unidad_destino_id"
                :items="listaUnidadesDelStore"
                item-title="nombre"
                item-value="id"
                label="Nueva Unidad Administrativa (Destino)"
                :rules="[rules.required]" outlined dense
                :loading="isLoadingStores"
              ></v-select>

              <v-text-field
                v-model="traslado.responsable_nuevo_nombre"
                label="Nuevo Responsable (Destino)"
                 outlined dense
              ></v-text-field>

              <v-text-field
                v-model="traslado.ubicacion_nueva_especifica"
                label="Nueva Ubicación Física Específica (Destino)"
                :rules="[rules.required]"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12">
             <v-subheader>Justificación y Documentación</v-subheader>
              <v-textarea
                v-model="traslado.motivo_traslado" 
                label="Motivo del Traslado"
                rows="3"
                outlined
                dense
              ></v-textarea>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="traslado.numero_oficio" 
                label="Número de Oficio/Referencia del Traslado"
                outlined
                dense
              ></v-text-field>
            </v-col>
            <v-col cols="12">
              <v-textarea
                v-model="traslado.observaciones_movimiento" 
                label="Observaciones Adicionales"
                rows="2"
                outlined
                dense
              ></v-textarea>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="grey" @click="cancelar">Cancelar</v-btn>
        <v-btn color="primary" :disabled="!validForm || procesandoTraslado" :loading="procesandoTraslado" @click="registrarTrasladoLocal">
          Registrar Traslado
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
// src/views/TrasladoFormView.vue
import { useMovimientoStore } from '@/stores/movimientoStore';
import { useBienesStore } from '@/stores/bienesStore'; // Para obtener la lista de bienes
import { useUnidadAdministrativaStore } from '@/stores/unidadAdministrativaStore'; // Para unidades

// mapState y mapActions si los usas, o accede a las acciones directamente

export default {
  name: 'TrasladoFormView',
  data: () => ({
    validForm: false,
    menuFechaTraslado: false,
    procesandoTraslado: false, // Nuevo para el estado de carga del botón

    bienSeleccionadoId: null, // Solo el ID del bien
    bienSeleccionadoObjeto: null, // Para mostrar info de origen

    traslado: { // Modelo local para el formulario del movimiento
      // bien: se asignará desde bienSeleccionadoId
      tipo_movimiento: 'TRASLADO', // Fijo para este formulario
      fecha_movimiento_picker: new Date(), // Inicializar con fecha actual para el picker
      fecha_movimiento_formateada: new Date().toLocaleDateString('es-VE', { year: 'numeric', month: '2-digit', day: '2-digit'}),

      unidad_origen_id: null, // ID de la unidad de origen
      unidad_destino_id: null, // ID de la unidad de destino

      responsable_anterior_nombre: '', // Se podría autocompletar al seleccionar el bien
      responsable_nuevo_nombre: '',

      // ubicacion_anterior_especifica: '', // Se podría autocompletar
      ubicacion_nueva_especifica: '', // Nueva ubicación física

      motivo_traslado: '', // Este campo se usará para motivo_desincorporacion en el modelo MovimientoBien
      numero_oficio: '', // Este campo se usará para numero_oficio_referencia
      observaciones_movimiento: '', // Para observaciones_movimiento
      // archivo_adjunto: null, // Manejo de archivos es más complejo, lo omitimos por ahora
    },
    rules: {
      required: value => !!value || 'Este campo es requerido.',
    },
  }),
  computed: {
    // Usar mapState si prefieres
    listaBienesDelStore() {
      const bienesStore = useBienesStore();
      // Formatear para v-autocomplete si es necesario, incluyendo estado actual
      return bienesStore.listaBienes
          .filter(b => b.estado_bien !== 'DESINCORPORADO') // No trasladar bienes desincorporados
          .map(bien => ({
              ...bien,
              displayText: `${bien.codigo_patrimonial} - ${bien.descripcion} (Actual: ${bien.ubicacion_fisica_especifica || 'N/A'})`
          }));
    },
    listaUnidadesDelStore() {
      const unidadAdminStore = useUnidadAdministrativaStore();
      return unidadAdminStore.unidades.filter(u => u.activa); // Solo unidades activas
    },
    isLoadingStores() {
        const bienesStore = useBienesStore();
        const unidadAdminStore = useUnidadAdministrativaStore();
        return bienesStore.isLoading || unidadAdminStore.isLoading;
    }
  },
  methods: {
    // ...mapActions(useMovimientoStore, ['registrarMovimiento']), // Si usas mapActions

    async cargarDependencias() {
        this.procesandoTraslado = true; // Usar como loading general
        const bienesStore = useBienesStore();
        const unidadAdminStore = useUnidadAdministrativaStore();
        try {
            // Cargar ambas listas en paralelo
            await Promise.all([
                bienesStore.fetchBienes(),
                unidadAdminStore.fetchUnidades() 
            ]);
        } catch (error) {
            this.$emit('show-snackbar', { message: 'Error al cargar datos necesarios para traslados.', color: 'error' });
        } finally {
            this.procesandoTraslado = false;
        }
    },

    async alSeleccionarBien(bienId) {
      this.bienSeleccionadoId = bienId;
      if (bienId) {
        const bienesStore = useBienesStore();
        this.bienSeleccionadoObjeto = bienesStore.listaBienes.find(b => b.id === bienId);
        
        console.log('Bien seleccionado (objeto completo):', JSON.parse(JSON.stringify(this.bienSeleccionadoObjeto)));

        if (this.bienSeleccionadoObjeto) {
          this.traslado.responsable_anterior_nombre = this.bienSeleccionadoObjeto.responsable_asignado_nombre || '';
          
          if (this.bienSeleccionadoObjeto.hasOwnProperty('unidad_administrativa_actual')) {
              if (typeof this.bienSeleccionadoObjeto.unidad_administrativa_actual === 'object' && this.bienSeleccionadoObjeto.unidad_administrativa_actual !== null) {
                  this.traslado.unidad_origen_id = this.bienSeleccionadoObjeto.unidad_administrativa_actual.id;
                  console.log('Unidad de Origen ID (desde objeto anidado):', this.traslado.unidad_origen_id);
              } else {
                  this.traslado.unidad_origen_id = this.bienSeleccionadoObjeto.unidad_administrativa_actual;
                  console.log('Unidad de Origen ID (directo o null):', this.traslado.unidad_origen_id);
              }
          } else {
              console.warn('El bien seleccionado NO tiene la propiedad "unidad_administrativa_actual".');
              this.traslado.unidad_origen_id = null;
          }

          // Validar que se haya obtenido la unidad de origen y mostrar advertencia si no
          if (!this.traslado.unidad_origen_id) {
              console.warn("El bien seleccionado no tiene una unidad administrativa actual asignada o la propiedad no se encontró.");
              this.$emit('show-snackbar', { message: 'Advertencia: El bien seleccionado no tiene una unidad de origen clara. Verifique sus datos.', color: 'warning', timeout: 5000 });
          }

        } else {
          console.warn('Bien no encontrado en la lista del store con ID:', bienId);
          this.bienSeleccionadoObjeto = null; 
          this.traslado.responsable_anterior_nombre = '';
          this.traslado.unidad_origen_id = null;
        }
      } else {
        this.bienSeleccionadoObjeto = null;
        this.traslado.responsable_anterior_nombre = '';
        this.traslado.unidad_origen_id = null;
      }
    },

    actualizarFechaTraslado() {
      if (this.traslado.fecha_movimiento_picker) {
        const d = new Date(this.traslado.fecha_movimiento_picker);
        this.traslado.fecha_movimiento_formateada = d.toLocaleDateString('es-VE', {
          year: 'numeric', month: '2-digit', day: '2-digit'
        });
      } else {
        this.traslado.fecha_movimiento_formateada = null;
      }
      this.menuFechaTraslado = false;
    },

    async registrarTrasladoLocal() {
      const { valid } = await this.$refs.formTraslado.validate();
      if (!valid) {
        this.$emit('show-snackbar', { message: 'Formulario inválido. Revise los campos.', color: 'error' });
        return;
      }

      if (!this.bienSeleccionadoId) {
        this.$emit('show-snackbar', { message: 'Debe seleccionar un bien a trasladar.', color: 'warning' });
        return;
      }

      // Advertencia si no hay unidad de origen, pero no bloquea si se decide permitir traslados sin origen conocido (raro)
      if (!this.traslado.unidad_origen_id) {
        this.$emit('show-snackbar', { 
            message: 'Advertencia: La unidad de origen del bien no está definida. El traslado se registrará sin ella si procede.',
            color: 'warning',
            timeout: 6000
        });
        // Si es mandatorio tener unidad de origen, descomentar el bloqueo:
        // this.procesandoTraslado = false;
        // return;
      }

      this.procesandoTraslado = true;
      const movimientoStore = useMovimientoStore();

      const payload = {
        bien: this.bienSeleccionadoId, 
        tipo_movimiento: 'TRASLADO',
        fecha_movimiento: this.traslado.fecha_movimiento_picker 
                            ? new Date(this.traslado.fecha_movimiento_picker).toISOString()
                            : new Date().toISOString(),
        unidad_origen: this.traslado.unidad_origen_id, // Este ahora debería tener un valor si el bien lo tiene
        unidad_destino: this.traslado.unidad_destino_id, 
        responsable_anterior_nombre: this.traslado.responsable_anterior_nombre,
        responsable_nuevo_nombre: this.traslado.responsable_nuevo_nombre,
        ubicacion_nueva_especifica: this.traslado.ubicacion_nueva_especifica,
        motivo_desincorporacion: this.traslado.motivo_traslado, 
        numero_oficio_referencia: this.traslado.numero_oficio,
        observaciones_movimiento: this.traslado.observaciones_movimiento,
      };

      // Comentamos la validación bloqueante anterior, ya que la advertencia se maneja arriba
      // y la lógica de si se permite o no un traslado sin unidad de origen puede ser más compleja
      // o manejada por el backend.
      /*
      if (!payload.unidad_origen) {
          this.$emit('show-snackbar', { message: 'No se pudo determinar la unidad de origen del bien seleccionado. Verifique que el bien tenga una unidad asignada.', color: 'error' });
          this.procesandoTraslado = false;
          return;
      }
      */

      try {
        await movimientoStore.registrarMovimiento(payload);
        this.$emit('show-snackbar', { 
          message: `Traslado del bien "${this.bienSeleccionadoObjeto?.descripcion || 'seleccionado'}" registrado exitosamente.`,
          color: 'success' 
        });

        const bienesStore = useBienesStore();
        await bienesStore.fetchBienes();

        this.resetForm();
        // this.$router.push('/bienes'); 
      } catch (error) {
        this.$emit('show-snackbar', { 
          message: movimientoStore.getError || 'Error al registrar el traslado.', 
          color: 'error' 
        });
      } finally {
        this.procesandoTraslado = false;
      }
    },

    resetForm() {
      this.bienSeleccionadoId = null;
      this.bienSeleccionadoObjeto = null;
      this.traslado = {
        tipo_movimiento: 'TRASLADO',
        fecha_movimiento_picker: new Date(),
        fecha_movimiento_formateada: new Date().toLocaleDateString('es-VE', { year: 'numeric', month: '2-digit', day: '2-digit'}),
        unidad_origen_id: null,
        unidad_destino_id: null,
        responsable_anterior_nombre: '',
        responsable_nuevo_nombre: '',
        ubicacion_nueva_especifica: '',
        motivo_traslado: '',
        numero_oficio: '',
        observaciones_movimiento: '',
      };
      if (this.$refs.formTraslado) {
        this.$refs.formTraslado.resetValidation();
      }
    },
    cancelar() {
      this.resetForm();
      this.$router.push('/'); 
    },
  },
  async mounted() {
    await this.cargarDependencias();
    this.actualizarFechaTraslado();
  },
   watch: {
    'traslado.fecha_movimiento_picker'() {
        this.actualizarFechaTraslado();
    }
  }
};
</script>

<style scoped>
/* Estilos específicos si son necesarios */
</style>