<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="5">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Restablecer Contraseña</v-toolbar-title>
            <v-spacer></v-spacer>
            <v-btn icon to="/login" title="Volver a Inicio de Sesión">
              <v-icon>mdi-login</v-icon>
            </v-btn>
          </v-toolbar>

          <div v-if="step === 1">
            <v-card-text class="pa-5">
              <p class="mb-4">Por favor, ingrese su nombre de usuario para buscar sus preguntas de seguridad.</p>
              <v-form ref="formUsuario" @submit.prevent="buscarUsuario">
                <v-text-field
                  v-model="username"
                  label="Nombre de Usuario"
                  prepend-inner-icon="mdi-account"
                  outlined
                  dense
                  required
                  :rules="[rules.required]"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions class="pa-4">
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="buscarUsuario" :loading="loading">Buscar</v-btn>
            </v-card-actions>
          </div>

          <div v-if="step === 2">
            <v-card-text class="pa-5">
              <p class="mb-4">Responda a las siguientes preguntas para verificar su identidad.</p>
              <v-form ref="formRespuestas" @submit.prevent="verificarRespuestas">
                <div v-for="(pregunta, index) in preguntas" :key="pregunta.id">
                  <label class="font-weight-medium">{{ pregunta.texto }}</label>
                  <v-text-field
                    v-model="respuestas[index].respuesta_plana"
                    label="Su respuesta"
                    outlined
                    dense
                    required
                    :rules="[rules.required]"
                    class="mb-3"
                  ></v-text-field>
                </div>
              </v-form>
            </v-card-text>
            <v-card-actions class="pa-4">
              <v-btn text @click="step = 1">Volver</v-btn>
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="verificarRespuestas" :loading="loading">Verificar Respuestas</v-btn>
            </v-card-actions>
          </div>

          <div v-if="step === 3">
            <v-card-text class="pa-5">
              <p class="mb-4">Verificación exitosa. Por favor, establezca su nueva contraseña.</p>
              <v-form ref="formPassword" @submit.prevent="restablecerPassword">
                <v-text-field
                  v-model="passwordData.new_password"
                  label="Nueva Contraseña"
                  type="password"
                  :rules="[rules.required, rules.minLength(8)]"
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
            <v-card-actions class="pa-4">
              <v-spacer></v-spacer>
              <v-btn color="primary" @click="restablecerPassword" :loading="loading">Restablecer Contraseña</v-btn>
            </v-card-actions>
          </div>

          <div v-if="step === 4">
            <v-card-text class="pa-5 text-center">
              <v-icon size="64" color="success" class="mb-4">mdi-check-circle-outline</v-icon>
              <h3 class="text-h6">¡Éxito!</h3>
              <p>Su contraseña ha sido restablecida correctamente.</p>
            </v-card-text>
            <v-card-actions class="pa-4">
                <v-spacer></v-spacer>
                <v-btn color="primary" to="/login">Ir a Inicio de Sesión</v-btn>
                <v-spacer></v-spacer>
            </v-card-actions>
          </div>

        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'RestablecerPasswordView',
  data() {
    return {
      step: 1,
      loading: false,
      username: '',
      preguntas: [], // Almacenará las preguntas del usuario [{id, texto}]
      respuestas: [], // Almacenará las respuestas del usuario [{pregunta_id, respuesta_plana}]
      reset_token: null,
      passwordData: {
        new_password: '',
        new_password_confirm: '',
      },
      rules: {
        required: value => !!value || 'Campo requerido.',
        minLength: min => v => (v && v.length >= min) || `Mínimo ${min} caracteres.`,
        passwordMatch: () => this.passwordData.new_password === this.passwordData.new_password_confirm || 'Las contraseñas no coinciden.',
      },
    };
  },
  methods: {
    async buscarUsuario() {
      const { valid } = await this.$refs.formUsuario.validate();
      if (!valid) return;

      this.loading = true;
      const authStore = useAuthStore();
      try {
        const preguntas = await authStore.getSecurityQuestionsForUser(this.username);
        this.preguntas = preguntas;
        // Preparamos el array de respuestas para vincularlo al formulario
        this.respuestas = this.preguntas.map(p => ({ pregunta_id: p.id, respuesta_plana: '' }));
        this.step = 2;
      } catch (error) {
        this.$emit('show-snackbar', { message: error.response?.data?.error || 'Error al buscar el usuario.', color: 'error' });
      } finally {
        this.loading = false;
      }
    },
    async verificarRespuestas() {
      const { valid } = await this.$refs.formRespuestas.validate();
      if (!valid) return;

      this.loading = true;
      const authStore = useAuthStore();
      const payload = {
        username: this.username,
        respuestas: this.respuestas,
      };
      try {
        const data = await authStore.verifySecurityAnswers(payload);
        this.reset_token = data.reset_token;
        this.step = 3;
      } catch (error) {
        this.$emit('show-snackbar', { message: error.response?.data?.error || 'Error al verificar las respuestas.', color: 'error' });
      } finally {
        this.loading = false;
      }
    },
    async restablecerPassword() {
      const { valid } = await this.$refs.formPassword.validate();
      if (!valid) return;

      this.loading = true;
      const authStore = useAuthStore();
      const payload = {
        reset_token: this.reset_token,
        ...this.passwordData,
      };
      try {
        await authStore.resetPasswordWithToken(payload);
        this.step = 4;
      } catch (error) {
        this.$emit('show-snackbar', { message: error.response?.data?.error || 'Error al restablecer la contraseña.', color: 'error' });
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>