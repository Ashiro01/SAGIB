<template>
  <v-app>
    <v-app-bar app color="primary" dark v-if="isAuthenticated">
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>IPSFA - Gestión de Inventario</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-menu offset-y min-width="280" rounded="lg">
        <template v-slot:activator="{ props }">
          <v-btn 
            icon 
            v-bind="props"
            class="user-menu-btn"
            variant="text"
          >
            <v-avatar size="36" v-if="userProfileImage" class="elevation-2">
              <v-img :src="userProfileImage" alt="Foto de Perfil">
                <template v-slot:placeholder>
                  <v-icon size="20" color="grey">mdi-account</v-icon>
                </template>
              </v-img>
            </v-avatar>
            <v-avatar size="36" v-else class="elevation-2">
              <v-icon size="20" color="primary">mdi-account-circle</v-icon>
            </v-avatar>
          </v-btn>
        </template>
        
        <v-card class="user-menu-card" elevation="8" rounded="lg">
          <!-- Header del menú con información del usuario -->
          <div class="user-menu-header pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar size="48" class="mr-3 elevation-3">
                <v-img :src="userProfileImage" v-if="userProfileImage" alt="Foto de Perfil">
                  <template v-slot:placeholder>
                    <v-icon size="24" color="grey">mdi-account</v-icon>
                  </template>
                </v-img>
                <v-icon v-else size="24" color="primary">mdi-account-circle</v-icon>
              </v-avatar>
              <div class="flex-grow-1">
                <h6 class="text-h6 font-weight-bold mb-1">
                  {{ currentUser ? (currentUser.nombre_completo || currentUser.username) : 'Usuario' }}
                </h6>
                <p class="text-body-2 text-grey-darken-1 mb-1">
                  @{{ currentUser ? currentUser.username : '' }}
                </p>
                <v-chip 
                  :color="getRoleColor(currentUser ? currentUser.rol : '')" 
                  size="small" 
                  variant="flat"
                  class="font-weight-medium"
                >
                  <v-icon size="14" class="mr-1">mdi-shield</v-icon>
                  {{ currentUser ? currentUser.rol : 'Usuario' }}
                </v-chip>
              </div>
            </div>
            <v-divider></v-divider>
          </div>

          <!-- Opciones del menú -->
          <v-list class="pa-0" density="compact">
            <v-list-item 
              to="/perfil" 
              link 
              class="user-menu-item"
              prepend-icon="mdi-account-edit-outline"
            >
              <v-list-item-title class="font-weight-medium">Mi Perfil</v-list-item-title>
              <v-list-item-subtitle class="text-caption">Gestionar información personal</v-list-item-subtitle>
            </v-list-item>

            <v-list-item 
              @click="logout" 
              link 
              class="user-menu-item"
              prepend-icon="mdi-logout"
            >
              <v-list-item-title class="font-weight-medium">Cerrar Sesión</v-list-item-title>
              <v-list-item-subtitle class="text-caption">Salir de la aplicación</v-list-item-subtitle>
            </v-list-item>
          </v-list>
        </v-card>
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
    userProfileImage() {
      const user = this.currentUser;
      if (user && user.perfil && user.perfil.foto_perfil) {
        return `http://127.0.0.1:8000${user.perfil.foto_perfil}`;
      }
      return null;
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
    getRoleColor(role) {
      const roleColors = {
        'Administrador': 'error',
        'Auditor': 'warning',
        'Consultor': 'info',
        'Usuario': 'info',
        'Supervisor': 'success',
        'default': 'grey'
      };
      return roleColors[role] || roleColors.default;
    },
  },
  watch: {
    isAuthenticated(val) {
      if (!val) {
        this.$router.push('/login');
      }
    },
    currentUser: {
      handler(newUser) {
        // El usuario se actualizó, la interfaz se actualizará automáticamente
      },
      deep: true
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
/* Estilos para el mini menú del usuario */
.user-menu-btn {
  transition: all 0.2s ease;
}

.user-menu-btn:hover {
  transform: scale(1.05);
}

.user-menu-card {
  border-radius: 16px !important;
  overflow: hidden;
}

.user-menu-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.user-menu-item {
  transition: all 0.2s ease;
  border-radius: 8px;
  margin: 2px 8px;
}

.user-menu-item:hover {
  background-color: rgba(var(--v-theme-primary), 0.1) !important;
  transform: translateX(4px);
}

.user-menu-item .v-list-item-title {
  font-weight: 500;
  color: rgba(var(--v-theme-on-surface), 0.87);
}

.user-menu-item .v-list-item-subtitle {
  color: rgba(var(--v-theme-on-surface), 0.6);
  font-size: 0.75rem;
}

/* Animación de entrada para el menú */
.v-menu__content {
  animation: slideInDown 0.3s ease-out;
}

@keyframes slideInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Estilos para el chip del rol */
.v-chip {
  font-weight: 500;
  letter-spacing: 0.5px;
}

/* Responsive design para el menú */
@media (max-width: 600px) {
  .user-menu-card {
    min-width: 260px;
  }
  
  .user-menu-header {
    padding: 16px !important;
  }
  
  .user-menu-item {
    margin: 1px 4px;
  }
}
</style>