# perfiles_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PerfilUsuarioView,
    ChangePasswordView,
    PreguntaSeguridadViewSet,
    RespuestaSeguridadUsuarioViewSet,
    PerfilCompletoView,
    GetSecurityQuestionsView,
    VerifySecurityAnswersView,
    SetNewPasswordView
)

router = DefaultRouter()
router.register(r'preguntas-seguridad', PreguntaSeguridadViewSet, basename='pregunta-seguridad')
router.register(r'mis-respuestas', RespuestaSeguridadUsuarioViewSet, basename='respuesta-seguridad-usuario')

urlpatterns = [
    path('perfil/me/', PerfilUsuarioView.as_view(), name='perfil-me'),
    path('perfil/completo/', PerfilCompletoView.as_view(), name='perfil-completo'),
    path('perfil/change-password/', ChangePasswordView.as_view(), name='perfil-change-password'),
    # --- NUEVAS RUTAS PARA RESTABLECER CONTRASEÑA ---
    path('password-reset/get-questions/', GetSecurityQuestionsView.as_view(), name='password-reset-get-questions'),
    path('password-reset/verify-answers/', VerifySecurityAnswersView.as_view(), name='password-reset-verify-answers'),
    path('password-reset/set-new-password/', SetNewPasswordView.as_view(), name='password-reset-set-new'),
    path('', include(router.urls)),
]