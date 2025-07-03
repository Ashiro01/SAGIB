<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Inicio de Sesión - IPSFANB</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <div class="text-center mb-4 mt-2">
              <img src="/logo-ipsfa.png" alt="Logo IPSFA" style="max-height: 80px;"/>
            </div>
            <v-form @submit.prevent="handleLogin" ref="loginForm" v-model="validForm">
              <v-text-field
                label="Usuario"
                v-model="credenciales.username"
                name="login"
                prepend-icon="mdi-account"
                type="text"
                :rules="[rules.required]"
                required
                outlined
                class="mb-3"
              ></v-text-field>

              <v-text-field
                label="Contraseña"
                v-model="credenciales.password"
                name="password"
                prepend-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append="showPassword = !showPassword"
                :rules="[rules.required]"
                required
                outlined
              ></v-text-field>

              <v-alert v-if="errorLogin" type="error" dense text class="mt-3 mb-3">
                {{ errorLoginMessage }}
              </v-alert>

              <v-btn 
                type="submit" 
                :disabled="!validForm || loading" 
                :loading="loading"
                color="primary" 
                block 
                large 
                class="mt-4"
              >
                Iniciar Sesión
              </v-btn>
            </v-form>
          </v-card-text>
          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <a href="#" class="caption">¿Olvidó su contraseña?</a>
          </v-card-actions>
        </v-card>
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
.fill-height {
  min-height: 100vh; /* Asegura que ocupe toda la altura de la vista */
}
.v-card-actions a {
    text-decoration: none;
}
</style>