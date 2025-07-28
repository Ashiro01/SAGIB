<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Restablecer Contraseña</v-toolbar-title>
          </v-toolbar>

          <!-- Paso 1: Ingresar usuario -->
          <div v-if="step === 1">
            <v-card-text>
              <v-form ref="formUsuario" v-model="formUsuarioValido">
                <v-text-field
                  v-model="username"
                  label="Nombre de usuario"
                  :rules="[rules.required]"
                  outlined
                  dense
                ></v-text-field>
              </v-form>
              <v-btn color="primary" block :loading="isSubmitting" :disabled="!formUsuarioValido" @click="consultarPreguntas">
                Consultar Preguntas
              </v-btn>
              <v-alert v-if="error" type="error" class="mt-2">{{ error }}</v-alert>
            </v-card-text>
          </div>

          <!-- Paso 2: Responder preguntas -->
          <div v-if="step === 2">
            <v-card-text>
              <div v-for="(pregunta, idx) in preguntas" :key="pregunta.id" class="mb-2">
                <strong>{{ pregunta.texto }}</strong>
                <v-text-field
                  v-model="respuestas[idx].respuesta_plana"
                  label="Respuesta"
                  :rules="[rules.required]"
                  outlined
                  dense
                ></v-text-field>
              </div>
              <v-btn color="primary" block :loading="isSubmitting" @click="verificarRespuestas">
                Verificar Respuestas
              </v-btn>
              <v-btn text block class="mt-2" @click="step = 1">Volver</v-btn>
              <v-alert v-if="error" type="error" class="mt-2">{{ error }}</v-alert>
            </v-card-text>
          </div>

          <!-- Paso 3: Nueva contraseña -->
          <div v-if="step === 3">
            <v-card-text>
              <v-form ref="formPassword" v-model="formPasswordValido">
                <v-text-field
                  v-model="newPassword"
                  label="Nueva contraseña"
                  type="password"
                  :rules="[rules.required, rules.minLength(8)]"
                  outlined
                  dense
                ></v-text-field>
                <v-text-field
                  v-model="newPasswordConfirm"
                  label="Confirmar nueva contraseña"
                  type="password"
                  :rules="[rules.required, v => v === newPassword || 'Las contraseñas no coinciden.']"
                  outlined
                  dense
                ></v-text-field>
              </v-form>
              <v-btn color="primary" block :loading="isSubmitting" :disabled="!formPasswordValido" @click="restablecerPassword">
                Restablecer Contraseña
              </v-btn>
              <v-btn text block class="mt-2" @click="step = 2">Volver</v-btn>
              <v-alert v-if="error" type="error" class="mt-2">{{ error }}</v-alert>
              <v-alert v-if="exito" type="success" class="mt-2">{{ exito }}</v-alert>
            </v-card-text>
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
      username: '',
      preguntas: [],
      respuestas: [],
      resetToken: '',
      newPassword: '',
      newPasswordConfirm: '',
      isSubmitting: false,
      error: '',
      exito: '',
      formUsuarioValido: false,
      formPasswordValido: false,
      rules: {
        required: v => !!v || 'Campo requerido.',
        minLength: min => v => (v && v.length >= min) || `Mínimo ${min} caracteres.`,
      },
    };
  },
  methods: {
    async consultarPreguntas() {
      this.error = '';
      this.isSubmitting = true;
      try {
        const authStore = useAuthStore();
        const preguntas = await authStore.getSecurityQuestionsForUser(this.username);
        this.preguntas = preguntas;
        this.respuestas = preguntas.map(p => ({ pregunta_id: p.id, respuesta_plana: '' }));
        this.step = 2;
      } catch (err) {
        this.error = err.response?.data?.error || 'No se pudieron obtener las preguntas.';
      } finally {
        this.isSubmitting = false;
      }
    },
    async verificarRespuestas() {
      this.error = '';
      this.isSubmitting = true;
      try {
        const authStore = useAuthStore();
        const payload = { username: this.username, respuestas: this.respuestas };
        const data = await authStore.verifySecurityAnswers(payload);
        this.resetToken = data.reset_token;
        this.step = 3;
      } catch (err) {
        this.error = err.response?.data?.error || 'Respuestas incorrectas.';
      } finally {
        this.isSubmitting = false;
      }
    },
    async restablecerPassword() {
      this.error = '';
      this.exito = '';
      this.isSubmitting = true;
      try {
        const authStore = useAuthStore();
        const payload = {
          reset_token: this.resetToken,
          new_password: this.newPassword,
          new_password_confirm: this.newPasswordConfirm,
        };
        const data = await authStore.resetPasswordWithToken(payload);
        this.exito = data.status || 'Contraseña restablecida exitosamente.';
        this.step = 3;
      } catch (err) {
        this.error = err.response?.data?.error || 'No se pudo restablecer la contraseña.';
      } finally {
        this.isSubmitting = false;
      }
    },
  },
};
</script>
