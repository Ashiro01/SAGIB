<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-2">Cálculo de Depreciación Periódica</h1>
        <p class="subtitle-1">
          Seleccione el período (mes y año) para ejecutar el cálculo de depreciación sobre todos los activos elegibles.
        </p>
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <v-card class="pa-4">
          <v-card-title>Seleccionar Período de Cálculo</v-card-title>
          <v-card-text>
            <v-form ref="formPeriodo" v-model="validForm">
              <v-row>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="periodo.mes"
                    :items="meses"
                    item-title="nombre"
                    item-value="valor"
                    label="Mes"
                    :rules="[rules.required]"
                    outlined
                    dense
                  ></v-select>
                </v-col>
                <v-col cols="12" sm="6">
                  <v-select
                    v-model="periodo.anio"
                    :items="anios"
                    label="Año"
                    :rules="[rules.required]"
                    outlined
                    dense
                  ></v-select>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
          <v-card-actions class="justify-center">
            <v-btn
              :loading="isLoading"
              :disabled="isLoading || !validForm"
              color="primary"
              x-large
              @click="iniciarCalculo"
            >
              <v-icon left>mdi-cogs</v-icon>
              Iniciar Cálculo de Depreciación
            </v-btn>
          </v-card-actions>
        </v-card>

        <v-card v-if="ultimoResultado" class="mt-6">
          <v-alert :type="ultimoResultado.errores && ultimoResultado.errores.length > 0 ? 'warning' : 'success'" prominent border="left">
            <h6 class="text-h6">Resultado del Último Cálculo</h6>
            <div class="mt-2">{{ ultimoResultado.status }}</div>
            <ul class="mt-2 text-body-2">
              <li><strong>Período:</strong> {{ ultimoResultado.mes }}/{{ ultimoResultado.anio }}</li>
              <li><strong>Bienes Calculados Exitosamente:</strong> {{ ultimoResultado.bienes_calculados }}</li>
              <li><strong>Bienes Omitidos (ya calculados o sin valor):</strong> {{ ultimoResultado.bienes_omitidos }}</li>
            </ul>
          </v-alert>
        </v-card>

      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useDepreciacionStore } from '@/stores/depreciacionStore';
import { mapState, mapActions } from 'pinia';

export default {
  name: 'CalcularDepreciacionView',
  data() {
    // Generar lista de meses y años para los selectores
    const meses = Array.from({ length: 12 }, (v, k) => ({
      nombre: new Date(0, k).toLocaleString('es-ES', { month: 'long' }),
      valor: k + 1,
    }));
    const anioActual = new Date().getFullYear();
    const anios = Array.from({ length: 5 }, (v, k) => anioActual - k);

    return {
      validForm: false,
      periodo: {
        mes: new Date().getMonth(), // Mes anterior por defecto
        anio: anioActual,
      },
      meses,
      anios,
      rules: {
        required: value => !!value || 'Este campo es requerido.',
      },
    };
  },
  computed: {
    ...mapState(useDepreciacionStore, ['isLoading', 'ultimoResultado', 'error']),
  },
  methods: {
    ...mapActions(useDepreciacionStore, ['ejecutarCalculoDepreciacion']),
    async iniciarCalculo() {
      const { valid } = await this.$refs.formPeriodo.validate();
      if (!valid) {
        this.$emit('show-snackbar', { message: 'Debe seleccionar un mes y un año.', color: 'warning' });
        return;
      }

      if (confirm(`¿Está seguro de que desea ejecutar el cálculo de depreciación para el período <span class="math-inline">\{this\.periodo\.mes\}/</span>{this.periodo.anio}? Esta acción no se puede deshacer.`)) {
        try {
          const resultado = await this.ejecutarCalculoDepreciacion(this.periodo);
          this.$emit('show-snackbar', {
            message: resultado.status || 'Proceso de cálculo finalizado.',
            color: 'success',
            timeout: 5000,
          });
        } catch (error) {
          this.$emit('show-snackbar', {
            message: error.message || 'Ocurrió un error al ejecutar el cálculo.',
            color: 'error',
            timeout: 5000,
          });
        }
      }
    },
  },
};
</script>