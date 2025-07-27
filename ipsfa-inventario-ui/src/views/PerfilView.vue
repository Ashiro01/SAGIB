<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-2">Mi Perfil</h1>
        <p class="subtitle-1">Gestiona tu información personal y de seguridad.</p>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Foto de Perfil</v-card-title>
          <v-card-text class="text-center">
            <v-avatar size="150" class="mb-4 elevation-3">
              <v-img :src="fotoUrl" alt="Foto de Perfil"></v-img>
            </v-avatar>
            <v-file-input
              v-model="fotoSeleccionada"
              label="Seleccionar nueva foto"
              accept="image/png, image/jpeg, image/bmp"
              prepend-icon="mdi-camera"
              outlined
              dense
              @change="previsualizarFoto"
            ></v-file-input>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="subirFoto" :loading="isSubmitting" :disabled="!fotoSeleccionada">
              Actualizar Foto
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card class="mb-6">
          <v-card-title class="d-flex align-center justify-space-between">
            <span>Datos Personales</span>
            <v-btn icon @click="toggleEditDatos" v-if="!editandoDatos">
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text>
            <v-form ref="formDatos" v-model="formDatosValido">
              <v-text-field
                v-model="perfilData.username"
                label="Nombre de Usuario"
                readonly
                disabled
                outlined
                dense
              ></v-text-field>
              <v-text-field
                v-model="perfilData.first_name"
                label="Nombre(s)"
                :rules="[rules.required]"
                outlined
                dense
                :readonly="!editandoDatos"
              ></v-text-field>
              <v-text-field
                v-model="perfilData.last_name"
                label="Apellido(s)"
                :rules="[rules.required]"
                outlined
                dense
                :readonly="!editandoDatos"
              ></v-text-field>
              <v-text-field
                v-model="perfilData.email"
                label="Correo Electrónico"
                type="email"
                :rules="[rules.required, rules.email]"
                outlined
                dense
                :readonly="!editandoDatos"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions v-if="editandoDatos">
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="actualizarDatos" :loading="isSubmitting" :disabled="!formDatosValido">
              Guardar Cambios
            </v-btn>
            <v-btn color="secondary" @click="cancelarEdicionDatos" :disabled="isSubmitting">
              Cancelar
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card>
          <v-card-title>Cambiar Contraseña</v-card-title>
          <v-card-text>
            <v-form ref="formPassword" v-model="formPasswordValido">
              <v-text-field
                v-model="passwordData.old_password"
                label="Contraseña Actual"
                type="password"
                :rules="[rules.required]"
                outlined
                dense
              ></v-text-field>
              <v-text-field
                v-model="passwordData.new_password"
                label="Nueva Contraseña"
                type="password"
                :rules="[rules.required, rules.minLength(8)]"
                hint="Mínimo 8 caracteres"
                outlined
                dense
              ></v-text-field>
              <v-text-field
                v-model="passwordData.new_password_confirm"
                label="Confirmar Nueva Contraseña"
                type="password"
                :rules="[rules.required, rules.passwordMatch]"
                outlined
                dense
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="guardarCambioContraseña" :loading="isSubmitting" :disabled="!formPasswordValido">
              Cambiar Contraseña
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card class="mt-6">
          <v-card-title>Preguntas de Seguridad</v-card-title>
          <v-card-subtitle>Añada hasta 3 preguntas para recuperar su cuenta.</v-card-subtitle>
          <v-card-text>
            <v-list v-if="respuestasUsuario.length > 0" lines="two">
              <v-list-item
                v-for="respuesta in respuestasUsuario"
                :key="respuesta.id"
                :title="respuesta.pregunta_texto"
                subtitle="Respuesta registrada (oculta por seguridad)"
              >
                <template v-slot:append>
                  <v-btn
                    color="error"
                    icon="mdi-delete-outline"
                    variant="text"
                    @click="eliminarRespuesta(respuesta.id)"
                    :loading="isSubmitting"
                  ></v-btn>
                </template>
              </v-list-item>
            </v-list>
            <p v-else class="text-grey">Aún no ha añadido ninguna pregunta de seguridad.</p>

            <v-divider class="my-4" v-if="respuestasUsuario.length > 0 && respuestasUsuario.length < 3"></v-divider>

            <div v-if="respuestasUsuario.length < 3">
              <h4 class="text-h6 mt-4 mb-2">Añadir Nueva Pregunta</h4>
              <v-form ref="formRespuesta" v-model="formRespuestaValido">
                <v-select
                  v-model="nuevaRespuesta.pregunta"
                  :items="preguntasParaSeleccionar"
                  item-title="texto"
                  item-value="id"
                  label="Seleccione una pregunta"
                  :rules="[rules.required]"
                  outlined
                  dense
                  no-data-text="No hay más preguntas disponibles"
                ></v-select>
                <v-text-field
                  v-model="nuevaRespuesta.respuesta_plana"
                  label="Su respuesta (sensible a mayúsculas/minúsculas)"
                  :rules="[rules.required]"
                  outlined
                  dense
                ></v-text-field>
              </v-form>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  @click="guardarRespuesta"
                  :loading="isSubmitting"
                  :disabled="!formRespuestaValido"
                >
                  Guardar Pregunta
                </v-btn>
              </v-card-actions>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>


<script>

import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'PerfilView',
  data() {
    return {
      isSubmitting: false,
      formDatosValido: false,
      formPasswordValido: false,
      editandoDatos: false,
      perfilData: {
        username: '',
        first_name: '',
        last_name: '',
        email: '',
      },
      perfilDataOriginal: {
        username: '',
        first_name: '',
        last_name: '',
        email: '',
      },
      passwordData: {
        old_password: '',
        new_password: '',
        new_password_confirm: '',
      },
      fotoSeleccionada: null,
      fotoUrl: null,
      rules: {
        required: value => !!value || 'Campo requerido.',
        email: value => /.+@.+\..+/.test(value) || 'Debe ser un correo válido.',
        minLength: min => v => (v && v.length >= min) || `Mínimo ${min} caracteres.`,
        passwordMatch: () => this.passwordData.new_password === this.passwordData.new_password_confirm || 'Las contraseñas no coinciden.',
      },
      usuario: null,
      // --- NUEVO PARA PREGUNTAS DE SEGURIDAD ---
      nuevaRespuesta: {
        pregunta: null,
        respuesta_plana: '',
      },
      formRespuestaValido: false,
      authStore: null,
    };
  },
  computed: {
    usuarioStore() {
      return this.authStore ? this.authStore.getCurrentUser : null;
    },
    preguntasDisponibles() {
      return this.authStore ? this.authStore.getPreguntasDisponibles : [];
    },
    respuestasUsuario() {
      return this.authStore ? this.authStore.getRespuestasUsuario : [];
    },
    isSubmittingStore() {
      return this.authStore ? this.authStore.loading : false;
    },
    preguntasParaSeleccionar() {
      const idsRespondidas = new Set(this.respuestasUsuario.map(r => r.pregunta));
      return this.preguntasDisponibles.filter(p => !idsRespondidas.has(p.id));
    },
    isSubmitting() {
      return this.isSubmittingStore || this.$data.isSubmitting;
    },
  },
  methods: {
    async cargarPerfilCompleto() {
      try {
        const axios = (await import('axios')).default;
        const token = this.authStore.accessToken;
        const response = await axios.get('http://127.0.0.1:8000/api/perfil/completo/', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        this.usuario = response.data;
        this.setUsuarioFromStore();
      } catch (error) {
        this.$emit('show-snackbar', { message: 'No se pudo cargar el perfil.', color: 'error' });
      }
    },
    async fetchSecurityQuestions() {
      await this.authStore.fetchSecurityQuestions();
    },
    async fetchUserSecurityAnswers() {
      await this.authStore.fetchUserSecurityAnswers();
    },
    async saveUserSecurityAnswer(payload) {
      return await this.authStore.saveUserSecurityAnswer(payload);
    },
    async deleteUserSecurityAnswer(answerId) {
      return await this.authStore.deleteUserSecurityAnswer(answerId);
    },
    async updateUserProfile(payload) {
      return await this.authStore.updateUserProfile(payload);
    },
    async changePassword(payload) {
      return await this.authStore.changePassword(payload);
    },
    // ...el resto de métodos existentes sin cambios...
    setUsuarioFromStore() {
      const newVal = this.usuario;
      this.perfilData.username = (newVal && newVal.username) ? newVal.username : '';
      this.perfilData.first_name = (newVal && newVal.first_name) ? newVal.first_name : '';
      this.perfilData.last_name = (newVal && newVal.last_name) ? newVal.last_name : '';
      this.perfilData.email = (newVal && newVal.email) ? newVal.email : '';
      this.perfilDataOriginal = {
        username: this.perfilData.username,
        first_name: this.perfilData.first_name,
        last_name: this.perfilData.last_name,
        email: this.perfilData.email,
      };
      if (newVal && newVal.perfil && newVal.perfil.foto_perfil) {
        this.fotoUrl = `http://127.0.0.1:8000${newVal.perfil.foto_perfil}`;
      } else {
        this.fotoUrl = 'https://cdn.vuetifyjs.com/images/avatars/avatar-15.jpg';
      }
    },
    toggleEditDatos() {
      this.editandoDatos = true;
    },
    cancelarEdicionDatos() {
      this.perfilData = { ...this.perfilDataOriginal };
      this.editandoDatos = false;
    },
    previsualizarFoto() {
      if (this.fotoSeleccionada) {
        this.fotoUrl = URL.createObjectURL(this.fotoSeleccionada);
      }
    },
    async actualizarDatos() {
      const { valid } = await this.$refs.formDatos.validate();
      if (!valid) return;
      this.isSubmitting = true;
      try {
        await this.updateUserProfile(this.perfilData);
        this.$emit('show-snackbar', { message: 'Datos personales actualizados exitosamente.', color: 'success' });
        this.setUsuarioFromStore();
        this.editandoDatos = false;
      } catch (error) {
        this.$emit('show-snackbar', { message: error.message || 'Error al actualizar los datos.', color: 'error' });
      } finally {
        this.isSubmitting = false;
      }
    },
    async subirFoto() {
      if (!this.fotoSeleccionada) return;
      this.isSubmitting = true;
      try {
        const payload = { ...this.perfilData, foto_perfil: this.fotoSeleccionada };
        await this.updateUserProfile(payload);
        this.$emit('show-snackbar', { message: 'Foto de perfil actualizada.', color: 'success' });
        this.fotoSeleccionada = null;
        this.setUsuarioFromStore();
      } catch (error) {
        this.$emit('show-snackbar', { message: error.message || 'Error al subir la foto.', color: 'error' });
      } finally {
        this.isSubmitting = false;
      }
    },
    async guardarCambioContraseña() {
      const { valid } = await this.$refs.formPassword.validate();
      if (!valid) return;
      this.isSubmitting = true;
      try {
        await this.changePassword(this.passwordData);
        this.$emit('show-snackbar', { message: 'Contraseña cambiada exitosamente.', color: 'success' });
        this.$refs.formPassword.reset();
      } catch (error) {
        this.$emit('show-snackbar', { message: error.message || 'Error al cambiar la contraseña.', color: 'error' });
      } finally {
        this.isSubmitting = false;
      }
    },
    // --- NUEVOS MÉTODOS PARA PREGUNTAS DE SEGURIDAD ---
    async guardarRespuesta() {
      const { valid } = await this.$refs.formRespuesta.validate();
      if (!valid) return;
      try {
        await this.saveUserSecurityAnswer(this.nuevaRespuesta);
        this.$emit('show-snackbar', { message: 'Pregunta de seguridad guardada.', color: 'success' });
        this.$refs.formRespuesta.reset();
      } catch (error) {
        this.$emit('show-snackbar', { message: error.message, color: 'error' });
      }
    },
    async eliminarRespuesta(respuestaId) {
      if (confirm('¿Está seguro de que desea eliminar esta pregunta y su respuesta?')) {
        try {
          await this.deleteUserSecurityAnswer(respuestaId);
          this.$emit('show-snackbar', { message: 'Respuesta eliminada.', color: 'success' });
        } catch (error) {
          this.$emit('show-snackbar', { message: error.message, color: 'error' });
        }
      }
    },
  },
  async created() {
    this.authStore = useAuthStore();
    if (!this.authStore.isUserAuthenticated) {
      await this.authStore.initialize();
    }
    await this.cargarPerfilCompleto();
    await this.fetchSecurityQuestions();
    await this.fetchUserSecurityAnswers();
  },
  watch: {
    usuario(val) {
      this.setUsuarioFromStore();
    },
  },
};
</script>
