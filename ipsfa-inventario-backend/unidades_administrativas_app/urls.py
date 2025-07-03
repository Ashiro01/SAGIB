from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UnidadAdministrativaViewSet

router = DefaultRouter()
router.register(r'unidades-administrativas', UnidadAdministrativaViewSet, basename='unidadadministrativa')

urlpatterns = [
    path('', include(router.urls)),
]
