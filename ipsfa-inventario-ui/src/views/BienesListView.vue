<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col cols="12" md="8">
        <h1>Listado de Bienes</h1>
        <p>Bienes patrimoniales registrados en el sistema.</p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn color="secondary" large to="/bienes/carga-masiva" class="mr-2"> <v-icon left>mdi-upload-multiple</v-icon>
          Carga Masiva
        </v-btn>
        <v-btn color="primary" large to="/bienes/registrar">
          <v-icon left>mdi-plus-circle-outline</v-icon>
          Registrar Nuevo Bien
        </v-btn>
      </v-col>
    </v-row>
    

    <v-card>
      <v-card-title>
        Bienes Registrados
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar bien..."
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
        :items="bienesDelStore"
        :search="search"
        :items-per-page="10"
        class="elevation-1"
        item-value="id"
        hover
        :loading="isLoadingBienes" loading-text="Cargando bienes desde el servidor...">
        <template v-slot:item.valor_unitario_bs="{ item }">
          <span>{{ formatCurrency(item.valor_unitario_bs, 'Bs.') }}</span>
        </template>
        <template v-slot:no-data>
          <v-alert v-if="!isLoadingBienes" :value="true" color="info" icon="mdi-information-outline">
            No hay bienes registrados en el sistema o que coincidan con la búsqueda.
          </v-alert>
        </template>
        <template #item.actions="{ item }">
          <v-icon small class="mr-2" @click="verBien(item)" color="blue darken-1">
            mdi-eye
          </v-icon>
          <v-icon small class="mr-2" @click="editarBien(item)" color="orange darken-1">
            mdi-pencil
          </v-icon>
          <v-icon small @click="prepararEliminarUnidad(item)" color="red darken-1">
            mdi-delete
          </v-icon>
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
          ¿Está seguro de que desea eliminar el bien <br>
          <strong v-if="itemToDelete">{{ itemToDelete.codigo_patrimonial }} - {{ itemToDelete.descripcion }}</strong>?
          <br><br>
          Esta acción no se puede deshacer.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cerrarDialogoEliminar">
            Cancelar
          </v-btn>
          <v-btn color="red darken-1" text @click="procederConEliminacion">
            Eliminar
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-container>
</template>

<script>
// 1. Importa lo necesario de Pinia y tu store
import { useBienesStore } from '@/stores/bienesStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'BienesListView',
  data: () => ({
    search: '',
    headers: [
      { title: 'Código Patrimonial', key: 'codigo_patrimonial', align: 'start', sortable: true },
      { title: 'Descripción', key: 'descripcion', sortable: true },
      { title: 'Marca', key: 'marca', sortable: true },
      { title: 'Modelo', key: 'modelo', sortable: false },
      { title: 'Fecha Adq.', key: 'fecha_adquisicion', sortable: true },
      { title: 'Ubicación', key: 'ubicacion_fisica_especifica', sortable: true },
      { title: 'Estado', key: 'estado_bien', sortable: true },
      { title: 'Valor (Bs.)', key: 'valor_unitario_bs', align: 'end', sortable: true },
      { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
    ],
    dialogDeleteVisible: false,
    itemToDelete: null,
    eliminando: false,
  }),
  computed: {
    // 3. Mapea el estado y getters del bienesStore
    ...mapState(useBienesStore, {
      bienesDelStore: 'listaBienes',
      isLoadingBienes: 'isLoading',
      errorBienes: 'getError',
    }),
    // bienesParaTabla() {
    //   return this.bienesDelStore.map(bien => ({
    //     ...bien,
    //     fecha_adquisicion_formateada: this.formatDate(bien.fecha_adquisicion)
    //   }));
    // }
  },
  methods: {
    // 4. Mapea las acciones del bienesStore
    ...mapActions(useBienesStore, [
      'fetchBienes',
    ]),
    formatCurrency(value, currencySymbol = 'Bs.') {
      if (value === null || typeof value === 'undefined') return 'N/A';
      if (typeof value !== 'number') {
        const numValue = parseFloat(value);
        if (isNaN(numValue)) return value;
        value = numValue;
      }
      const fixedValue = parseFloat(value.toFixed(2));
      return `${currencySymbol} ${fixedValue.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    },
    verBien(item) {
      this.$router.push({ name: 'detalleBien', params: { id: item.id } });
    },
    editarBien(item) {
      this.$router.push({ name: 'editarBien', params: { id: item.id } });
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
        const bienesStore = useBienesStore();
        try {
          await bienesStore.eliminarBien(this.itemToDelete.id);
          this.$emit('show-snackbar', {
            message: `Bien "${this.itemToDelete.descripcion}" eliminado exitosamente.`,
            color: 'success',
          });
        } catch (error) {
          console.error("Error al eliminar bien desde la vista:", error);
          this.$emit('show-snackbar', {
            message: error.message || 'Error al intentar eliminar el bien.',
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
      await this.fetchBienes();
    } catch (error) {
      this.$emit('show-snackbar', {
        message: this.errorBienes || 'No se pudieron cargar los bienes.',
        color: 'error'
      });
    }
  },
};
</script>

<style scoped>
/* Si necesitas estilos específicos */
.v-card-title {
  align-items: center; /* Para alinear el buscador verticalmente con el título */
}
</style>