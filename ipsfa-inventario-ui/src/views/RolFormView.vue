<template>
  <v-container>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formRol" v-model="validForm">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="rol.name"
                label="Nombre del Rol"
                :rules="[rules.required]"
                :disabled="isEditing && rol.esSistema"
                required outlined dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-textarea
                v-model="rol.descripcion"
                label="Descripción del Rol"
                rows="3"
                outlined dense
              ></v-textarea>
            </v-col>
          </v-row>

          <v-divider class="my-4"></v-divider>
          <h3 class="text-h6 mb-2">Asignar Permisos</h3>

          <v-row dense>
            <v-col 
                v-for="grupo in permisosAgrupados" 
                :key="grupo.grupo" 
                cols="12" md="6" lg="4"
            >
                <v-card outlined class="mb-3">
                    <v-card-subtitle class="pb-0">{{ grupo.grupo }}</v-card-subtitle>
                    <v-list dense class="pt-0">
                        <v-list-item v-for="permiso in grupo.items" :key="permiso.id" class="px-2">
                            <v-checkbox
                                v-model="rol.permisos"
                                :label="permiso.descripcion"
                                :value="permiso.id"
                                dense
                                hide-details
                                class="my-0 py-0"
                            ></v-checkbox>
                        </v-list-item>
                    </v-list>
                </v-card>
            </v-col>
          </v-row>
          <v-row v-if="!permisosAgrupados.length">
            <v-col cols="12">
                <v-alert type="info">No hay permisos disponibles para asignar.</v-alert>
            </v-col>
          </v-row>

        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelar">Cancelar</v-btn>
        <v-btn color="blue darken-1" :disabled="!validForm" @click="guardarRol">Guardar Rol</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import { useRolStore } from '@/stores/rolStore';

export default {
  name: 'RolFormView',
  data() {
    return {
      isEditing: false,
      validForm: false,
      guardando: false,
      rol: {
        id: null,
        name: '',
        descripcion: '',
        permisos: [],
        esSistema: false,
      },
      permisosDisponibles: [
        { id: 'ver_bienes', descripcion: 'Ver listado de bienes', grupo: 'Gestión de Bienes' },
        { id: 'ver_detalle_bien', descripcion: 'Ver detalles de un bien', grupo: 'Gestión de Bienes' },
        { id: 'registrar_bienes', descripcion: 'Registrar nuevos bienes', grupo: 'Gestión de Bienes' },
        { id: 'editar_bienes', descripcion: 'Editar información de bienes', grupo: 'Gestión de Bienes' },
        { id: 'eliminar_bienes', descripcion: 'Eliminar bienes del inventario', grupo: 'Gestión de Bienes' },
        { id: 'realizar_traslados', descripcion: 'Registrar traslados de bienes', grupo: 'Procesos de Inventario' },
        { id: 'realizar_desincorporaciones', descripcion: 'Registrar desincorporaciones', grupo: 'Procesos de Inventario' },
        { id: 'gestionar_proveedores', descripcion: 'Administrar proveedores', grupo: 'Gestión de Proveedores' },
        { id: 'gestionar_usuarios', descripcion: 'Administrar usuarios y sus accesos', grupo: 'Seguridad' },
        { id: 'gestionar_roles', descripcion: 'Administrar roles y permisos', grupo: 'Seguridad' },
        { id: 'generar_reportes_basicos', descripcion: 'Generar reportes generales', grupo: 'Reportes' },
        { id: 'generar_reportes_avanzados', descripcion: 'Generar reportes detallados/financieros', grupo: 'Reportes' },
        { id: 'ver_logs_auditoria', descripcion: 'Ver registros de auditoría', grupo: 'Seguridad' },
      ],
      rules: {
        required: value => !!value || 'Este campo es requerido.',
      },
    };
  },
  computed: {
    formTitle() {
      return this.isEditing ? 'Editar Rol (Nombre)' : 'Registrar Nuevo Rol';
    },
    permisosAgrupados() {
        const grupos = {};
        this.permisosDisponibles.forEach(p => {
            if (!grupos[p.grupo]) {
                grupos[p.grupo] = { grupo: p.grupo, items: [] };
            }
            grupos[p.grupo].items.push(p);
        });
        return Object.values(grupos);
    },
    rolActualDelStore() {
        const rolStore = useRolStore();
        return rolStore.getRolActual;
    }
  },
  methods: {
    async cargarRolParaEditar(rolId) {
      const rolStore = useRolStore();
      this.guardando = true;
      try {
        let rolData = rolStore.listaRoles.find(r => r.id === rolId);
        if (!rolData && rolStore.fetchRolById) {
            rolData = await rolStore.fetchRolById(rolId);
        }

        if (rolData) {
          this.rol.id = rolData.id;
          this.rol.name = rolData.name;
          this.rol.descripcion = rolData.descripcion;
          this.rol.permisos = rolData.permisos_asignados_ids || [];
          this.rol.esSistema = rolData.es_sistema;
        } else {
             this.$emit('show-snackbar', { message: 'Rol no encontrado.', color: 'error' });
             this.$router.push('/roles');
        }
      } catch (error) {
        this.$emit('show-snackbar', { message: rolStore.getError || 'Error al cargar datos del rol.', color: 'error' });
        this.$router.push('/roles');
      } finally {
        this.guardando = false;
      }
    },
    resetForm() {
      this.isEditing = false;
      this.rol = { id: null, name: '', descripcion: '', permisos: [], esSistema: false };
      if (this.$refs.formRol) {
        this.$refs.formRol.resetValidation();
      }
    },
    async guardarRol() {
      const { valid } = await this.$refs.formRol.validate();
      if (!valid) {
        this.$emit('show-snackbar', { message: 'Por favor, complete los campos requeridos.', color: 'error' });
        return;
      }

      this.guardando = true;
      const rolStore = useRolStore();
      const payload = {
        name: this.rol.name,
        descripcion: this.rol.descripcion,
        permisos: this.rol.permisos,
        es_sistema: this.rol.esSistema,
      };

      try {
        if (this.isEditing) {
          await rolStore.actualizarRol(this.rol.id, payload);
          this.$emit('show-snackbar', { message: `Rol "${this.rol.name}" actualizado.`, color: 'success' });
        } else {
          await rolStore.crearRol(payload);
          this.$emit('show-snackbar', { message: `Rol "${this.rol.name}" registrado.`, color: 'success' });
        }
        this.$router.push('/roles');
      } catch (error) {
         const storeError = rolStore.getError;
        this.$emit('show-snackbar', { message: storeError || 'Error al guardar el rol.', color: 'error' });
      } finally {
        this.guardando = false;
      }
    },
    cancelar() {
      this.$router.push('/roles');
    },
  },
  watch: {
    '$route.params.id': {
      immediate: true,
      handler(newId) {
        const rolStore = useRolStore();
        if (this.$route.name === 'editarRol' && newId) {
          this.isEditing = true;
          if (rolStore.listaRoles.length === 0) {
            rolStore.fetchRoles().then(() => {
                this.cargarRolParaEditar(parseInt(newId));
            });
          } else {
             this.cargarRolParaEditar(parseInt(newId));
          }
        } else if (this.$route.name === 'registrarRol') {
          this.isEditing = false;
          this.resetForm();
        }
      }
    }
  },
  async created() {
    const rolStore = useRolStore();
    if (rolStore.listaRoles.length === 0) {
        try {
            await rolStore.fetchRoles();
        } catch(e) {
            console.error("Error inicial al cargar roles en RolFormView", e);
        }
    }
  }
};
</script>