<template>
  <v-container>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formProveedor" v-model="validForm">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="proveedor.nombre_proveedor"
                label="Nombre del Proveedor"
                :rules="[rules.required]"
                required
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="proveedor.rif"
                label="RIF del Proveedor"
                :rules="[rules.required]"
                placeholder="Ej: J-12345678-9"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="proveedor.contacto_principal_nombre"
                label="Nombre del Contacto Principal"
                outlined
                dense
              ></v-text-field>

              <v-text-field
                v-model="proveedor.contacto_principal_email"
                label="Email de Contacto"
                type="email"
                :rules="[rules.email]"
                outlined
                dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" md="6">
              <v-text-field
                v-model="proveedor.contacto_principal_telefono"
                label="Teléfono de Contacto"
                outlined
                dense
              ></v-text-field>

              <v-textarea
                v-model="proveedor.direccion_fiscal"
                label="Dirección Fiscal"
                rows="4"
                outlined
                dense
              ></v-textarea>

              <v-switch
                v-model="proveedor.activo"
                label="Proveedor Activo"
                color="success"
                class="mt-4"
              ></v-switch>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelar">Cancelar</v-btn>
        <v-btn color="blue darken-1" :disabled="!validForm" @click="guardarProveedor">Guardar</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import { useProveedorStore } from '@/stores/proveedorStore';
import { mapActions, mapState } from 'pinia';

export default {
  name: 'ProveedorFormView',
  data: () => ({
    isEditing: false,
    validForm: false,
    proveedor: {
      id: null,
      nombre_proveedor: '',
      rif: '',
      direccion_fiscal: '',
      contacto_principal_nombre: '',
      contacto_principal_email: '',
      contacto_principal_telefono: '',
      activo: true,
    },
    rules: {
      required: value => !!value || 'Este campo es requerido.',
      email: value => {
        if (!value) return true; // Permite campo vacío si no es requerido
        const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return pattern.test(value) || 'Email inválido.';
      },
    },
    guardando: false,
  }),
  computed: {
    formTitle() {
      return this.isEditing ? 'Editar Proveedor' : 'Registrar Nuevo Proveedor';
    },
    ...mapState(useProveedorStore, ['getError', 'isLoading', 'getProveedorActual'])
  },
  methods: {
    ...mapActions(useProveedorStore, ['crearProveedor', 'actualizarProveedor', 'fetchProveedorById']),
    cancelar() {
      this.$router.push('/proveedores');
    },
    async cargarProveedorParaEditar(id) {
      this.guardando = true;
      try {
        const prov = await this.fetchProveedorById(id);
        if (prov) {
          this.proveedor = {
            id: prov.id,
            nombre_proveedor: prov.nombre_proveedor,
            rif: prov.rif,
            direccion_fiscal: prov.direccion_fiscal,
            contacto_principal_nombre: prov.contacto_principal_nombre,
            contacto_principal_email: prov.contacto_principal_email,
            contacto_principal_telefono: prov.contacto_principal_telefono,
            activo: prov.activo,
          };
        }
      } catch (error) {
        this.$emit('show-snackbar', { message: this.getError || 'Error al cargar datos del proveedor.', color: 'error' });
        this.$router.push('/proveedores');
      } finally {
        this.guardando = false;
      }
    },
    async guardarProveedor() {
      if (!this.$refs.formProveedor.validate()) return;
      this.guardando = true;
      const payload = {
        nombre_proveedor: this.proveedor.nombre_proveedor,
        rif: this.proveedor.rif,
        direccion_fiscal: this.proveedor.direccion_fiscal,
        contacto_principal_nombre: this.proveedor.contacto_principal_nombre,
        contacto_principal_email: this.proveedor.contacto_principal_email,
        contacto_principal_telefono: this.proveedor.contacto_principal_telefono,
        activo: this.proveedor.activo,
      };
      try {
        if (this.isEditing) {
          await this.actualizarProveedor(this.proveedor.id, payload);
          this.$emit('show-snackbar', { message: 'Proveedor actualizado correctamente.', color: 'success' });
        } else {
          await this.crearProveedor(payload);
          this.$emit('show-snackbar', { message: 'Proveedor creado correctamente.', color: 'success' });
        }
        this.$router.push('/proveedores');
      } catch (error) {
        this.$emit('show-snackbar', {
          message: this.getError || 'Error al guardar el proveedor.',
          color: 'error',
        });
      } finally {
        this.guardando = false;
      }
    },
    resetForm() {
      this.isEditing = false;
      this.proveedor = {
        id: null,
        nombre_proveedor: '',
        rif: '',
        direccion_fiscal: '',
        contacto_principal_nombre: '',
        contacto_principal_email: '',
        contacto_principal_telefono: '',
        activo: true,
      };
      if (this.$refs.formProveedor) this.$refs.formProveedor.resetValidation();
    }
  },
  created() {
    const id = this.$route.params.id;
    if (id) {
      this.isEditing = true;
      this.cargarProveedorParaEditar(parseInt(id));
    } else {
      this.isEditing = false;
      this.resetForm();
    }
  },
  watch: {
    '$route.params.id': function(newId) {
      if (this.$route.name === 'editarProveedor' && newId) {
        this.isEditing = true;
        this.cargarProveedorParaEditar(parseInt(newId));
      } else if (this.$route.name === 'registrarProveedor') {
        this.isEditing = false;
        this.resetForm();
      }
    }
  }
};
</script>