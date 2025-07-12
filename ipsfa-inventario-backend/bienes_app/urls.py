from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BienViewSet,
    MovimientoBienViewSet,
    ReporteInventarioGeneralPDF,
    ReporteInventarioGeneralExcel,
    ReporteBienesPorCategoriaPDF,
    ReporteBienesPorCategoriaExcel,
    ReporteBienesPorUnidadPDF,
    ReporteBienesPorUnidadExcel,
    ReporteBienesDesincorporadosPDF,
    ReporteBienesDesincorporadosExcel,
    ReporteBienesTrasladadosPDF,
    ReporteBienesTrasladadosExcel,
    DashboardStatsView,
    BienesUploadView,
    CalcularDepreciacionView,
    CategoriaViewSet,
    BienQRCodeView,
)
from .user_views import UserDetailView

router = DefaultRouter()
router.register(r'bienes', BienViewSet, basename='bien')
router.register(r'movimientos-bienes', MovimientoBienViewSet, basename='movimientobien')
router.register(r'categorias', CategoriaViewSet, basename='categoria')

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('bienes/upload/', BienesUploadView.as_view(), name='bienes-upload'),
    path('bienes/<int:pk>/qr_code/', BienQRCodeView.as_view(), name='bien-qr-code'),
    path('depreciacion/calcular/', CalcularDepreciacionView.as_view(), name='calcular-depreciacion'),
    path('reportes/inventario-general/', ReporteInventarioGeneralPDF.as_view(), name='reporte-inventario-general'),
    path('reportes/inventario-general/excel/', ReporteInventarioGeneralExcel.as_view(), name='reporte-inventario-general-excel'),
    path('reportes/bienes-por-categoria/pdf/', ReporteBienesPorCategoriaPDF.as_view(), name='reporte-bienes-categoria-pdf'),
    path('reportes/bienes-por-categoria/excel/', ReporteBienesPorCategoriaExcel.as_view(), name='reporte-bienes-categoria-excel'),
    path('reportes/bienes-por-unidad/pdf/', ReporteBienesPorUnidadPDF.as_view(), name='reporte-bienes-unidad-pdf'),
    path('reportes/bienes-por-unidad/excel/', ReporteBienesPorUnidadExcel.as_view(), name='reporte-bienes-unidad-excel'),
    path('reportes/bienes-desincorporados/pdf/', ReporteBienesDesincorporadosPDF.as_view(), name='reporte-bienes-desincorporados-pdf'),
    path('reportes/bienes-desincorporados/excel/', ReporteBienesDesincorporadosExcel.as_view(), name='reporte-bienes-desincorporados-excel'),
    path('reportes/bienes-trasladados/pdf/', ReporteBienesTrasladadosPDF.as_view(), name='reporte-bienes-trasladados-pdf'),
    path('reportes/bienes-trasladados/excel/', ReporteBienesTrasladadosExcel.as_view(), name='reporte-bienes-trasladados-excel'),
    path('', include(router.urls)),
    path('users/me/', UserDetailView.as_view(), name='user-detail'),
]