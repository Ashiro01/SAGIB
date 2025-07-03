<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col cols="12" md="8">
        <h1>Listado de Proveedores</h1>
        <p>Proveedores registrados en el sistema.</p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn color="primary" large to="/proveedores/registrar">
          <v-icon left>mdi-plus-circle-outline</v-icon>
          Registrar Nuevo Proveedor
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        Proveedores Registrados
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar proveedor..."
          single-line
          hide-details
          dense
          outlined
          class="mr-4"
          style="max-width: 300px;"
        ></v-text-field>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="listaProveedores"
        :search="search"
        :items-per-page="10"
        class="elevation-1"
        item-value="id"
        hover
        :loading="isLoading"
        loading-text="Cargando proveedores..."
      >
        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="verProveedor(item)" color="blue darken-1">
            mdi-eye
          </v-icon>
          <v-icon small class="mr-2" @click="editarProveedor(item)" color="orange darken-1">
            mdi-pencil
          </v-icon>
          <v-icon small @click="eliminarProveedorDialog(item)" color="red darken-1">
            mdi-delete
          </v-icon>
        </template>

        <template v-slot:no-data>
          <v-alert :value="true" color="warning" icon="mdi-alert">
            No hay proveedores registrados o que coincidan con la búsqueda.
          </v-alert>
        </template>
      </v-data-table>
    </v-card>

    <v-dialog v-model="dialogDeleteVisible" max-width="500px" persistent>
      <v-card>
        <v-card-title class="text-h5 justify-center">
          <v-icon color="warning" large class="mr-2">mdi-alert-circle-outline</v-icon>
          Confirmar Eliminación
        </v-card-title>
        <v-card-text class="text-center body-1">
          ¿Está seguro de que desea eliminar el proveedor <br>
          <strong v-if="itemToDelete">{{ itemToDelete.nombre_proveedor }}</strong>?
          <br><br>
          Esta acción no se puede deshacer.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cerrarDialogoEliminar">
            Cancelar
          </v-btn>
          <v-btn color="red darken-1" text @click="procederConEliminacionProveedor" :loading="eliminando">
            Eliminar
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { useProveedorStore } from '@/stores/proveedorStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'ProveedorListView',
  data: () => ({
    search: '',
    headers: [
      { title: 'Nombre del Proveedor', key: 'nombre_proveedor', align: 'start', sortable: true },
      { title: 'RIF', key: 'rif', sortable: true },
      { title: 'Email de Contacto', key: 'contacto_principal_email', sortable: true },
      { title: 'Teléfono', key: 'contacto_principal_telefono', sortable: false },
      { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
    ],
    dialogDeleteVisible: false,
    itemToDelete: null,
    eliminando: false,
  }),
  computed: {
    ...mapState(useProveedorStore, ['listaProveedores', 'isLoading', 'getError']),
  },
  methods: {
    ...mapActions(useProveedorStore, ['fetchProveedores', 'eliminarProveedor']),
    verProveedor(item) {
      this.$router.push({ name: 'detalleProveedor', params: { id: item.id } });
    },
    editarProveedor(item) {
      this.$router.push({ name: 'editarProveedor', params: { id: item.id } });
    },
    eliminarProveedorDialog(item) {
      this.itemToDelete = item;
      this.dialogDeleteVisible = true;
    },
    cerrarDialogoEliminar() {
      this.dialogDeleteVisible = false;
      this.$nextTick(() => {
        this.itemToDelete = null;
      });
    },
    async procederConEliminacionProveedor() {
      if (this.itemToDelete) {
        this.eliminando = true;
        try {
          await this.eliminarProveedor(this.itemToDelete.id);
          this.$emit('show-snackbar', {
            message: `Proveedor "${this.itemToDelete.nombre_proveedor}" eliminado correctamente.`,
            color: 'success',
          });
        } catch (error) {
          this.$emit('show-snackbar', {
            message: this.getError || 'Error al eliminar el proveedor.',
            color: 'error',
          });
        } finally {
          this.eliminando = false;
          this.cerrarDialogoEliminar();
        }
      }
    },
  },
  async mounted() {
    try {
      await this.fetchProveedores();
    } catch (error) {
      this.$emit('show-snackbar', {
        message: this.getError || 'No se pudieron cargar los proveedores.',
        color: 'error',
      });
    }
  },
};
</script>