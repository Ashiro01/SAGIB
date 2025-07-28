<template>
  <v-container fluid class="pa-6">
    <!-- Header con información del usuario -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div class="d-flex align-center mb-4">
          <v-avatar size="80" class="mr-4 elevation-4">
            <v-img :src="fotoUrl" alt="Foto de Perfil">
              <template v-slot:placeholder>
                <v-icon size="40" color="grey">mdi-account</v-icon>
              </template>
            </v-img>
          </v-avatar>
          <div>
            <h1 class="text-h3 font-weight-bold primary--text mb-1">
              {{ perfilData.first_name }} {{ perfilData.last_name }}
            </h1>
            <p class="text-h6 text-grey-darken-1 mb-1">@{{ perfilData.username }}</p>
            <p class="text-body-1 text-grey-darken-2">
              <v-icon size="16" class="mr-1">mdi-email</v-icon>
              {{ perfilData.email }}
            </p>
          </div>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <!-- Columna izquierda - Foto de perfil y datos personales -->
      <v-col cols="12" lg="6">
        <!-- Tarjeta de foto de perfil -->
        <v-card class="mb-6" elevation="2" rounded="lg">
          <v-card-title class="d-flex align-center pa-6 pb-4">
            <v-icon size="24" color="primary" class="mr-3">mdi-camera</v-icon>
            <span class="text-h5 font-weight-medium">Foto de Perfil</span>
          </v-card-title>
          <v-card-text class="pa-6 pt-0">
            <div class="text-center">
              <v-avatar size="200" class="mb-6 elevation-6">
                <v-img :src="fotoUrl" alt="Foto de Perfil">
                  <template v-slot:placeholder>
                    <v-icon size="60" color="grey">mdi-account</v-icon>
                  </template>
                </v-img>
              </v-avatar>
              
              <v-file-input
                v-model="fotoSeleccionada"
                label="Seleccionar nueva foto"
                accept="image/png, image/jpeg, image/jpg"
                prepend-icon="mdi-camera-plus"
                outlined
                dense
                hide-details
                class="mb-4"
                @change="previsualizarFoto"
                :rules="[rules.imageFile]"
              ></v-file-input>
              
              <v-btn 
                color="primary" 
                size="large"
                :loading="isSubmitting" 
                :disabled="!fotoSeleccionada"
                @click="subirFoto"
                prepend-icon="mdi-upload"
                class="px-8"
              >
                Actualizar Foto
              </v-btn>
            </div>
          </v-card-text>
        </v-card>

        <!-- Tarjeta de datos personales -->
        <v-card elevation="2" rounded="lg">
          <v-card-title class="d-flex align-center justify-space-between pa-6 pb-4">
            <div class="d-flex align-center">
              <v-icon size="24" color="primary" class="mr-3">mdi-account-edit</v-icon>
              <span class="text-h5 font-weight-medium">Datos Personales</span>
            </div>
            <v-btn 
              icon 
              @click="toggleEditDatos" 
              v-if="!editandoDatos"
              color="primary"
              variant="text"
            >
              <v-icon>mdi-pencil</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-text class="pa-6 pt-0">
            <v-form ref="formDatos" v-model="formDatosValido">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="perfilData.username"
                    label="Nombre de Usuario"
                    readonly
                    disabled
                    outlined
                    dense
                    prepend-inner-icon="mdi-account"
                    class="mb-4"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="perfilData.email"
                    label="Correo Electrónico"
                    type="email"
                    :rules="[rules.required, rules.email]"
                    outlined
                    dense
                    :readonly="!editandoDatos"
                    prepend-inner-icon="mdi-email"
                    class="mb-4"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="perfilData.first_name"
                    label="Nombre(s)"
                    :rules="[rules.required]"
                    outlined
                    dense
                    :readonly="!editandoDatos"
                    prepend-inner-icon="mdi-account"
                    class="mb-4"
                  ></v-text-field>
                </v-col>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="perfilData.last_name"
                    label="Apellido(s)"
                    :rules="[rules.required]"
                    outlined
                    dense
                    :readonly="!editandoDatos"
                    prepend-inner-icon="mdi-account"
                    class="mb-4"
                  ></v-text-field>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions v-if="editandoDatos" class="pa-6 pt-0">
            <v-spacer></v-spacer>
            <v-btn 
              color="secondary" 
              variant="outlined"
              @click="cancelarEdicionDatos" 
              :disabled="isSubmitting"
              class="mr-3"
            >
              Cancelar
            </v-btn>
            <v-btn 
              color="primary" 
              @click="actualizarDatos" 
              :loading="isSubmitting" 
              :disabled="!formDatosValido"
              prepend-icon="mdi-content-save"
            >
              Guardar Cambios
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <!-- Columna derecha - Contraseña y preguntas de seguridad -->
      <v-col cols="12" lg="6">
        <!-- Tarjeta de cambio de contraseña -->
        <v-card class="mb-6" elevation="2" rounded="lg">
          <v-card-title class="d-flex align-center pa-6 pb-4">
            <v-icon size="24" color="warning" class="mr-3">mdi-lock-reset</v-icon>
            <span class="text-h5 font-weight-medium">Cambiar Contraseña</span>
          </v-card-title>
          <v-card-text class="pa-6 pt-0">
            <v-form ref="formPassword" v-model="formPasswordValido">
              <v-text-field
                v-model="passwordData.old_password"
                label="Contraseña Actual"
                type="password"
                :rules="[rules.required]"
                outlined
                dense
                prepend-inner-icon="mdi-lock"
                class="mb-4"
              ></v-text-field>
              <v-text-field
                v-model="passwordData.new_password"
                label="Nueva Contraseña"
                type="password"
                :rules="[rules.required, rules.minLength(8)]"
                hint="Mínimo 8 caracteres"
                outlined
                dense
                prepend-inner-icon="mdi-lock-plus"
                class="mb-4"
              ></v-text-field>
              <v-text-field
                v-model="passwordData.new_password_confirm"
                label="Confirmar Nueva Contraseña"
                type="password"
                :rules="[rules.required, rules.passwordMatch]"
                outlined
                dense
                prepend-inner-icon="mdi-lock-check"
                class="mb-4"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions class="pa-6 pt-0">
            <v-spacer></v-spacer>
            <v-btn 
              color="warning" 
              @click="guardarCambioContraseña" 
              :loading="isSubmitting" 
              :disabled="!formPasswordValido"
              prepend-icon="mdi-lock-reset"
            >
              Cambiar Contraseña
            </v-btn>
          </v-card-actions>
        </v-card>

<<<<<<< HEAD
        <!-- Tarjeta de preguntas de seguridad -->
        <v-card elevation="2" rounded="lg">
          <v-card-title class="d-flex align-center pa-6 pb-4">
            <v-icon size="24" color="info" class="mr-3">mdi-shield-question</v-icon>
            <span class="text-h5 font-weight-medium">Preguntas de Seguridad</span>
          </v-card-title>
          <v-card-subtitle class="pa-6 pt-0 pb-4">
            <v-icon size="16" class="mr-1">mdi-information</v-icon>
            Añada hasta 3 preguntas para recuperar su cuenta en caso de olvido de contraseña.
          </v-card-subtitle>
          <v-card-text class="pa-6 pt-0">
            <!-- Lista de preguntas existentes -->
            <div v-if="respuestasUsuario.length > 0" class="mb-6">
              <h6 class="text-h6 mb-3 text-grey-darken-1">Preguntas Configuradas</h6>
              <v-list lines="two" class="bg-grey-lighten-5 rounded-lg">
                <v-list-item
                  v-for="respuesta in respuestasUsuario"
                  :key="respuesta.id"
                  class="mb-2"
                >
                  <template v-slot:prepend>
                    <v-icon color="success" class="mr-3">mdi-check-circle</v-icon>
                  </template>
                  <v-list-item-title class="font-weight-medium">
                    {{ respuesta.pregunta_texto }}
                  </v-list-item-title>
                  <v-list-item-subtitle class="text-grey-darken-1">
                    Respuesta registrada (oculta por seguridad)
                  </v-list-item-subtitle>
                  <template v-slot:append>
                    <v-btn
                      color="error"
                      icon="mdi-delete-outline"
                      variant="text"
                      @click="eliminarRespuesta(respuesta.id)"
                      :loading="isSubmitting"
                      size="small"
                    ></v-btn>
                  </template>
                </v-list-item>
              </v-list>
            </div>

            <!-- Mensaje cuando no hay preguntas -->
            <div v-else class="text-center py-8">
              <v-icon size="48" color="grey-lighten-1" class="mb-3">mdi-shield-off</v-icon>
              <p class="text-grey-darken-1">Aún no ha añadido ninguna pregunta de seguridad.</p>
            </div>

            <!-- Formulario para añadir nueva pregunta -->
            <div v-if="respuestasUsuario.length < 3" class="mt-6">
              <v-divider class="mb-4"></v-divider>
              <h6 class="text-h6 mb-3 text-grey-darken-1">
                <v-icon size="20" class="mr-2">mdi-plus-circle</v-icon>
                Añadir Nueva Pregunta
              </h6>
=======
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
>>>>>>> 8fa146e0b4882641682ef1184d6a54b651e56746
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
<<<<<<< HEAD
                  prepend-inner-icon="mdi-help-circle"
                  no-data-text="No hay más preguntas disponibles"
                  class="mb-4"
                ></v-select>
                <v-text-field
                  v-model="nuevaRespuesta.respuesta_plana"
                  label="Su respuesta"
                  :rules="[rules.required]"
                  outlined
                  dense
                  prepend-inner-icon="mdi-text"
                  hint="Sensible a mayúsculas/minúsculas"
                  class="mb-4"
                ></v-text-field>
              </v-form>
              <div class="text-right">
                <v-btn
                  color="info"
                  @click="guardarRespuesta"
                  :loading="isSubmitting"
                  :disabled="!formRespuestaValido"
                  prepend-icon="mdi-shield-plus"
                >
                  Guardar Pregunta
                </v-btn>
              </div>
            </div>

            <!-- Mensaje cuando ya tiene 3 preguntas -->
            <div v-else class="text-center py-4">
              <v-icon size="32" color="success" class="mb-2">mdi-shield-check</v-icon>
              <p class="text-success font-weight-medium">Ya tiene configuradas las 3 preguntas de seguridad.</p>
=======
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
>>>>>>> 8fa146e0b4882641682ef1184d6a54b651e56746
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
        imageFile: value => !value || value.size <= 5 * 1024 * 1024 || 'La foto debe ser menor a 5MB.',
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
<<<<<<< HEAD
        this.$emit('show-snackbar', { message: 'Foto de perfil actualizada exitosamente.', color: 'success' });
=======
        this.$emit('show-snackbar', { message: 'Foto de perfil actualizada.', color: 'success' });
>>>>>>> 8fa146e0b4882641682ef1184d6a54b651e56746
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

<style scoped>
.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15) !important;
}

.v-avatar {
  transition: all 0.3s ease;
}

.v-avatar:hover {
  transform: scale(1.05);
}

.v-btn {
  transition: all 0.2s ease;
}

.v-btn:hover {
  transform: translateY(-1px);
}

.v-list-item {
  transition: all 0.2s ease;
}

.v-list-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.05) !important;
}

/* Animación para el header */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.d-flex.align-center {
  animation: fadeInUp 0.6s ease-out;
}

/* Estilos para los iconos en los campos */
.v-text-field .v-field__prepend-inner {
  color: rgba(var(--v-theme-primary), 0.7);
}

/* Estilos para las tarjetas con bordes redondeados */
.v-card {
  border-radius: 16px !important;
}

/* Estilos para los botones con mejor apariencia */
.v-btn {
  border-radius: 8px;
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0.5px;
}

/* Estilos para los campos de formulario */
.v-text-field .v-field {
  border-radius: 8px;
}

/* Estilos para el avatar principal */
.v-avatar {
  border: 4px solid white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* Estilos para las preguntas de seguridad */
.v-list {
  border-radius: 12px;
}

/* Estilos para los mensajes de estado */
.text-center {
  border-radius: 12px;
  padding: 24px;
}

/* Responsive design */
@media (max-width: 960px) {
  .d-flex.align-center {
    flex-direction: column;
    text-align: center;
  }
  
  .v-avatar {
    margin-bottom: 16px;
  }
}

/* Animación para los botones de acción */
.v-card-actions .v-btn {
  position: relative;
  overflow: hidden;
}

.v-card-actions .v-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.v-card-actions .v-btn:hover::before {
  left: 100%;
}
</style>
