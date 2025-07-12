// Vuetify plugin setup for Vue 3
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css';

// Paleta de colores sugerida (puedes ajustarla)
const ipsfaTheme = {
  dark: false, // Puedes experimentar con un tema oscuro si lo deseas (true/false)
  colors: {
    primary: '#0D47A1',   // Azul Marino Intenso
    secondary: '#1E88E5', // Azul Cielo Medio
    accent: '#FDD835',    // Amarillo Oro
    error: '#B71C1C',     // Rojo Ladrillo
    info: '#2196F3',      // Azul Brillante
    success: '#2E7D32',   // Verde Bosque
    warning: '#FF8F00',   // Ámbar Oscuro
    background: '#ECEFF1', // Gris Azulado Claro
    surface: '#FFFFFF',    // Blanco
    // 'verde-oliva': '#556B2F',
    // 'gris-oscuro-institucional': '#37474F',
  }
}

export default createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'ipsfaTheme',
    themes: {
      ipsfaTheme,
      // ipsfaDarkTheme: { ... }
    }
  },
  icons: {
    defaultSet: 'mdi',
  },
})
