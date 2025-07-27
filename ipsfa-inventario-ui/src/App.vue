<template>
  <v-app>
    <v-app-bar app color="primary" dark v-if="isAuthenticated">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>IPSFA - Gestión de Inventario</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-menu offset-y>
        <template v-slot:activator="{ props }">
          <v-btn icon v-bind="props">
            <v-icon>mdi-account-circle</v-icon>
          </v-btn>
        </template>
        <v-list dense>
          <v-list-item>
            <v-list-item-title>Usuario: {{ currentUser ? (currentUser.nombre_completo || currentUser.username) : '' }}</v-list-item-title>
          </v-list-item>
          <v-list-item>
            <v-list-item-subtitle>Rol: {{ currentUser ? currentUser.rol : '' }}</v-list-item-subtitle>
          </v-list-item>
          <v-divider></v-divider>
          <v-list-item to="/perfil" link>
            <template v-slot:prepend>
              <v-icon>mdi-account-edit-outline</v-icon>
            </template>
            <v-list-item-title>Mi Perfil</v-list-item-title>
          </v-list-item>
          <v-list-item @click="logout" link>
            <template v-slot:prepend>
              <v-icon>mdi-logout</v-icon>
            </template>
            <v-list-item-title>Cerrar Sesión</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <v-navigation-drawer app v-model="drawer" temporary v-if="isAuthenticated">
      <v-list-item>
        <div>
          <v-list-item-title class="text-h6">
            Menú Principal
          </v-list-item-title>
          <v-list-item-subtitle>
            IPSFA
          </v-list-item-subtitle>
        </div>
      </v-list-item>
      <v-divider></v-divider>
      <v-list dense nav>
        <v-list-item
          v-for="item in menuItems"
          :key="item.title"
          :to="item.route"
          link
        >
          <template v-slot:prepend>
            <v-icon :icon="item.icon"></v-icon>
          </template>
          <v-list-item-title>{{ item.title }}</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-main :class="{ 'main-content-with-watermark': isAuthenticated }">
      <v-container fluid v-if="isAuthenticated && breadcrumbItems.length > 0" class="pa-0 ma-0">
        <v-breadcrumbs :items="breadcrumbItems" class="pa-2 elevation-1 mb-2" style="background-color: #f5f5f5;">
          <template v-slot:divider>
            <v-icon>mdi-chevron-right</v-icon>
          </template>
          <template v-slot:item="{ item }">
            <v-breadcrumbs-item
              :to="item.to"
              :disabled="item.disabled"
              :exact="item.exact"
            >
              {{ item.text.toUpperCase() }}
            </v-breadcrumbs-item>
          </template>
        </v-breadcrumbs>
      </v-container>
      <v-container fluid>
        <router-view @login-successful="handleLoginSuccess" @show-snackbar="showSnackbar"></router-view>
      </v-container>
    </v-main>

    <v-footer app padless v-if="isAuthenticated">
      <v-col class="text-center" cols="12">
        {{ new Date().getFullYear() }} — <strong>IPSFA</strong>
      </v-col>
    </v-footer>

    <v-snackbar
      v-model="snackbar.visible"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top right"
      variant="elevated"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn icon @click="snackbar.visible = false">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-snackbar>

  </v-app>
</template>

<script>
import { useAuthStore } from './stores/authStore';

export default {
  name: 'App',
  data: () => ({
    drawer: null,
    menuItems: [
      { title: 'Dashboard', icon: 'mdi-view-dashboard', route: '/' },
      { title: 'Bienes', icon: 'mdi-archive', route: '/bienes' },
      { title: 'Proveedores', icon: 'mdi-store-outline', route: '/proveedores' },
      { title: 'Traslados', icon: 'mdi-swap-horizontal-bold', route: '/traslados/nuevo' },
      { title: 'Desincorporaciones', icon: 'mdi-archive-arrow-down-outline', route: '/desincorporaciones/nueva' },
      { title: 'Reportes', icon: 'mdi-chart-bar', route: '/reportes' },
      { title: 'Cálculo de Depreciación', icon: 'mdi-calculator', route: '/depreciacion', roles: ['Administrador'] },
      { title: 'Gestión de Usuarios', icon: 'mdi-account-group-outline', route: '/usuarios', roles: ['Administrador'] },
      { title: 'Gestión de Roles', icon: 'mdi-shield-key-outline', route: '/roles', roles: ['Administrador'] },
      { title: 'Unidades Administrativas', icon: 'mdi-office-building-outline', route: '/unidades-administrativas' },
      { title: 'Logs de Auditoría', icon: 'mdi-text-box-search-outline', route: '/audit-logs', roles: ['Administrador', 'Auditor'] },
      { title: 'Carga Masiva', icon: 'mdi-upload', route: '/bienes/carga-masiva' },
      { title: 'Configuración', icon: 'mdi-cog-outline', route: '/configuracion' }
    ],
    snackbar: {
      visible: false,
      message: '',
      color: 'info',
      timeout: 3000,
    },
  }),
  computed: {
    isAuthenticated() {
      const authStore = useAuthStore();
      return authStore.isUserAuthenticated;
    },
    currentUser() {
      const authStore = useAuthStore();
      return authStore.getCurrentUser;
    },
    breadcrumbItems() {
      const matchedRoutes = this.$route.matched;
      const breadcrumbs = [];
      if (this.$route.name !== 'dashboard' && this.isAuthenticated) {
        breadcrumbs.push({
          text: 'Dashboard',
          to: { name: 'dashboard' },
          disabled: false,
          exact: true
        });
      }
      matchedRoutes.forEach(route => {
        if (route.meta && route.meta.breadcrumb && (route.name !== 'dashboard' || breadcrumbs.length === 0)) {
          if (route.name === 'dashboard' && breadcrumbs.some(b => b.name === 'dashboard')) return;
          let text = route.meta.breadcrumb;
          breadcrumbs.push({
            text: text,
            to: { name: route.name, params: this.$route.params },
            disabled: route.path === this.$route.path,
            exact: true
          });
        }
      });
      return breadcrumbs;
    }
  },
  methods: {
    handleLoginSuccess() {
      // El estado de autenticación ya fue manejado por el store desde LoginView.
      // App.vue simplemente reacciona a ese estado a través de las propiedades computadas.
      // Aquí solo necesitamos redirigir si es necesario.
      console.log('App.vue: Login successful event received. User should be authenticated via store.');
      this.$router.push('/');
      const authStore = useAuthStore();
      const user = authStore.getCurrentUser;
      if (user) {
        this.showSnackbar({
          message: `¡Bienvenido de nuevo, ${user.nombre_completo || user.username}!`,
          color: 'success'
        });
      }
    },
    logout() {
      const authStore = useAuthStore();
      authStore.logout();
      this.showSnackbar({
        message: 'Sesión cerrada exitosamente.',
        color: 'info'
      });
    },
    showSnackbar(payload) {
      this.snackbar.message = payload.message || 'Mensaje no especificado.';
      this.snackbar.color = payload.color || 'info';
      this.snackbar.timeout = payload.timeout || 3000;
      this.snackbar.visible = true;
    },
  },
  watch: {
    isAuthenticated(val) {
      if (!val) {
        this.$router.push('/login');
      }
    }
  },
  mounted() {
    if (!this.isAuthenticated) {
      this.$router.push('/login');
    }
  },
  created() {
    // Restaurar autenticación al recargar la página
    const authStore = useAuthStore();
    authStore.initialize();
  },
};
</script>

<style>
/* Estilos globales muy básicos si los necesitas, por ahora vacío */
</style>