<template>
  <v-container>
    <v-card v-if="proveedorActual && !isLoading">
      <v-card-title>
        <span class="text-h5">Detalles del Proveedor: {{ proveedorActual.nombre_proveedor }}</span>
        <v-spacer></v-spacer>
         <v-btn color="orange darken-1" text @click="irAEditar" class="mr-2">
          <v-icon left>mdi-pencil</v-icon>
          Editar
        </v-btn>
        <v-btn color="primary" text @click="volverAlListado">
          <v-icon left>mdi-arrow-left</v-icon>
          Volver al Listado
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-list dense>
              <v-list-item>
                <v-list-item-subtitle>Nombre del Proveedor</v-list-item-subtitle>
                <v-list-item-title>{{ proveedorActual.nombre_proveedor || 'N/A' }}</v-list-item-title>
              </v-list-item>
              <v-divider inset></v-divider>
              <v-list-item>
                <v-list-item-subtitle>RIF</v-list-item-subtitle>
                <v-list-item-title>{{ proveedorActual.rif || 'N/A' }}</v-list-item-title>
              </v-list-item>
              <v-divider inset></v-divider>
              <v-list-item>
                <v-list-item-subtitle>Dirección Fiscal</v-list-item-subtitle>
                <v-list-item-title style="white-space: pre-wrap;">{{ proveedorActual.direccion_fiscal || 'N/A' }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
          <v-col cols="12" md="6">
            <v-list dense>
              <v-list-item>
                <v-list-item-subtitle>Nombre del Contacto Principal</v-list-item-subtitle>
                <v-list-item-title>{{ proveedorActual.contacto_principal_nombre || 'N/A' }}</v-list-item-title>
              </v-list-item>
              <v-divider inset></v-divider>
              <v-list-item>
                <v-list-item-subtitle>Email de Contacto</v-list-item-subtitle>
                <v-list-item-title>{{ proveedorActual.contacto_principal_email || 'N/A' }}</v-list-item-title>
              </v-list-item>
              <v-divider inset></v-divider>
              <v-list-item>
                <v-list-item-subtitle>Teléfono de Contacto</v-list-item-subtitle>
                <v-list-item-title>{{ proveedorActual.contacto_principal_telefono || 'N/A' }}</v-list-item-title>
              </v-list-item>
              <v-divider inset></v-divider>
              <v-list-item>
                <v-list-item-subtitle>Estado</v-list-item-subtitle>
                <v-list-item-title>
                  <v-chip :color="proveedorActual.activo ? 'green' : 'grey'" small dark>
                    {{ proveedorActual.activo ? 'Activo' : 'Inactivo' }}
                  </v-chip>
                </v-list-item-title>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-row v-else-if="isLoading" justify="center" align="center" style="min-height: 200px;">
      <v-col cols="12" class="text-center">
        <v-progress-circular indeterminate color="primary" size="48" />
        <div class="mt-2">Cargando proveedor...</div>
      </v-col>
    </v-row>
    <v-alert v-else type="error" prominent class="mt-5">
      No se pudo cargar la información del proveedor.
    </v-alert>
  </v-container>
</template>

<script>
import { useProveedorStore } from '@/stores/proveedorStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'ProveedorDetailView',
  props: ['id'],
  computed: {
    ...mapState(useProveedorStore, ['getError', 'isLoading', 'getProveedorActual']),
    proveedorActual() {
      return this.getProveedorActual;
    }
  },
  async created() {
    await this.cargarProveedor();
  },
  watch: {
    id: {
      immediate: false,
      handler() {
        this.cargarProveedor();
      }
    }
  },
  methods: {
    ...mapActions(useProveedorStore, ['fetchProveedorById']),
    async cargarProveedor() {
      try {
        const idNum = Number(this.id);
        if (idNum) {
          await this.fetchProveedorById(idNum);
        }
      } catch (error) {
        // El error ya se maneja con el alert
      }
    },
    volverAlListado() {
      this.$router.push('/proveedores');
    },
    irAEditar() {
      if (this.proveedorActual) {
        this.$router.push({ name: 'editarProveedor', params: { id: this.proveedorActual.id } });
      }
    },
  },
};
</script>

<style scoped>
.v-list-item__subtitle { font-weight: bold; color: rgba(0,0,0,0.6); font-size: 0.8rem; }
.v-list-item__title { font-size: 1rem; padding-top: 2px; }
.v-divider[inset] { margin-left: 0px; margin-right: 16px; }
</style>