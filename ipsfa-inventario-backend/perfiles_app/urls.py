# perfiles_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PerfilUsuarioView,
    ChangePasswordView,
    PreguntaSeguridadViewSet,
    RespuestaSeguridadUsuarioViewSet,
    PerfilCompletoView
)

router = DefaultRouter()
router.register(r'preguntas-seguridad', PreguntaSeguridadViewSet, basename='pregunta-seguridad')
router.register(r'mis-respuestas', RespuestaSeguridadUsuarioViewSet, basename='respuesta-seguridad-usuario')

urlpatterns = [
    path('perfil/me/', PerfilUsuarioView.as_view(), name='perfil-me'),
    path('perfil/completo/', PerfilCompletoView.as_view(), name='perfil-completo'),
    path('perfil/change-password/', ChangePasswordView.as_view(), name='perfil-change-password'),
    path('', include(router.urls)),
]