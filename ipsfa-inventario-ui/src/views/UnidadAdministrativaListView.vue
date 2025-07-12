<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col cols="12" md="8">
        <h1>Unidades Administrativas</h1>
        <p>Catálogo de gerencias, departamentos y sedes del IPSFANB.</p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn color="primary" large to="/unidades-administrativas/registrar">
          <v-icon left>mdi-office-building-plus-outline</v-icon>
          Agregar Unidad
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        Listado de Unidades
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar unidad..."
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
        :items="unidades"
        :search="search"
        :items-per-page="10"
        class="elevation-1"
        item-value="id"
        hover
        :loading="loading"
        loading-text="Cargando unidades..."
      >
        <template v-slot:item.activa="{ item }">
          <v-chip :color="item.activa ? 'green' : 'grey'" small dark>
            {{ item.activa ? 'Activa' : 'Inactiva' }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="editarUnidad(item)" color="orange darken-1">
            mdi-pencil
          </v-icon>
          <v-icon small @click="prepararEliminarUnidad(item)" color="red darken-1">
            mdi-delete
          </v-icon>
        </template>
        <template v-slot:no-data>
          <v-alert :value="true" color="info" icon="mdi-information-outline">
            No hay unidades administrativas registradas.
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
          ¿Está seguro de que desea eliminar la unidad <br>
          <strong v-if="itemToDelete">{{ itemToDelete.codigo }} - {{ itemToDelete.nombre }}</strong>?
          <br><br>
          Esta acción no se puede deshacer.
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
import { useUnidadAdministrativaStore } from '@/stores/unidadAdministrativaStore';
import { mapActions, mapState } from 'pinia';

export default {
  name: 'UnidadAdministrativaListView',
  data: () => ({
    search: '',
    headers: [
      { title: 'Código', key: 'codigo', align: 'start', sortable: true },
      { title: 'Nombre de la Unidad', key: 'nombre', sortable: true },
      { title: 'Descripción', key: 'descripcion', sortable: false, width: '30%' },
      { title: 'Estado', key: 'activa', sortable: true, align: 'center' },
      { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
    ],
    dialogDeleteVisible: false,
    itemToDelete: null,
    loading: false, // Para el estado de carga de la tabla
    eliminando: false, // Para el estado de carga del botón de eliminar en el diálogo
  }),
  computed: {
    // Mapeamos el estado 'unidades' del store a una propiedad computada local
    ...mapState(useUnidadAdministrativaStore, ['unidades', 'isLoading']), 
  },
  methods: {
    // Mapeamos la acción 'eliminarUnidad' del store
    ...mapActions(useUnidadAdministrativaStore, ['eliminarUnidad', 'fetchUnidades']),

    editarUnidad(item) {
      this.$router.push({ name: 'editarUnidadAdministrativa', params: { id: item.id } });
    },
    prepararEliminarUnidad(item) {
      this.itemToDelete = item;
      this.dialogDeleteVisible = true;
    },
    cerrarDialogoEliminar() {
      this.dialogDeleteVisible = false;
      this.$nextTick(() => {
        this.itemToDelete = null;
      });
    },
    async procederConEliminacion() {
      if (this.itemToDelete) {
        this.eliminando = true;
        try {
          await this.eliminarUnidad(this.itemToDelete.id); // Llama a la acción del store
          this.$emit('show-snackbar', {
            message: `Unidad "${this.itemToDelete.nombre}" eliminada correctamente.`,
            color: 'success',
          });
        } catch (error) {
          console.error("Error al eliminar unidad:", error);
          this.$emit('show-snackbar', {
            message: error.message || 'Error al eliminar la unidad.',
            color: 'error',
          });
        } finally {
          this.eliminando = false;
          this.cerrarDialogoEliminar();
        }
      }
    },
  },
  mounted() {
    this.fetchUnidades();
  }
};
</script>