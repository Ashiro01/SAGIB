<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col cols="12" md="8">
        <h1>Gestión de Roles</h1>
        <p>Definición de roles y asignación de permisos en el sistema.</p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn color="primary" large to="/roles/registrar">
          <v-icon left>mdi-shield-plus-outline</v-icon>
          Agregar Nuevo Rol
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        Roles Definidos
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar rol..."
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
        :items="listaRoles"
        :search="search"
        :items-per-page="10"
        class="elevation-1"
        item-value="id"
        hover
        :loading="isLoading"
        loading-text="Cargando roles..."
      >
        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="editarRol(item)" color="orange darken-1" title="Editar Rol">
            mdi-pencil
          </v-icon>
          <v-icon small @click="prepararEliminarRol(item)" color="red darken-1" title="Eliminar Rol" :disabled="item.name === 'Administrador' || item.name === 'admin'">
            mdi-delete
          </v-icon>
        </template>

        <template v-slot:no-data>
          <v-alert v-if="!isLoading" :value="true" color="info" icon="mdi-information-outline">
            No hay roles definidos o que coincidan con la búsqueda.
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
          ¿Está seguro de que desea eliminar el rol <br>
          <strong v-if="itemToDelete">{{ itemToDelete.name }}</strong>?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cerrarDialogoEliminar">Cancelar</v-btn>
          <v-btn color="red darken-1" text @click="procederConEliminacion" :loading="eliminando">Eliminar</v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { useRolStore } from '@/stores/rolStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'RolListView',
  data: () => ({
    search: '',
    headers: [
      { title: 'ID', key: 'id', align: 'start', sortable: true, width: '80px'},
      { title: 'Nombre del Rol (Grupo)', key: 'name', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
    ],
    dialogDeleteVisible: false,
    itemToDelete: null,
    eliminando: false,
  }),
  computed: {
    ...mapState(useRolStore, ['listaRoles', 'isLoading', 'getError']),
  },
  methods: {
    ...mapActions(useRolStore, ['fetchRoles', 'eliminarRol']),

    editarRol(item) {
      this.$router.push({ name: 'editarRol', params: { id: item.id } });
    },
    prepararEliminarRol(item) {
      this.itemToDelete = item;
      this.dialogDeleteVisible = true;
    },
    cerrarDialogoEliminar() {
      this.dialogDeleteVisible = false;
      this.$nextTick(() => { this.itemToDelete = null; });
    },
    async procederConEliminacion() {
      if (this.itemToDelete) {
        if (['admin', 'Administrador', 'DefaultUser'].includes(this.itemToDelete.name)) {
            this.$emit('show-snackbar', { message: `El rol "${this.itemToDelete.name}" no puede ser eliminado.`, color: 'warning' });
            this.cerrarDialogoEliminar();
            return;
        }
        this.eliminando = true;
        try {
          await this.eliminarRol(this.itemToDelete.id);
          this.$emit('show-snackbar', {
            message: `Rol "${this.itemToDelete.name}" eliminado correctamente.`,
            color: 'success',
          });
        } catch (error) {
          this.$emit('show-snackbar', {
            message: this.getError || 'Error al eliminar el rol.',
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
      await this.fetchRoles();
    } catch (error) {
      this.$emit('show-snackbar', {
        message: this.getError || 'No se pudieron cargar los roles.',
        color: 'error'
      });
    }
  },
};
</script>
<style scoped>
.text-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>