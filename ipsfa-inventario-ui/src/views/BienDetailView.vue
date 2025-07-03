<template>
  <v-container>
    <div v-if="isLoading" class="text-center">
      <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      <p>Cargando detalles del bien...</p>
    </div>
    <v-card v-if="!isLoading && bienActual && !errorBien">
      <v-card-title>
        <span class="text-h5">Detalles del Bien: {{ bienActual.descripcion }}</span>
        <v-spacer></v-spacer>
        <v-btn color="orange darken-1" variant="text" @click="irAEditar" class="mr-2">
          <v-icon start>mdi-pencil</v-icon>
          Editar
        </v-btn>
        <v-btn color="primary" variant="text" @click="volverAlListado">
          <v-icon start>mdi-arrow-left</v-icon>
          Volver al Listado
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text>
        <v-row>
          <v-col cols="12" md="6">
            <v-list-item>
              <v-list-item-title>Código Patrimonial</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.codigo_patrimonial || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Descripción Completa</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.descripcion || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Fecha de Adquisición</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.fecha_adquisicion || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Marca</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.marca || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Modelo</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.modelo || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Serial del Fabricante</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.serial || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>N° Orden Compra / Factura</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.n_orden_compra_factura || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Proveedor</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.nombre_proveedor || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
          </v-col>

          <v-col cols="12" md="6">
            <v-list-item>
              <v-list-item-title>Cantidad</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.cantidad || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Valor Unitario Bs.</v-list-item-title>
              <v-list-item-subtitle>{{ formatCurrency(bienActual.valor_unitario_bs, 'Bs.') }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Valor Unitario $</v-list-item-title>
              <v-list-item-subtitle>{{ formatCurrency(bienActual.valor_unitario_usd, '$') }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Responsable del Área</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.responsable_asignado_nombre || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Cargo del Responsable</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.responsable_asignado_cargo || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Ubicación Física</v-list-item-title>
              <v-list-item-subtitle>{{ bienActual.ubicacion_fisica_especifica || 'N/A' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Estado del Bien</v-list-item-title>
              <v-list-item-subtitle>
                <v-chip :color="getColorPorEstado(bienActual.estado_bien)" size="small" dark>
                  {{ bienActual.estado_bien || 'N/A' }}
                </v-chip>
              </v-list-item-subtitle>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-title>Observaciones</v-list-item-title>
              <v-list-item-subtitle style="white-space: pre-wrap;">{{ bienActual.observaciones || 'Sin observaciones' }}</v-list-item-subtitle>
            </v-list-item>
            <v-divider class="my-4"></v-divider>
            <h3 class="text-h6 mb-2">Código de Trazabilidad</h3>
            <div class="d-flex flex-column align-center text-center">
              <v-img
                v-if="qrCodeUrl"
                :src="qrCodeUrl + '?t=' + cacheBuster"
                alt="Código QR del Bien"
                contain
                max-width="200"
                max-height="200"
                @load="qrCodeLoading = false"
                @error="qrCodeLoading = false"
              ></v-img>
              <div v-else style="width: 200px; height: 200px;" class="d-flex justify-center align-center grey lighten-3">
                  <v-progress-circular indeterminate color="primary"></v-progress-circular>
              </div>
              <p class="mt-2 caption">
                Código Patrimonial: <strong>{{ bienActual.codigo_patrimonial || 'No generado' }}</strong>
              </p>
              <v-btn
                color="primary"
                class="mt-4"
                @click="imprimirEtiqueta"
              >
                <v-icon left>mdi-printer</v-icon>
                Imprimir Etiqueta
              </v-btn>
            </div>
          </v-col>
        </v-row>
        <v-divider class="my-4"></v-divider>
        <v-row>
          <v-col cols="12" md="6">
            <div class="text-subtitle-1 font-weight-bold mb-2">Datos de Depreciación</div>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-subtitle>Vida Útil Estimada</v-list-item-subtitle>
                <v-list-item-title>
                  {{ bienActual.vida_util_estimada_anios ? `${bienActual.vida_util_estimada_anios} años` : 'No especificada' }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-subtitle>Valor Residual (Salvamento)</v-list-item-subtitle>
                <v-list-item-title>
                  {{ formatCurrency(bienActual.valor_residual) }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
            <v-divider inset></v-divider>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-subtitle>Método de Depreciación</v-list-item-subtitle>
                <v-list-item-title>
                  {{ getMetodoDepreciacionDisplay(bienActual.metodo_depreciacion) }}
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    <v-alert v-else :border="'start'" variant="outlined" type="error" class="mt-5">
      <template #title>Error</template>
      {{ errorBien || 'No se pudo cargar la información del bien seleccionado o el bien no existe.' }}
    </v-alert>
  </v-container>
</template>

<script setup>
import { onMounted, computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';
import { useBienesStore } from '@/stores/bienesStore';

const route = useRoute();
const router = useRouter();
const bienesStore = useBienesStore();
const { bienActual, getError: errorBien, isLoading } = storeToRefs(bienesStore);

const qrCodeLoading = ref(true);
const cacheBuster = ref(Date.now());

const qrCodeUrl = computed(() => {
  if (bienActual.value && bienActual.value.id) {
    return `http://127.0.0.1:8000/api/bienes/${bienActual.value.id}/qr_code/`;
  }
  return null;
});

watch(qrCodeUrl, () => {
  qrCodeLoading.value = true;
  cacheBuster.value = Date.now();
});

function formatCurrency(value, currencySymbol = 'Bs.') {
  if (value === null || typeof value === 'undefined') return 'N/A';
  if (typeof value !== 'number') {
    const numValue = parseFloat(value);
    if (isNaN(numValue)) return value;
    value = numValue;
  }
  const fixedValue = parseFloat(value.toFixed(2));
  return `${currencySymbol} ${fixedValue.toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function getColorPorEstado(estado) {
  if (estado === 'Nuevo') return 'green';
  if (estado === 'Bueno') return 'blue';
  if (estado === 'Regular') return 'orange';
  if (estado === 'Malo') return 'red';
  if (estado === 'Obsoleto') return 'grey';
  if (estado === 'En Reparación') return 'purple';
  return 'default';
}

function volverAlListado() {
  router.push('/bienes');
}
function irAEditar() {
  if (bienActual.value) {
    router.push({ name: 'editarBien', params: { id: bienActual.value.id } });
  }
}

function imprimirEtiqueta() {
  window.alert('Funcionalidad de impresión de etiquetas pendiente de implementación.');
}

function getMetodoDepreciacionDisplay(metodo) {
  if (metodo === 'LINEA_RECTA') return 'Línea Recta';
  if (metodo === 'SALDO_DECRECIENTE') return 'Saldo Decreciente';
  return 'No especificado';
}

onMounted(async () => {
  const bienId = parseInt(route.params.id);
  if (!isNaN(bienId)) {
    try {
      await bienesStore.fetchBienById(bienId);
    } catch (e) {
      // Error is handled by store
    }
  }
});
</script>

<style scoped>
.v-list-item__title {
  font-size: 1rem;
  padding-top: 2px;
}
.v-list-item__subtitle {
  font-weight: bold;
  color: rgba(0,0,0,0.6);
  font-size: 0.8rem;
}
.v-divider[inset] {
  margin-left: 0px;
  margin-right: 16px;
}
</style>