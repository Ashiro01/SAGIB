<template>
  <v-container>
    <v-row align="center" class="mb-4">
      <v-col cols="12" md="8">
        <h1>Gestión de Usuarios</h1>
        <p>Administración de cuentas de usuario del sistema.</p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn color="primary" large to="/usuarios/registrar">
          <v-icon left>mdi-account-plus-outline</v-icon>
          Agregar Nuevo Usuario
        </v-btn>
      </v-col>
    </v-row>

    <v-card>
      <v-card-title>
        Usuarios Registrados
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Buscar usuario..."
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
        :items="usuariosParaTabla"
        :search="search"
        :items-per-page="10"
        class="elevation-1"
        item-value="id"
        hover
        :loading="isLoading"
      >
        <template v-slot:item.rol="{ item }">
          <v-chip :color="getRolColor(item.rol)" small dark>{{ item.rol }}</v-chip>
        </template>

        <template v-slot:item.estado="{ item }">
          <v-chip :color="item.estado === 'Activo' ? 'green' : 'red'" small dark @click="toggleEstadoUsuario(item)">
            {{ item.estado }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="editarUsuario(item)" color="orange darken-1">
            mdi-pencil
          </v-icon>
          <v-icon small @click="eliminarUsuario(item)" color="red darken-1" :disabled="item.username === 'admin'">
            mdi-delete
          </v-icon>
        </template>

        <template v-slot:no-data>
          <v-alert :value="true" color="warning" icon="mdi-alert">
            No hay usuarios registrados o que coincidan con la búsqueda.
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
          ¿Está seguro de que desea eliminar el usuario <br>
          <strong v-if="itemToDelete">{{ itemToDelete.nombre_completo }} ({{ itemToDelete.username }})</strong>?
          <br><br>
          Esta acción no se puede deshacer.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="cerrarDialogoEliminar">
            Cancelar
          </v-btn>
          <v-btn color="red darken-1" text @click="procederConEliminacionUsuario">
            Eliminar
          </v-btn>
          <v-spacer></v-spacer>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { useUsuarioStore } from '@/stores/usuarioStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'UsuarioListView',
  data: () => ({
    search: '',
    headers: [
      { title: 'Nombre Completo', key: 'nombre_completo', align: 'start', sortable: true },
      { title: 'Nombre de Usuario', key: 'username', sortable: true },
      { title: 'Email', key: 'email', sortable: true },
      { title: 'Rol Asignado', key: 'rol', sortable: true, align: 'center' },
      { title: 'Estado', key: 'estado', sortable: true, align: 'center' },
      { title: 'Acciones', key: 'actions', sortable: false, align: 'center' },
    ],
    dialogDeleteVisible: false,
    itemToDelete: null,
  }),
  watch: {
    listaUsuarios(newVal, oldVal) {
      console.log('[UsuarioListView] Watcher: listaUsuarios cambió.');
      console.log('[UsuarioListView] Watcher: Nuevo valor:', JSON.parse(JSON.stringify(newVal)));
      console.log('[UsuarioListView] Watcher: Antiguo valor:', JSON.parse(JSON.stringify(oldVal)));
      if (newVal.length < oldVal.length) {
        console.log('[UsuarioListView] Watcher: Un usuario fue eliminado de la lista.');
      } else if (newVal.length > oldVal.length) {
        console.log('[UsuarioListView] Watcher: Un usuario fue añadido a la lista.');
      }
    },
    getError(newError) {
        if (newError) {
            console.error('[UsuarioListView] Watcher: Se detectó un error en el store:', newError);
            // Puedes emitir una snackbar aquí si es necesario, aunque el store ya maneja el this.error
        }
    }
  },
  computed: {
    ...mapState(useUsuarioStore, ['listaUsuarios', 'isLoading', 'getError']),
    usuariosParaTabla() {
      // Mapea los usuarios del backend a las columnas de la tabla
      return this.listaUsuarios.map(u => ({
        id: u.id,
        nombre_completo: `${u.first_name} ${u.last_name}`.trim(),
        username: u.username,
        email: u.email,
        rol: (u.groups && Array.isArray(u.groups) && u.groups.length > 0)
          ? u.groups.map(g => g.name || g).join(', ')
          : 'Sin rol',
        estado: u.is_active ? 'Activo' : 'Inactivo',
      }));
    },
  },
  methods: {
    ...mapActions(useUsuarioStore, {
      fetchUsuarios: 'fetchUsuarios',
      eliminarUsuarioStoreAction: 'eliminarUsuario'
    }),
    editarUsuario(item) {
      this.$router.push({ name: 'editarUsuario', params: { id: item.id } });
    },
    async eliminarUsuario(item) {
      if (item.username === 'admin') {
        this.$emit('show-snackbar', {
          message: 'El usuario administrador principal no puede ser eliminado.',
          color: 'warning',
        });
        return;
      }
      this.itemToDelete = item;
      this.dialogDeleteVisible = true;
    },
    cerrarDialogoEliminar() {
      this.dialogDeleteVisible = false;
      this.$nextTick(() => {
        this.itemToDelete = null;
      });
    },
    async procederConEliminacionUsuario() {
      if (this.itemToDelete) {
        console.log(`[UsuarioListView] procederConEliminacionUsuario para ID: ${this.itemToDelete.id}, Nombre: ${this.itemToDelete.nombre_completo || this.itemToDelete.username}`);
        const nombreUsuarioAEliminar = this.itemToDelete.nombre_completo || this.itemToDelete.username;
        try {
          console.log('[UsuarioListView] Llamando a la acción del store eliminarUsuario...');
          const resultadoAccion = await this.eliminarUsuarioStoreAction(this.itemToDelete.id);
          console.log('[UsuarioListView] Resultado de la acción del store eliminarUsuario:', resultadoAccion);

          if (resultadoAccion && resultadoAccion.success) {
            this.$emit('show-snackbar', {
              message: resultadoAccion.message || `Usuario "${nombreUsuarioAEliminar}" eliminado correctamente.`,
              color: 'success',
            });
            console.log(`[UsuarioListView] Eliminación exitosa para ${nombreUsuarioAEliminar}. Snackbar emitida.`);
          } else {
            // Este caso podría no darse si la acción del store siempre lanza error en caso de fallo
            this.$emit('show-snackbar', {
              message: (resultadoAccion && resultadoAccion.message) || 'Error al eliminar el usuario.',
              color: 'error',
            });
            console.error(`[UsuarioListView] Eliminación fallida (según resultadoAccion) para ${nombreUsuarioAEliminar}. Snackbar de error emitida.`);
          }
        } catch (error) {
          console.error('[UsuarioListView] Error capturado al llamar a la acción del store eliminarUsuario:', error);
          this.$emit('show-snackbar', {
            message: error.message || 'Error al eliminar el usuario (excepción).',
            color: 'error',
          });
        } finally {
          console.log('[UsuarioListView] Cerrando diálogo de eliminación.');
          this.cerrarDialogoEliminar();
        }
      }
    },
    getRolColor(rol) {
      if (rol.includes('Administrador')) return 'red darken-2';
      if (rol.includes('Gestor')) return 'blue darken-1';
      if (rol.includes('Auditor')) return 'orange darken-2';
      if (rol.includes('Consultor')) return 'green darken-1';
      return 'grey';
    },
    toggleEstadoUsuario(item) {
      // Implementar lógica de cambio de estado real si lo necesitas
    },
  },
  async mounted() {
    try {
      await this.fetchUsuarios();
    } catch (error) {
      this.$emit('show-snackbar', {
        message: this.getError || 'No se pudieron cargar los usuarios.',
        color: 'error',
      });
    }
  },
};
</script>