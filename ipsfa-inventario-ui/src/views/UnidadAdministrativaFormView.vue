<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card>
          <v-card-title>
            <span class="text-h5">{{ formTitle }}</span>
          </v-card-title>
          <v-card-text>
            <v-form ref="formUnidad" v-model="validForm">
              <v-row>
                <v-col cols="12" sm="4">
                  <v-text-field
                    v-model="unidad.codigo"
                    label="Código de Unidad"
                    :rules="[rules.required, rules.codigoMax]"
                    counter="10"
                    required outlined dense
                    :disabled="isEditing"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" sm="8">
                  <v-text-field
                    v-model="unidad.nombre"
                    label="Nombre de la Unidad"
                    :rules="[rules.required]"
                    required outlined dense
                  ></v-text-field>
                </v-col>
                <v-col cols="12">
                  <v-textarea
                    v-model="unidad.descripcion"
                    label="Descripción (Opcional)"
                    rows="3"
                    outlined dense
                  ></v-textarea>
                </v-col>
                <v-col cols="12">
                   <v-switch
                      v-model="unidad.activa"
                      :label="`Estado: ${unidad.activa ? 'Activa' : 'Inactiva'}`"
                      color="primary"
                      inset
                    ></v-switch>
                </v-col>
                </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey darken-1" text @click="cancelar">Cancelar</v-btn>
            <v-btn 
                color="primary" 
                :disabled="!validForm || guardando" 
                :loading="guardando"
                @click="guardarUnidadLocal"
            >
                Guardar Unidad
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useUnidadAdministrativaStore } from '@/stores/unidadAdministrativaStore';
import { mapActions } from 'pinia';

export default {
  name: 'UnidadAdministrativaFormView',
  data() {
    return {
      isEditing: false,
      validForm: false,
      guardando: false,
      unidad: {
        id: null,
        codigo: '',
        nombre: '',
        descripcion: '',
        activa: true, // Por defecto activa para nuevas unidades
      },
      rules: {
        required: value => !!value || 'Este campo es requerido.',
        codigoMax: value => (value && value.length <= 10) || 'Máximo 10 caracteres para el código.',
      },
    };
  },
  computed: {
    formTitle() {
      return this.isEditing ? 'Editar Unidad Administrativa' : 'Registrar Nueva Unidad';
    },
  },
  methods: {
    ...mapActions(useUnidadAdministrativaStore, ['agregarUnidad', 'actualizarUnidad']),

    async guardarUnidadLocal() {
      if (!this.$refs.formUnidad.validate()) {
         this.$emit('show-snackbar', { message: 'Por favor, corrija los errores en el formulario.', color: 'error' });
         return;
      }
      this.guardando = true;
      const store = useUnidadAdministrativaStore();
      // Prepara el payload con los nombres de campo del backend
      const payload = {
        codigo: this.unidad.codigo,
        nombre: this.unidad.nombre,
        descripcion: this.unidad.descripcion || null,
        activa: this.unidad.activa,
      };
      try {
        if (this.isEditing) {
          await store.actualizarUnidad(this.unidad.id, payload);
          this.$emit('show-snackbar', { message: `Unidad "${this.unidad.nombre}" actualizada.`, color: 'success' });
        } else {
          const unidadCreada = await store.agregarUnidad(payload);
          this.$emit('show-snackbar', { message: `Unidad "${unidadCreada.nombre}" registrada.`, color: 'success' });
        }
        this.$router.push('/unidades-administrativas');
      } catch (error) {
        this.$emit('show-snackbar', { message: store.error || 'Error al guardar la unidad.', color: 'error' });
      } finally {
        this.guardando = false;
      }
    },
    async cargarDatosParaEdicion(idUnidad) {
      const store = useUnidadAdministrativaStore();
      try {
        const unidad = await store.fetchUnidadById(idUnidad);
        this.unidad = { ...unidad };
      } catch (error) {
        this.$emit('show-snackbar', { message: 'Error: Unidad no encontrada.', color: 'error' });
        this.$router.push('/unidades-administrativas');
      }
    },
    cancelar() {
      this.$router.push('/unidades-administrativas');
    },
    resetForm() {
      this.unidad = { id: null, codigo: '', nombre: '', descripcion: '', activa: true };
      if (this.$refs.formUnidad) {
        this.$refs.formUnidad.resetValidation();
      }
    }
  },
  created() {
    const id = this.$route.params.id;
    if (id) {
      this.isEditing = true;
      this.cargarDatosParaEdicion(parseInt(id));
    } else {
      this.isEditing = false;
      this.resetForm();
    }
  },
   watch: {
    '$route.params.id': {
      immediate: true,
      handler(newId) {
        if (this.$route.name === 'editarUnidadAdministrativa' && newId) {
          this.isEditing = true;
          this.cargarDatosParaEdicion(parseInt(newId));
        } else if (this.$route.name === 'registrarUnidadAdministrativa') {
          this.isEditing = false;
          this.resetForm();
        }
      }
    }
  }
};
</script>