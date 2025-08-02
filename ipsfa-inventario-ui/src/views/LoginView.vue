<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6" xl="4">
        <!-- Header con logo y título -->
        <div class="text-center mb-8">
          <v-avatar size="100" class="mb-4 elevation-4">
            <v-img src="/logo-ipsfa.png" alt="IPSFA Logo">
              <template v-slot:placeholder>
                <v-icon size="50" color="primary">mdi-shield-lock</v-icon>
              </template>
            </v-img>
          </v-avatar>
          <h1 class="text-h3 font-weight-bold primary--text mb-2">
            SAGIB
          </h1>
          <p class="text-body-1 text-grey-darken-1">
            Sistema Automatizado de Gestión de Inventario de Bienes
          </p>
        </div>

        <!-- Tarjeta principal -->
        <v-card class="elevation-8" rounded="xl">
          <!-- Header de la tarjeta -->
          <v-card-title class="d-flex align-center justify-center pa-6 pb-4 bg-gradient">
            <div class="d-flex align-center">
              <v-icon size="24" color="white" class="mr-3">mdi-login</v-icon>
              <span class="text-h5 font-weight-medium text-white">Inicio de Sesión</span>
            </div>
          </v-card-title>

          <!-- Contenido del formulario -->
          <div class="pa-6">
            <div class="text-center mb-6">
              <v-icon size="64" color="primary" class="mb-4">mdi-account-lock</v-icon>
              <h2 class="text-h5 font-weight-medium mb-2">Acceso al Sistema</h2>
              <p class="text-body-2 text-grey-darken-1">
                Ingrese sus credenciales para acceder a su cuenta
              </p>
            </div>

            <v-form @submit.prevent="handleLogin" ref="loginForm" v-model="validForm">
              <v-text-field
                v-model="credenciales.username"
                label="Nombre de usuario"
                name="login"
                prepend-inner-icon="mdi-account"
                type="text"
                :rules="[rules.required]"
                required
                outlined
                dense
                class="mb-4"
                hide-details="auto"
              ></v-text-field>

              <v-text-field
                v-model="credenciales.password"
                label="Contraseña"
                name="password"
                prepend-inner-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                :rules="[rules.required]"
                required
                outlined
                dense
                class="mb-6"
                hide-details="auto"
              ></v-text-field>

              <v-alert v-if="errorLogin" type="error" class="mb-4" variant="tonal">
                <template v-slot:prepend>
                  <v-icon>mdi-alert-circle</v-icon>
                </template>
                {{ errorLoginMessage }}
              </v-alert>

              <v-btn 
                type="submit" 
                :disabled="!validForm || loading" 
                :loading="loading"
                color="primary" 
                size="large"
                block 
                class="mb-4"
                elevation="2"
                prepend-icon="mdi-login"
              >
                Iniciar Sesión
              </v-btn>
            </v-form>

            <!-- Enlace de restablecer contraseña -->
            <div class="text-center">
              <v-btn 
                text 
                color="primary" 
                @click="$router.push('/restablecer-password')"
                prepend-icon="mdi-help-circle"
                class="text-caption"
              >
                ¿Olvidó su contraseña?
              </v-btn>
            </div>
          </div>
        </v-card>

        <!-- Información adicional -->
        <div class="text-center mt-6">
          <v-chip
            color="info"
            variant="tonal"
            prepend-icon="mdi-information"
            class="mb-2"
          >
            Sistema de Inventario IPSFA
          </v-chip>
          <p class="text-caption text-grey-darken-1">
            Versión 1.0 - Todos los derechos reservados
          </p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';

export default {
  name: 'LoginView',
  data: () => ({
    validForm: false,
    showPassword: false,
    loading: false,
    errorLogin: false,
    errorLoginMessage: '',
    credenciales: {
      username: '',
      password: '',
    },
    rules: {
      required: value => !!value || 'Campo requerido.',
    }
  }),
  methods: {
    async handleLogin() {
      this.errorLogin = false;
      this.errorLoginMessage = '';
      if (this.$refs.loginForm.validate()) {
        this.loading = true;
        const authStore = useAuthStore();
        try {
          const response = await authStore.login(this.credenciales);
          console.log(response.message);
          this.$emit('login-successful');
        } catch (error) {
          this.errorLogin = true;
          this.errorLoginMessage = error.message || 'Error desconocido al iniciar sesión.';
          this.$emit('show-snackbar', {
            message: this.errorLoginMessage,
            color: 'error'
          });
        } finally {
          this.loading = false;
        }
      }
    },
  },
   mounted() {
    // Si por alguna razón el usuario llega aquí y ya está "autenticado" (en nuestra simulación)
    // lo redirigimos al dashboard. Esto necesitaría una forma de verificar el estado de App.vue
    // o un estado global. Por ahora, esta lógica es más compleja de implementar sin un store.
    // if (this.$root.isAuthenticated) { // Esto es una suposición de cómo accederíamos al estado
    //   this.$router.push('/');
    // }
  }
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

/* Estilos para el chip de información */
.v-chip {
  border-radius: 20px;
}

/* Responsive design */
@media (max-width: 960px) {
  .v-avatar {
    size: 80px;
  }
  
  .text-h3 {
    font-size: 2rem !important;
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

/* Estilos para los iconos grandes */
.v-icon {
  transition: all 0.3s ease;
}

.v-icon:hover {
  transform: scale(1.1);
}

.fill-height {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>