import RestablecerPasswordView from '../views/RestablecerPasswordView.vue';

import { createRouter, createWebHistory } from 'vue-router'
import BienDetailView from '../views/BienDetailView.vue'
import PerfilView from '../views/PerfilView.vue';
import DashboardView from '../views/DashboardView.vue'
import BienesListView from '../views/BienesListView.vue'
import BienFormView from '../views/BienFormView.vue'
import ProveedorListView from '../views/ProveedorListView.vue';
import ProveedorFormView from '../views/ProveedorFormView.vue';
import ProveedorDetailView from '../views/ProveedorDetailView.vue';
import TrasladoFormView from '../views/TrasladoFormView.vue';
import DesincorporacionFormView from '../views/DesincorporacionFormView.vue';
import ReportesView from '../views/ReportesView.vue';
import LoginView from '../views/LoginView.vue';
import UsuarioListView from '../views/UsuarioListView.vue';
import UsuarioFormView from '../views/UsuarioFormView.vue';
import RolListView from '../views/RolListView.vue';
import RolFormView from '../views/RolFormView.vue';
import CargaMasivaView from '../views/CargaMasivaView.vue';
import { useAuthStore } from '../stores/authStore';
import UnidadAdministrativaListView from '../views/UnidadAdministrativaListView.vue';
import UnidadAdministrativaFormView from '../views/UnidadAdministrativaFormView.vue';
import AuditLogView from '../views/AuditLogView.vue';
import CalcularDepreciacionView from '../views/CalcularDepreciacionView.vue';

const routes = [
  {
    path: '/restablecer-password',
    name: 'restablecerPassword',
    component: RestablecerPasswordView,
    meta: { breadcrumb: 'Restablecer Contraseña' }
  },
  {
    path: '/perfil',
    name: 'perfil',
    component: PerfilView,
    meta: { requiresAuth: true, breadcrumb: 'Mi Perfil' }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/',
    name: 'dashboard',
    component: DashboardView,
    meta: { requiresAuth: true, breadcrumb: 'Dashboard' }
  },
  {
    path: '/bienes',
    name: 'bienes',
    component: BienesListView,
    meta: { requiresAuth: true, breadcrumb: 'Bienes' }
  },
  {
    path: '/bienes/registrar',
    name: 'registrarBien',
    component: BienFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Bien' }
  },
  {
    path: '/bienes/detalle/:id',
    name: 'detalleBien',
    component: BienDetailView,
    props: true,
    meta: { requiresAuth: true, breadcrumb: 'Detalle del Bien' }
  },
  {
    path: '/bienes/editar/:id',
    name: 'editarBien',
    component: BienFormView,
    props: true,
    meta: { requiresAuth: true, breadcrumb: 'Editar Bien' }
  },
  {
    path: '/proveedores',
    name: 'proveedores',
    component: ProveedorListView,
    meta: { requiresAuth: true, breadcrumb: 'Proveedores' }
  },
  {
    path: '/proveedores/registrar',
    name: 'registrarProveedor',
    component: ProveedorFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Proveedor' }
  },
  {
    path: '/proveedores/editar/:id',
    name: 'editarProveedor',
    component: ProveedorFormView,
    props: true,
    meta: { requiresAuth: true, breadcrumb: 'Editar Proveedor' }
  },
  {
    path: '/proveedores/detalle/:id',
    name: 'detalleProveedor',
    component: ProveedorDetailView,
    props: true,
    meta: { requiresAuth: true, breadcrumb: 'Detalle del Proveedor' }
  },
  {
    path: '/traslados/nuevo',
    name: 'registrarTraslado',
    component: TrasladoFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Traslado' }
  },
  {
    path: '/desincorporaciones/nueva',
    name: 'registrarDesincorporacion',
    component: DesincorporacionFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Desincorporación' }
  },
  {
    path: '/reportes',
    name: 'reportes',
    component: ReportesView,
    meta: { requiresAuth: true, breadcrumb: 'Reportes' }
  },
  {
    path: '/usuarios',
    name: 'usuarios',
    component: UsuarioListView,
    meta: { requiresAuth: true, breadcrumb: 'Usuarios' }
  },
  {
    path: '/usuarios/registrar',
    name: 'registrarUsuario',
    component: UsuarioFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Usuario' }
  },
  {
    path: '/usuarios/editar/:id',
    name: 'editarUsuario',
    component: UsuarioFormView,
    meta: { requiresAuth: true, breadcrumb: 'Editar Usuario' },
    props: true
  },
  {
    path: '/roles',
    name: 'roles',
    component: RolListView,
    meta: { requiresAuth: true, breadcrumb: 'Gestión de Roles' }
  },
  {
    path: '/roles/registrar',
    name: 'registrarRol',
    component: RolFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Rol' }
  },
  {
    path: '/roles/editar/:id',
    name: 'editarRol',
    component: RolFormView,
    meta: { requiresAuth: true, breadcrumb: 'Editar Rol' },
    props: true
  },
  {
    path: '/bienes/carga-masiva',
    name: 'cargaMasivaBienes',
    component: CargaMasivaView,
    meta: { requiresAuth: true, breadcrumb: 'Carga Masiva de Bienes' }
  },
  {
    path: '/unidades-administrativas',
    name: 'unidadesAdministrativas',
    component: UnidadAdministrativaListView,
    meta: { requiresAuth: true, breadcrumb: 'Unidades Administrativas' }
  },
  {
    path: '/unidades-administrativas/registrar',
    name: 'registrarUnidadAdministrativa',
    component: UnidadAdministrativaFormView,
    meta: { requiresAuth: true, breadcrumb: 'Registrar Unidad' }
  },
  {
    path: '/unidades-administrativas/editar/:id',
    name: 'editarUnidadAdministrativa',
    component: UnidadAdministrativaFormView,
    meta: { requiresAuth: true, breadcrumb: 'Editar Unidad' },
    props: true
  },
  {
  path: '/audit-logs',
  name: 'auditLogs',
  component: AuditLogView,
  meta: { requiresAuth: true, breadcrumb: 'Logs de Auditoría' }
  },
  {
    path: '/depreciacion',
    name: 'calcularDepreciacion',
    component: CalcularDepreciacionView,
    meta: { requiresAuth: true, breadcrumb: 'Cálculo de Depreciación' }
  },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Protección de rutas
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !authStore.isUserAuthenticated) {
    console.log('Router Guard: Ruta requiere autenticación y usuario no logueado. Redirigiendo a /login.');
    next({ name: 'login' });
  } else if (to.name === 'login' && authStore.isUserAuthenticated) {
    console.log('Router Guard: Usuario logueado intentando acceder a /login. Redirigiendo a /dashboard.');
    next({ name: 'dashboard' });
  } else {
    next();
  }
});

export default router