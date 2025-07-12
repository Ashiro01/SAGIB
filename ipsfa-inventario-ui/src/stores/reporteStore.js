// src/stores/reporteStore.js
import { defineStore } from 'pinia';
import apiClient from '@/services/api'; // Tu instancia de Axios

export const useReporteStore = defineStore('reporte', {
 state: () => ({
  loading: false,
  error: null,
 }),
 actions: {
  async generarReporteInventarioGeneral(filtros = {}) {
   this.loading = true;
   this.error = null;
   try {
    const response = await apiClient.get('/reportes/inventario-general/', {
     params: filtros, // Enviamos los filtros como query params en la URL
     responseType: 'blob',
    });

    // Crear una URL temporal para el objeto Blob recibido
    const url = window.URL.createObjectURL(new Blob([response.data]));

    // Crear un enlace temporal en el DOM para iniciar la descarga
    const link = document.createElement('a');
    link.href = url;

    // El nombre del archivo que se descargará.
    link.setAttribute('download', 'reporte_inventario_general.pdf');

    // Añadir el enlace al cuerpo del documento y simular un clic
    document.body.appendChild(link);
    link.click();

    // Limpiar el enlace y la URL del objeto después de la descarga
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    return { success: true };

   } catch (err) {
    this.error = 'Error al generar el reporte de inventario.';
    console.error('Error en generarReporteInventarioGeneral:', err);
    throw new Error(this.error);
   } finally {
    this.loading = false;
   }
  },
  async generarReporteInventarioExcel(filtros = {}) {
   this.loading = true;
   this.error = null;
   try {
    const response = await apiClient.get('/reportes/inventario-general/excel/', {
     params: filtros,
     responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'reporte_inventario_general.xlsx');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    return { success: true };
   } catch (err) {
    this.error = 'Error al generar el reporte de inventario en Excel.';
    console.error('Error en generarReporteInventarioExcel:', err);
    throw new Error(this.error);
   } finally {
    this.loading = false;
   }
  },
  async generarReportePorCategoriaPDF(filtros = {}) {
   this.loading = true;
   this.error = null;
   try {
    const response = await apiClient.get('/reportes/bienes-por-categoria/pdf/', {
     params: filtros,
     responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    // Nombre dinámico según la categoría si está presente
    let nombreArchivo = 'reporte_bienes_por_categoria.pdf';
    if (filtros.categoria_nombre) {
      nombreArchivo = `reporte_bienes_categoria_${filtros.categoria_nombre}.pdf`;
    }
    link.href = url;
    link.setAttribute('download', nombreArchivo);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    return { success: true };
   } catch (err) {
    this.error = 'Error al generar el reporte de bienes por categoría.';
    console.error('Error en generarReportePorCategoriaPDF:', err);
    throw new Error(this.error);
   } finally {
    this.loading = false;
   }
  },
  async generarReportePorCategoriaExcel(filtros = {}) {
   this.loading = true;
   this.error = null;
   try {
    const response = await apiClient.get('/reportes/bienes-por-categoria/excel/', {
     params: filtros,
     responseType: 'blob',
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    let nombreArchivo = 'reporte_bienes_por_categoria.xlsx';
    if (filtros.categoria_nombre) {
      nombreArchivo = `reporte_bienes_categoria_${filtros.categoria_nombre}.xlsx`;
    }
    link.href = url;
    link.setAttribute('download', nombreArchivo);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    return { success: true };
   } catch (err) {
    this.error = 'Error al generar el reporte de bienes por categoría en Excel.';
    console.error('Error en generarReportePorCategoriaExcel:', err);
    throw new Error(this.error);
   } finally {
    this.loading = false;
   }
  },
  async generarReportePorUnidadPDF(filtros) {
    this.loading = true;
    this.error = null;
    try {
        const response = await apiClient.get('/reportes/bienes-por-unidad/pdf/', {
            params: filtros,
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `reporte_bienes_unidad_${filtros.unidad_id}.pdf`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        return { success: true };
    } catch (err) {
        this.error = 'Error al generar el reporte por unidad en PDF.';
        throw new Error(this.error);
    } finally {
        this.loading = false;
    }
  },
  async generarReportePorUnidadExcel(filtros) {
    this.loading = true;
    this.error = null;
    try {
        const response = await apiClient.get('/reportes/bienes-por-unidad/excel/', {
            params: filtros,
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `reporte_bienes_unidad_${filtros.unidad_id}.xlsx`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        return { success: true };
    } catch (err) {
        this.error = 'Error al generar el reporte por unidad en Excel.';
        throw new Error(this.error);
    } finally {
        this.loading = false;
    }
  },
  async generarReporteDesincorporadosPDF(filtros) {
    this.loading = true;
    this.error = null;
    try {
        const response = await apiClient.get('/reportes/bienes-desincorporados/pdf/', {
            params: filtros,
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'reporte_bienes_desincorporados.pdf');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        return { success: true };
    } catch (err) {
        this.error = 'Error al generar el reporte de desincorporados en PDF.';
        throw new Error(this.error);
    } finally {
        this.loading = false;
    }
  },
  async generarReporteDesincorporadosExcel(filtros) {
    this.loading = true;
    this.error = null;
    try {
        const response = await apiClient.get('/reportes/bienes-desincorporados/excel/', {
            params: filtros,
            responseType: 'blob',
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'reporte_bienes_desincorporados.xlsx');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        return { success: true };
    } catch (err) {
        this.error = 'Error al generar el reporte de desincorporados en Excel.';
        throw new Error(this.error);
    } finally {
        this.loading = false;
    }
  },
  // --- NUEVAS ACCIONES PARA REPORTE DE TRASLADADOS ---
  async generarReporteTrasladadosPDF(filtros) {
    this.loading = true;
    this.error = null;
    try {
      const response = await apiClient.get('/reportes/bienes-trasladados/pdf/', {
        params: filtros,
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'reporte_bienes_trasladados.pdf');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      return { success: true };
    } catch (err) {
      this.error = 'Error al generar el reporte de traslados en PDF.';
      throw new Error(this.error);
    } finally {
      this.loading = false;
    }
  },
  async generarReporteTrasladadosExcel(filtros) {
    this.loading = true;
    this.error = null;
    try {
      const response = await apiClient.get('/reportes/bienes-trasladados/excel/', {
        params: filtros,
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'reporte_bienes_trasladados.xlsx');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      return { success: true };
    } catch (err) {
      this.error = 'Error al generar el reporte de traslados en Excel.';
      throw new Error(this.error);
    } finally {
      this.loading = false;
    }
  },
 }
});

