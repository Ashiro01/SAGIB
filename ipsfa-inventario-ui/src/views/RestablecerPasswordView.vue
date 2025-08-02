<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6" xl="4">
        <!-- Header con logo y título -->
        <div class="text-center mb-8">
          <v-avatar size="80" class="mb-4 elevation-4">
            <v-img src="/logo-ipsfa.png" alt="IPSFA Logo">
              <template v-slot:placeholder>
                <v-icon size="40" color="primary">mdi-shield-lock</v-icon>
              </template>
            </v-img>
          </v-avatar>
          <h1 class="text-h3 font-weight-bold primary--text mb-2">
            Restablecer Contraseña
          </h1>
          <p class="text-body-1 text-grey-darken-1">
            Recupere el acceso a su cuenta de forma segura
          </p>
        </div>

        <!-- Tarjeta principal -->
        <v-card class="elevation-8" rounded="xl">
          <!-- Indicador de progreso -->
          <v-card-title class="d-flex align-center justify-center pa-6 pb-4 bg-gradient">
            <div class="d-flex align-center">
              <v-icon size="24" color="white" class="mr-3">mdi-shield-lock</v-icon>
              <span class="text-h5 font-weight-medium text-white">Paso {{ step }} de 3</span>
            </div>
          </v-card-title>

          <!-- Paso 1: Ingresar usuario -->
          <div v-if="step === 1" class="pa-6">
            <div class="text-center mb-6">
              <v-icon size="64" color="primary" class="mb-4">mdi-account-search</v-icon>
              <h2 class="text-h5 font-weight-medium mb-2">Identificación</h2>
              <p class="text-body-2 text-grey-darken-1">
                Ingrese su nombre de usuario para continuar con el proceso de recuperación
              </p>
            </div>

              <v-form ref="formUsuario" v-model="formUsuarioValido">
                <v-text-field
                  v-model="username"
                  label="Nombre de usuario"
                  :rules="[rules.required]"
                  outlined
                  dense
                prepend-inner-icon="mdi-account"
                class="mb-6"
                hide-details="auto"
                ></v-text-field>
              </v-form>

            <v-btn 
              color="primary" 
              size="large"
              block 
              :loading="isSubmitting" 
              :disabled="!formUsuarioValido" 
              @click="consultarPreguntas"
              prepend-icon="mdi-arrow-right"
              class="mb-4"
              elevation="2"
            >
              Continuar
              </v-btn>

            <v-alert v-if="error" type="error" class="mt-4" variant="tonal">
              <template v-slot:prepend>
                <v-icon>mdi-alert-circle</v-icon>
              </template>
              {{ error }}
            </v-alert>
          </div>

          <!-- Paso 2: Responder preguntas -->
          <div v-if="step === 2" class="pa-6">
            <div class="text-center mb-6">
              <v-icon size="64" color="info" class="mb-4">mdi-shield-question</v-icon>
              <h2 class="text-h5 font-weight-medium mb-2">Verificación de Seguridad</h2>
              <p class="text-body-2 text-grey-darken-1">
                Responda las preguntas de seguridad para verificar su identidad
              </p>
            </div>

            <!-- Contenedor con scroll para las preguntas -->
            <div class="questions-container mb-4">
              <div v-for="(pregunta, idx) in preguntas" :key="pregunta.id" class="mb-4">
                <v-card variant="outlined" class="mb-3" rounded="lg">
                  <v-card-text class="pa-4">
                    <div class="d-flex align-center mb-3">
                      <v-icon color="info" class="mr-2">mdi-help-circle</v-icon>
                      <span class="font-weight-medium text-body-1">{{ pregunta.texto }}</span>
                    </div>
                <v-text-field
                  v-model="respuestas[idx].respuesta_plana"
                      label="Su respuesta"
                  :rules="[rules.required]"
                  outlined
                  dense
                      prepend-inner-icon="mdi-text"
                      hide-details="auto"
                      hint="Sensible a mayúsculas/minúsculas"
                      persistent-hint
                ></v-text-field>
                  </v-card-text>
                </v-card>
              </div>
            </div>

            <!-- Botones fijos en la parte inferior -->
            <div class="buttons-container">
              <div class="d-flex gap-6 justify-center">
                <v-btn 
                  color="secondary" 
                  variant="outlined"
                  height="48"
                  width="150"
                  @click="step = 1"
                  prepend-icon="mdi-arrow-left"
                >
                  Volver
                </v-btn>
                <v-btn 
                  color="info" 
                  height="48"
                  width="150"
                  :loading="isSubmitting" 
                  @click="verificarRespuestas"
                  prepend-icon="mdi-shield-check"
                  elevation="2"
                >
                  Verificar
              </v-btn>
              </div>
            </div>

            <v-alert v-if="error" type="error" class="mt-4" variant="tonal">
              <template v-slot:prepend>
                <v-icon>mdi-alert-circle</v-icon>
              </template>
              {{ error }}
            </v-alert>
          </div>

          <!-- Paso 3: Nueva contraseña -->
          <div v-if="step === 3" class="pa-6">
            <div class="text-center mb-6">
              <v-icon size="64" color="success" class="mb-4">mdi-lock-reset</v-icon>
              <h2 class="text-h5 font-weight-medium mb-2">Nueva Contraseña</h2>
              <p class="text-body-2 text-grey-darken-1">
                Establezca una nueva contraseña segura para su cuenta
              </p>
            </div>

              <v-form ref="formPassword" v-model="formPasswordValido">
                <v-text-field
                  v-model="newPassword"
                  label="Nueva contraseña"
                  type="password"
                  :rules="[rules.required, rules.minLength(8)]"
                  outlined
                  dense
                prepend-inner-icon="mdi-lock-plus"
                class="mb-4"
                hide-details="auto"
                hint="Mínimo 8 caracteres"
                persistent-hint
                ></v-text-field>
              
                <v-text-field
                  v-model="newPasswordConfirm"
                  label="Confirmar nueva contraseña"
                  type="password"
                  :rules="[rules.required, v => v === newPassword || 'Las contraseñas no coinciden.']"
                  outlined
                  dense
                prepend-inner-icon="mdi-lock-check"
                class="mb-6"
                hide-details="auto"
                ></v-text-field>
              </v-form>

            <div class="d-flex gap-6 justify-center">
              <v-btn 
                color="secondary" 
                variant="outlined"
                height="48"
                width="150"
                @click="step = 2"
                prepend-icon="mdi-arrow-left"
              >
                Volver
              </v-btn>
              <v-btn 
                color="success" 
                height="48"
                width="150"
                :loading="isSubmitting" 
                :disabled="!formPasswordValido" 
                @click="restablecerPassword"
                prepend-icon="mdi-check"
                elevation="2"
              >
                Restablecer
              </v-btn>
            </div>

            <v-alert v-if="error" type="error" class="mt-4" variant="tonal">
              <template v-slot:prepend>
                <v-icon>mdi-alert-circle</v-icon>
              </template>
              {{ error }}
            </v-alert>

            <v-alert v-if="exito" type="success" class="mt-4" variant="tonal">
              <template v-slot:prepend>
                <v-icon>mdi-check-circle</v-icon>
              </template>
              {{ exito }}
            </v-alert>
          </div>

          <!-- Mensaje de éxito final -->
          <div v-if="exito && step === 3" class="pa-6 text-center">
            <v-icon size="80" color="success" class="mb-4">mdi-check-circle</v-icon>
            <h2 class="text-h5 font-weight-medium mb-2 text-success">¡Contraseña Restablecida!</h2>
            <p class="text-body-1 text-grey-darken-1 mb-6">
              Su contraseña ha sido actualizada exitosamente. Ya puede iniciar sesión con su nueva contraseña.
            </p>
            <v-btn 
              color="primary" 
              size="large"
              @click="$router.push('/login')"
              prepend-icon="mdi-login"
              elevation="2"
            >
              Ir al Login
            </v-btn>
          </div>
        </v-card>

        <!-- Enlace de regreso -->
        <div class="text-center mt-6">
          <v-btn 
            text 
            color="primary" 
            @click="$router.push('/login')"
            prepend-icon="mdi-arrow-left"
          >
            Volver al Login
          </v-btn>
        </div>
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

<style scoped>
.bg-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.v-card {
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
}

.v-btn {
  border-radius: 8px;
  font-weight: 500;
  text-transform: none;
  letter-spacing: 0.5px;
  transition: all 0.2s ease;
}

.v-btn:hover {
  transform: translateY(-1px);
}

.v-text-field {
  border-radius: 8px;
}

.v-text-field .v-field {
  border-radius: 8px;
}

.v-alert {
  border-radius: 8px;
}

.v-avatar {
  border: 4px solid white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
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

.text-center {
  animation: fadeInUp 0.6s ease-out;
}

/* Estilos para los iconos en los campos */
.v-text-field .v-field__prepend-inner {
  color: rgba(var(--v-theme-primary), 0.7);
}

/* Estilos para las tarjetas de preguntas */
.v-card.variant-outlined {
  border: 1px solid rgba(var(--v-theme-outline), 0.12);
  background: rgba(var(--v-theme-surface), 0.5);
}

/* Responsive design */
@media (max-width: 960px) {
  .d-flex.gap-3 {
    flex-direction: column;
  }
  
  .v-btn {
    margin-bottom: 8px;
  }
}

/* Animación para los botones de acción */
.v-btn {
  position: relative;
  overflow: hidden;
}

.v-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.v-btn:hover::before {
  left: 100%;
}

/* Estilos para el mensaje de éxito */
.text-success {
  color: #4caf50 !important;
}

/* Estilos para los iconos grandes */
.v-icon {
  transition: all 0.3s ease;
}

.v-icon:hover {
  transform: scale(1.1);
}

/* Contenedor de preguntas sin scroll */
.questions-container {
  margin-bottom: 16px;
}



/* Contenedor de botones siempre visible */
.buttons-container {
  position: sticky;
  bottom: 0;
  background: white;
  padding-top: 16px;
  margin-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.12);
  z-index: 10;
}

/* Asegurar que los botones no se superpongan */
.d-flex.gap-3 {
  margin-bottom: 0;
}
</style>
