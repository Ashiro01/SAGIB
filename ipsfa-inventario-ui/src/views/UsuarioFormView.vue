<template>
  <v-container>
    <v-card>
      <v-card-title>
        <span class="text-h5">{{ formTitle }}</span>
      </v-card-title>
      <v-card-text>
        <v-form ref="formUsuario" v-model="validForm">
          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="usuario.first_name"
                label="Primer Nombre"
                :rules="[rules.required]"
                required outlined dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="usuario.last_name"
                label="Apellido"
                :rules="[rules.required]"
                required outlined dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="usuario.username"
                label="Nombre de Usuario"
                :rules="[rules.required, rules.minLength(4)]"
                :disabled="isEditing" 
                counter="20"
                required outlined dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="usuario.email"
                label="Correo Electrónico"
                type="email"
                :rules="[rules.required, rules.email]"
                required outlined dense
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="usuario.group_ids"
                :items="rolesParaSelector"
                label="Rol(es) del Usuario"
                :rules="[rules.required]"
                required outlined dense
                :disabled="isEditing && usuario.username === 'admin'"
                multiple
                chips
                deletable-chips
                item-title="name"
                item-value="id"
              ></v-select>
            </v-col>

            <v-col cols="12"><v-divider class="my-2"></v-divider></v-col>

            <v-col cols="12">
               <p class="caption" v-if="isEditing">
                Deje los campos de contraseña en blanco si no desea cambiarla.
              </p>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="usuario.password"
                label="Contraseña"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showPassword = !showPassword"
                :rules="isEditing ? [rules.passwordOptional] : [rules.required, rules.minLength(6)]"
                outlined dense
                :hint="!isEditing ? 'Mínimo 6 caracteres' : ''"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="usuario.password_confirm"
                label="Confirmar Contraseña"
                :type="showPasswordConfirm ? 'text' : 'password'"
                :append-icon="showPasswordConfirm ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showPasswordConfirm = !showPasswordConfirm"
                :rules="isEditing ? [rules.passwordMatchOptional] : [rules.required, rules.passwordMatch]"
                outlined dense
              ></v-text-field>
            </v-col>

            <v-col cols="12" v-if="isEditing"> <v-switch
                v-model="usuario.is_active"
                :label="`Estado: ${usuario.is_active ? 'Activo' : 'Inactivo'}`"
                true-value="true"
                false-value="false"
                color="primary"
                inset
                :disabled="isEditing && usuario.username === 'admin' && usuario.is_active"
              ></v-switch>
            </v-col>

          </v-row>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue darken-1" text @click="cancelar">Cancelar</v-btn>
        <v-btn color="blue darken-1" :disabled="isLoading" @click="guardarUsuario">Guardar Usuario</v-btn>
      </v-card-actions>
    </v-card>
  </v-container>
</template>

<script>
import { useUsuarioStore } from '@/stores/usuarioStore';
import { mapActions, mapState } from 'pinia';

export default {
  name: 'UsuarioFormView',
  data() {
    return {
      isEditing: false,
      validForm: false,
      showPassword: false,
      showPasswordConfirm: false,
      usuario: {
        id: null,
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        password_confirm: '',
        group_ids: [],
        is_active: true,
        is_staff: false,
      },
      rules: {
        required: value => !!value || 'Este campo es requerido.',
        minLength: min => value => (value && value.length >= min) || `Mínimo ${min} caracteres.`,
        email: value => {
          if (!value) return true;
          const pattern = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || 'Email inválido.';
        },
        passwordMatch: value => value === this.usuario.password || 'Las contraseñas no coinciden.',
        passwordOptional: value => (!value || value.length >= 6) || 'Si ingresa contraseña, mínimo 6 caracteres.',
        passwordMatchOptional: value => (!this.usuario.password || value === this.usuario.password) || 'Las contraseñas no coinciden.',
      },
      rolesDisponibles: [],
    };
  },
  computed: {
    ...mapState(useUsuarioStore, ['listaGrupos', 'getError', 'isLoading']),
    formTitle() {
      return this.isEditing ? 'Editar Usuario' : 'Registrar Nuevo Usuario';
    },
    rolesParaSelector() {
      // Normaliza para asegurar que cada grupo tiene id y name
      return this.listaGrupos;
    },
  },
  async created() {
    const usuarioStore = useUsuarioStore();
    await usuarioStore.fetchGrupos();
    if (this.$route.params.id) {
      this.isEditing = true;
      await this.cargarUsuarioParaEditar(parseInt(this.$route.params.id));
    } else {
      this.resetForm();
    }
  },
  methods: {
    ...mapActions(useUsuarioStore, ['crearUsuario', 'actualizarUsuario', 'fetchUsuarioById']),
    async cargarUsuarioParaEditar(usuarioId) {
      try {
        const usuarioStore = useUsuarioStore();
        await usuarioStore.fetchUsuarioById(usuarioId);
        const usuarioExistente = usuarioStore.getUsuarioActual;
        if (usuarioExistente) {
          this.usuario = {
            id: usuarioExistente.id,
            first_name: usuarioExistente.first_name,
            last_name: usuarioExistente.last_name,
            username: usuarioExistente.username,
            email: usuarioExistente.email,
            password: '',
            password_confirm: '',
            group_ids: usuarioExistente.groups ? usuarioExistente.groups.map(g => g.id) : [],
            is_active: usuarioExistente.is_active,
            is_staff: usuarioExistente.is_staff,
          };
        }
      } catch (error) {
        this.$emit('show-snackbar', { message: this.getError || 'Error al cargar datos del usuario.', color: 'error' });
        this.$router.push('/usuarios');
      }
    },
    resetForm() {
      this.isEditing = false;
      this.usuario = {
        id: null,
        first_name: '',
        last_name: '',
        username: '',
        email: '',
        password: '',
        password_confirm: '',
        group_ids: [],
        is_active: true,
        is_staff: false,
      };
      if (this.$refs.formUsuario) {
        this.$refs.formUsuario.resetValidation();
      }
    },
    async guardarUsuario() {
      if (!this.$refs.formUsuario.validate()) {
        this.$emit('show-snackbar', { message: 'Por favor, complete todos los campos requeridos correctamente.', color: 'error' });
        return;
      }
      const payload = {
        username: this.usuario.username,
        first_name: this.usuario.first_name,
        last_name: this.usuario.last_name,
        email: this.usuario.email,
        is_active: this.usuario.is_active,
        is_staff: this.usuario.is_staff,
        group_ids: this.usuario.group_ids,
      };
      // Solo incluir password si se está creando o si el usuario la cambió
      if (!this.isEditing || (this.usuario.password && this.usuario.password_confirm)) {
        payload.password = this.usuario.password;
        payload.password_confirm = this.usuario.password_confirm;
      }
      try {
        if (this.isEditing) {
          await this.actualizarUsuario(this.usuario.id, payload);
          this.$emit('show-snackbar', { message: `Usuario "${this.usuario.username}" actualizado correctamente.`, color: 'success' });
        } else {
          await this.crearUsuario(payload);
          this.$emit('show-snackbar', { message: `Usuario "${this.usuario.username}" registrado correctamente.`, color: 'success' });
        }
        this.$router.push('/usuarios');
      } catch (error) {
        this.$emit('show-snackbar', { message: this.getError || 'Error al guardar el usuario.', color: 'error' });
      }
    },
    cancelar() {
      this.$router.push('/usuarios');
    },
    onRolesChange(val) {
      // Si por alguna razón llegan objetos, extrae solo los IDs
      if (Array.isArray(val)) {
        this.usuario.group_ids = val.map(v => (typeof v === 'object' && v !== null ? v.id : v));
      }
    },
  },
  watch: {
    '$route'(to, _from) {
      if (to.name === 'registrarUsuario' && !to.params.id) {
        this.isEditing = false;
        this.resetForm();
      } else if (to.name === 'editarUsuario' && to.params.id) {
        this.isEditing = true;
        this.cargarUsuarioParaEditar(parseInt(to.params.id));
      }
    }
  }
};
</script>