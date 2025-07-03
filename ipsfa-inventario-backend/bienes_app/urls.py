# ipsfa-inventario-backend/bienes_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BienViewSet, MovimientoBienViewSet, DashboardStatsView, BienesUploadView, BienQRCodeView, CalcularDepreciacionView
)
from .user_views import UserDetailView

router = DefaultRouter()
router.register(r'bienes', BienViewSet, basename='bien')
router.register(r'movimientos-bienes', MovimientoBienViewSet, basename='movimientobien') 

urlpatterns = [
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('bienes/upload/', BienesUploadView.as_view(), name='bienes-upload'), # <-- AÑADE ESTA LÍNEA
    path('bienes/<int:pk>/qr_code/', BienQRCodeView.as_view(), name='bien-qr-code'), # <-- AÑADE ESTA LÍNEA
    path('depreciacion/calcular/', CalcularDepreciacionView.as_view(), name='calcular-depreciacion'),
    path('', include(router.urls)),
    path('users/me/', UserDetailView.as_view(), name='user-detail'),
]