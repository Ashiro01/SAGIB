<template>
  <v-container>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formBien" v-model="validForm">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="bien.descripcion"
                label="Descripción del Bien"
                :rules="[rules.required, rules.minLength(5)]"
                required
                outlined
                dense
              ></v-text-field>

              <v-menu
                v-model="menuFechaAdquisicion"
                :close-on-content-click="false"
                transition="scale-transition"
                offset-y
                min-width="auto"
              >
                <template v-slot:activator="{ props }">
                  <v-text-field
                    v-model="bien.fecha_adquisicion"
                    label="Fecha de Adquisición"
                    prepend-icon="mdi-calendar"
                    readonly
                    v-bind="props"
                    outlined
                    dense
                  ></v-text-field>
                </template>
                <v-date-picker
                  v-model="bien.fecha_adquisicion_picker"
                  no-title
                  @update:model-value="actualizarFechaAdquisicion"
                  locale="es-VE"
                ></v-date-picker>
              </v-menu>

              <v-text-field
                v-model="bien.cantidad"
                label="Cantidad"
                type="number"
                :rules="[rules.required, rules.positiveNumber]"
                required
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.marca"
                label="Marca"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.modelo"
                label="Modelo"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.serial"
                label="Serial del Fabricante"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.codigo_anterior"
                label="Código de Inventario Anterior (si aplica)"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.n_orden_compra_factura"
                label="N° Orden de Compra o Factura"
                outlined
                dense
              ></v-text-field>

              <v-select
                v-model="bien.proveedor_id"
                :items="listaProveedores"
                item-value="id"
                item-title="title"
                label="Proveedor"
                outlined
                dense
                :loading="cargandoProveedores"
                clearable
                :hint="proveedorHint"
                persistent-hint
              >
                <template v-slot:item="{ props, item }">
                  <v-list-item v-bind="props">
                    <v-list-item-subtitle v-if="item.raw.rif">
                      RIF: {{ item.raw.rif }}
                    </v-list-item-subtitle>
                    <v-list-item-subtitle v-if="item.raw.contacto_principal_nombre">
                      Contacto: {{ item.raw.contacto_principal_nombre }}
                    </v-list-item-subtitle>
                  </v-list-item>
                </template>
                <template v-slot:selection="{ item }">
                  <span>{{ item.raw.nombre_proveedor }}</span>
                  <span v-if="item.raw.rif" class="text-caption text-grey-darken-1 ml-2">
                    ({{ item.raw.rif }})
                  </span>
                </template>
              </v-select>

              <v-select
                v-model="bien.motivo_adquisicion"
                :items="motivosAdquisicion"
                item-title="title"
                item-value="value"
                label="Motivo de Adquisición"
                outlined
                dense
                :rules="[rules.required]"
                required
              ></v-select>

              <v-text-field
                v-model="bien.valor_unitario_bs"
                label="Valor Unitario Bs."
                type="number"
                prefix="Bs."
                :rules="[rules.required, rules.positiveNumber]"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.valor_unitario_usd"
                label="Valor Unitario $"
                type="number"
                prefix="$"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-select
                v-model="bien.unidad_administrativa_actual_id"
                :items="listaUnidadesAdministrativas"
                item-title="nombre"
                item-value="id"
                label="Unidad Administrativa Actual"
                :rules="[rules.required]"
                required
                outlined
                dense
                :loading="cargandoUnidades"
                clearable
                @update:model-value="actualizarCodigoPatrimonial"
              ></v-select>

              <v-text-field
                v-model="bien.codigo_patrimonial"
                label="Código Patrimonial"
                :rules="[rules.codigoPatrimonial]"
                required
                outlined
                dense
                :hint="codigoPatrimonialHint"
                persistent-hint
                :placeholder="codigoPatrimonialPlaceholder"
                :append-inner-icon="bien.unidad_administrativa_actual_id ? 'mdi-numeric' : ''"
                @click:append-inner="generarSiguienteCodigo"
                :disabled="!bien.unidad_administrativa_actual_id"
              >
                <template v-slot:append-inner>
                  <v-tooltip
                    v-if="bien.unidad_administrativa_actual_id"
                    text="Generar siguiente número automáticamente"
                    location="top"
                  >
                    <template v-slot:activator="{ props }">
                      <v-icon
                        v-bind="props"
                        @click="generarSiguienteCodigo"
                        color="primary"
                        class="cursor-pointer"
                      >
                        mdi-numeric
                      </v-icon>
                    </template>
                  </v-tooltip>
                </template>
              </v-text-field>

              <v-text-field
                v-model="bien.ubicacion_fisica_especifica"
                label="Ubicación Física Específica (ej: Oficina 3, Almacén B)"
                :rules="[rules.required]"
                required
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.responsable_asignado_nombre"
                label="Nombre del Responsable Asignado"
                :rules="[rules.required]"
                required
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="bien.responsable_asignado_cargo"
                label="Cargo del Responsable Asignado"
                outlined
                dense
              ></v-text-field>

              <v-select
                v-model="bien.estado_bien"
                :items="['NUEVO', 'BUENO', 'REGULAR', 'MALO', 'EN_REPARACION', 'OBSOLETO', 'DESINCORPORADO']"
                label="Estado del Bien"
                :rules="[rules.required]"
                required
                outlined
                dense
              ></v-select>

              <v-textarea
                v-model="bien.observaciones"
                label="Observaciones"
                outlined
                dense
                rows="3"
              ></v-textarea>

              <v-divider class="my-4"></v-divider>
              <v-subheader>Datos para Depreciación</v-subheader>

              <v-text-field
                  v-model="bien.vida_util_estimada_anios"
                  label="Vida Útil Estimada"
                  type="number"
                  suffix="años"
                  outlined
                  dense
                  clearable
              ></v-text-field>

              <v-text-field
                  v-model="bien.valor_residual"
                  label="Valor Residual (Salvamento)"
                  type="number"
                  prefix="Bs."
                  outlined
                  dense
              ></v-text-field>

              <v-select
                  v-model="bien.metodo_depreciacion"
                  :items="metodosDepreciacion"
                  item-title="title"
                  item-value="value"
                  label="Método de Depreciación"
                  outlined
                  dense
                  clearable
              ></v-select>

              <v-select
                v-model="bien.categoria"
                :items="listaCategorias"
                item-title="nombre"
                item-value="id"
                label="Categoría del Bien"
                :rules="[rules.required]"
                required
                outlined
                dense
                :loading="cargandoCatalogos"
                clearable
              ></v-select>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelar">Cancelar</v-btn>
        <v-btn color="blue darken-1" :disabled="!validForm || guardando" :loading="guardando" @click="guardarBien">Guardar Bien</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import { useBienesStore } from '@/stores/bienesStore';
import { useUnidadAdministrativaStore } from '@/stores/unidadAdministrativaStore';
import { useCategoriaStore } from '@/stores/categoriaStore';
import { useProveedorStore } from '@/stores/proveedorStore';

export default {
  name: 'BienFormView',
  data() {
    return {
      isEditing: false,
      validForm: false,
      guardando: false,
      bien: {
        id: null,
        codigo_anterior: '',
        codigo_patrimonial: '',
        descripcion: '',
        marca: '',
        modelo: '',
        serial: '',
        cantidad: 1,
        fecha_adquisicion: null,
        fecha_adquisicion_picker: null,
        n_orden_compra_factura: '',
        proveedor: '',
        valor_unitario_bs: null,
        valor_unitario_usd: null,
        unidad_administrativa_actual_id: null,
        ubicacion_fisica_especifica: '',
        responsable_asignado_nombre: '',
        responsable_asignado_cargo: '',
        estado_bien: 'NUEVO',
        observaciones: '',
        // --- Propiedades Nuevas ---
        vida_util_estimada_anios: null,
        valor_residual: 0.00,
        metodo_depreciacion: null,
        // --- NUEVO: Categoría ---
        categoria: null, // <-- ID de la categoría
      },
      // --- NUEVA PROPIEDAD PARA EL SELECTOR ---
      metodosDepreciacion: [
        { title: 'Línea Recta', value: 'LINEA_RECTA' },
        { title: 'Saldo Decreciente', value: 'SALDO_DECRECIENTE' },
      ],
      motivosAdquisicion: [
        { title: 'Compra Directa', value: 'COMPRA_DIRECTA' },
        { title: 'Licitación Pública', value: 'LICITACION' },
        { title: 'Dación en Pago', value: 'DACION_PAGO' },
        { title: 'Donación', value: 'DONACION' },
        { title: 'Transferencia de Otros Organismos', value: 'TRANSFERENCIA' },
        { title: 'Construcción Propia', value: 'CONSTRUCCION_PROPIA' },
        { title: 'Recuperación de Bienes', value: 'RECUPERACION' },
        { title: 'Comodato', value: 'COMODATO' },
        { title: 'Arrendamiento con Opción de Compra', value: 'ARRENDAMIENTO' },
        { title: 'Herencia o Legado', value: 'HERENCIA' },
        { title: 'Otro', value: 'OTRO' },
      ],
      rules: {
        required: value => !!value || 'Este campo es requerido.',
        positiveNumber: value => (parseFloat(value) > 0) || 'Debe ser un número positivo.',
        minLength: min => value => (value && value.length >= min) || `Mínimo ${min} caracteres.`,
        codigoPatrimonial: value => {
          if (!value) return 'El código patrimonial es requerido.';
          if (!value.includes('-')) return 'El código debe tener el formato: CÓDIGO-NÚMERO';
          const partes = value.split('-');
          if (partes.length < 2) return 'El código debe tener el formato: CÓDIGO-NÚMERO';
          if (!partes[1] || partes[1].trim() === '') return 'Debe completar el número del bien.';
          return true;
        },
      },
      menuFechaAdquisicion: false,
      cargandoUnidades: false,
    };
  },
  computed: {
    formTitle() {
      return this.isEditing ? 'Editar Bien' : 'Registrar Nuevo Bien';
    },
    listaUnidadesAdministrativas() {
      const unidadAdminStore = useUnidadAdministrativaStore();
      return unidadAdminStore.unidades.filter(u => u.activa);
    },
    listaCategorias() {
      const categoriaStore = useCategoriaStore();
      return categoriaStore.listaCategorias;
    },
    cargandoCatalogos() {
      const unidadAdminStore = useUnidadAdministrativaStore();
      const categoriaStore = useCategoriaStore();
      return unidadAdminStore.isLoading || categoriaStore.isLoading;
    },
    codigoPatrimonialHint() {
      if (this.bien.unidad_administrativa_actual_id) {
        const unidadSeleccionada = this.listaUnidadesAdministrativas.find(
          u => u.id === this.bien.unidad_administrativa_actual_id
        );
        if (unidadSeleccionada) {
          return `Código de la unidad: ${unidadSeleccionada.codigo}. Complete el número del bien.`;
        }
      }
      return 'Seleccione una unidad administrativa primero';
    },
    codigoPatrimonialPlaceholder() {
      if (this.bien.unidad_administrativa_actual_id) {
        const unidadSeleccionada = this.listaUnidadesAdministrativas.find(
          u => u.id === this.bien.unidad_administrativa_actual_id
        );
        if (unidadSeleccionada) {
          return `${unidadSeleccionada.codigo}-`;
        }
      }
      return 'Ej: IPSFA-001';
    },
    listaProveedores() {
      const proveedorStore = useProveedorStore();
      return proveedorStore.listaProveedores.filter(p => p.activo).map(proveedor => ({
        ...proveedor,
        title: proveedor.nombre_proveedor // Para que Vuetify use este campo como título
      }));
    },
    cargandoProveedores() {
      const proveedorStore = useProveedorStore();
      return proveedorStore.isLoading;
    },
    proveedorHint() {
      return 'Seleccione un proveedor registrado. Se mostrará el nombre, RIF y contacto.';
    }
  },
  methods: {
    async cargarUnidadesParaSelector() {
      this.cargandoUnidades = true;
      const unidadAdminStore = useUnidadAdministrativaStore();
      try {
        await unidadAdminStore.fetchUnidades();
      } catch (error) {
        this.$emit('show-snackbar', { message: 'Error al cargar unidades administrativas para el selector.', color: 'error' });
      } finally {
        this.cargandoUnidades = false;
      }
    },
    async cargarProveedoresParaSelector() {
      const proveedorStore = useProveedorStore();
      try {
        await proveedorStore.fetchProveedores();
      } catch (error) {
        this.$emit('show-snackbar', { message: 'Error al cargar proveedores para el selector.', color: 'error' });
      }
    },
    async cargarBienParaEditar(bienId) {
      const bienesStore = useBienesStore();
      this.guardando = true;
      try {
        const bienDesdeAPI = await bienesStore.fetchBienById(bienId);
        if (bienDesdeAPI) {
          this.bien.id = bienDesdeAPI.id;
          this.bien.codigo_anterior = bienDesdeAPI.codigo_anterior;
          this.bien.codigo_patrimonial = bienDesdeAPI.codigo_patrimonial;
          this.bien.descripcion = bienDesdeAPI.descripcion;
          this.bien.marca = bienDesdeAPI.marca;
          this.bien.modelo = bienDesdeAPI.modelo;
          this.bien.serial = bienDesdeAPI.serial;
          this.bien.cantidad = bienDesdeAPI.cantidad;

          if (bienDesdeAPI.fecha_adquisicion) {
            this.bien.fecha_adquisicion_picker = bienDesdeAPI.fecha_adquisicion;
            this.bien.fecha_adquisicion = new Date(bienDesdeAPI.fecha_adquisicion + 'T00:00:00').toLocaleDateString('es-VE');
          } else {
            this.bien.fecha_adquisicion_picker = null;
            this.bien.fecha_adquisicion = null;
          }
          this.bien.n_orden_compra_factura = bienDesdeAPI.n_orden_compra_factura;
          this.bien.proveedor_id = bienDesdeAPI.proveedor;
          this.bien.motivo_adquisicion = bienDesdeAPI.motivo_adquisicion || 'COMPRA_DIRECTA';
          this.bien.valor_unitario_bs = bienDesdeAPI.valor_unitario_bs;
          this.bien.valor_unitario_usd = bienDesdeAPI.valor_unitario_usd;

          this.bien.unidad_administrativa_actual_id = bienDesdeAPI.unidad_administrativa_actual;
          this.bien.ubicacion_fisica_especifica = bienDesdeAPI.ubicacion_fisica_especifica;
          this.bien.responsable_asignado_nombre = bienDesdeAPI.responsable_asignado_nombre;
          this.bien.responsable_asignado_cargo = bienDesdeAPI.responsable_asignado_cargo;

          this.bien.estado_bien = bienDesdeAPI.estado_bien;
          this.bien.observaciones = bienDesdeAPI.observaciones;

          // --- Añadir mapeo para los nuevos campos ---
          this.bien.vida_util_estimada_anios = bienDesdeAPI.vida_util_estimada_anios;
          this.bien.valor_residual = bienDesdeAPI.valor_residual;
          this.bien.metodo_depreciacion = bienDesdeAPI.metodo_depreciacion;
          // --- NUEVO: Cargar categoria_id ---
          this.bien.categoria = bienDesdeAPI.categoria || null;
          this.$emit('show-snackbar', { message: 'Datos del bien cargados para edición.', color: 'info' });
        } else {
          throw new Error('Bien no encontrado en la API.');
        }
      } catch (error) {
        console.error("Error al cargar bien para editar:", error);
        this.$emit('show-snackbar', { message: error.message || 'Error al cargar datos del bien.', color: 'error' });
        this.$router.push('/bienes');
      } finally {
        this.guardando = false;
      }
    },
    async guardarBien() {
      const { valid } = await this.$refs.formBien.validate();
      if (!valid) {
        this.$emit('show-snackbar', { message: 'Formulario inválido. Revise los campos.', color: 'error' });
        return;
      }
      this.guardando = true;
      const bienesStore = useBienesStore();
      let payload = {
        codigo_anterior: this.bien.codigo_anterior || null,
        codigo_patrimonial: this.bien.codigo_patrimonial,
        descripcion: this.bien.descripcion,
        marca: this.bien.marca || null,
        modelo: this.bien.modelo || null,
        serial: this.bien.serial || null,
        cantidad: parseInt(this.bien.cantidad) || 1,
        fecha_adquisicion: this.bien.fecha_adquisicion_picker 
                            ? new Date(this.bien.fecha_adquisicion_picker).toISOString().split('T')[0] 
                            : null,
        n_orden_compra_factura: this.bien.n_orden_compra_factura || null,
        proveedor: this.bien.proveedor_id,
        motivo_adquisicion: this.bien.motivo_adquisicion,
        valor_unitario_bs: parseFloat(this.bien.valor_unitario_bs) || 0,
        valor_unitario_usd: this.bien.valor_unitario_usd ? parseFloat(this.bien.valor_unitario_usd) : null,

        unidad_administrativa_actual: this.bien.unidad_administrativa_actual_id,
        ubicacion_fisica_especifica: this.bien.ubicacion_fisica_especifica,
        responsable_asignado_nombre: this.bien.responsable_asignado_nombre || null,
        responsable_asignado_cargo: this.bien.responsable_asignado_cargo || null,

        estado_bien: this.bien.estado_bien,
        observaciones: this.bien.observaciones || null,
        // --- Añadir los nuevos campos al payload ---
        vida_util_estimada_anios: this.bien.vida_util_estimada_anios ? parseInt(this.bien.vida_util_estimada_anios) : null,
        valor_residual: this.bien.valor_residual ? parseFloat(this.bien.valor_residual) : 0.00,
        metodo_depreciacion: this.bien.metodo_depreciacion || null,
        // --- NUEVO: Categoría ---
        categoria: this.bien.categoria,
      };

      try {
        if (this.isEditing) {
          const bienActualizado = await bienesStore.actualizarBien(this.bien.id, payload);
          this.$emit('show-snackbar', { 
            message: `Bien "${bienActualizado.descripcion}" actualizado exitosamente.`, 
            color: 'success' 
          });
          this.$router.push('/bienes'); 
        } else {
          const nuevoBien = await bienesStore.crearBien(payload);
          this.$emit('show-snackbar', { 
            message: `Bien "${nuevoBien.descripcion}" registrado con ID: ${nuevoBien.id}.`, 
            color: 'success' 
          });
          this.$router.push('/bienes');
        }
      } catch (error) {
        console.error('Error al guardar el bien:', error);
        this.$emit('show-snackbar', { 
          message: (error.response && error.response.data && typeof error.response.data === 'object' ? bienesStore.formatApiErrors(error.response.data) : error.message) || 'Ocurrió un error al guardar.', 
          color: 'error' 
        });
      } finally {
        this.guardando = false;
      }
    },
    cancelar() {
      this.$router.push('/bienes');
    },
    resetForm() {
      this.isEditing = false;
      this.bien = {
        id: null,
        codigo_anterior: '',
        codigo_patrimonial: '',
        descripcion: '',
        marca: '',
        modelo: '',
        serial: '',
        cantidad: 1,
        fecha_adquisicion: null,
        fecha_adquisicion_picker: null,
        n_orden_compra_factura: '',
        proveedor: '',
        valor_unitario_bs: null,
        valor_unitario_usd: null,
        unidad_administrativa_actual_id: null,
        ubicacion_fisica_especifica: '',
        responsable_asignado_nombre: '',
        responsable_asignado_cargo: '',
        estado_bien: 'NUEVO',
        observaciones: '',
        // --- Añadir reset para los nuevos campos ---
        vida_util_estimada_anios: null,
        valor_residual: 0.00,
        metodo_depreciacion: null,
        // --- NUEVO: Categoría ---
        categoria: null,
        // --- NUEVO: Proveedor ---
        proveedor_id: null,
        // --- NUEVO: Motivo de Adquisición ---
        motivo_adquisicion: 'COMPRA_DIRECTA',
      };
      if (this.$refs.formBien) {
        this.$refs.formBien.reset();
      }
    },
    actualizarFechaAdquisicion(fecha) {
      if (fecha) {
        this.bien.fecha_adquisicion = new Date(fecha).toLocaleDateString('es-VE');
      } else {
        this.bien.fecha_adquisicion = null;
      }
    },
    actualizarCodigoPatrimonial(unidadId) {
      if (unidadId) {
        const unidadSeleccionada = this.listaUnidadesAdministrativas.find(u => u.id === unidadId);
        if (unidadSeleccionada) {
          // Si ya hay un código patrimonial, mantener solo la parte numérica
          const codigoActual = this.bien.codigo_patrimonial;
          if (codigoActual && codigoActual.includes('-')) {
            const partes = codigoActual.split('-');
            if (partes.length > 1) {
              // Mantener solo la parte numérica después del último guión
              const numero = partes[partes.length - 1];
              this.bien.codigo_patrimonial = `${unidadSeleccionada.codigo}-${numero}`;
            } else {
              this.bien.codigo_patrimonial = `${unidadSeleccionada.codigo}-`;
            }
          } else {
            // Si no hay código o no tiene formato, solo agregar el código de la unidad
            this.bien.codigo_patrimonial = `${unidadSeleccionada.codigo}-`;
          }
        }
      } else {
        // Si se deselecciona la unidad, limpiar el código patrimonial
        this.bien.codigo_patrimonial = '';
      }
    },
    async generarSiguienteCodigo() {
      if (!this.bien.unidad_administrativa_actual_id) {
        this.$emit('show-snackbar', { 
          message: 'Debe seleccionar una unidad administrativa primero.', 
          color: 'warning' 
        });
        return;
      }

      const unidadSeleccionada = this.listaUnidadesAdministrativas.find(
        u => u.id === this.bien.unidad_administrativa_actual_id
      );
      
      if (!unidadSeleccionada) {
        this.$emit('show-snackbar', { 
          message: 'Error al obtener información de la unidad administrativa.', 
          color: 'error' 
        });
        return;
      }

      try {
        // Obtener el siguiente número disponible para esta unidad
        const bienesStore = useBienesStore();
        const siguienteNumero = await bienesStore.obtenerSiguienteCodigoPatrimonial(unidadSeleccionada.codigo);
        
        this.bien.codigo_patrimonial = `${unidadSeleccionada.codigo}-${siguienteNumero}`;
        
        this.$emit('show-snackbar', { 
          message: `Código patrimonial generado: ${this.bien.codigo_patrimonial}`, 
          color: 'success' 
        });
      } catch (error) {
        console.error('Error al generar código patrimonial:', error);
        this.$emit('show-snackbar', { 
          message: 'Error al generar el código patrimonial automáticamente.', 
          color: 'error' 
        });
      }
    },
  },
  async created() {
    const unidadAdminStore = useUnidadAdministrativaStore();
    const categoriaStore = useCategoriaStore();
    const proveedorStore = useProveedorStore();
    try {
      await Promise.all([
        unidadAdminStore.fetchUnidades(),
        categoriaStore.fetchCategorias(),
        proveedorStore.fetchProveedores()
      ]);
    } catch (error) {
      this.$emit('show-snackbar', { message: 'Error al cargar catálogos necesarios.', color: 'error' });
    }
    const id = this.$route.params.id;
    if (id) {
      this.isEditing = true;
      await this.cargarBienParaEditar(parseInt(id));
    }
  },
};
</script>

<style scoped>
/* Estilos específicos para esta vista */
.cursor-pointer {
  cursor: pointer;
}
</style>