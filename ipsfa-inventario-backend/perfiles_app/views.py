from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# Endpoint para obtener los datos completos del usuario autenticado y su perfil
class PerfilCompletoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        from .serializers import UserDetailSerializer
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
# perfiles_app/views.py
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import PerfilUsuario, PreguntaSeguridad, RespuestaSeguridadUsuario
from .serializers import (
    UserDetailSerializer,
    ChangePasswordSerializer,
    PreguntaSeguridadSerializer,
    RespuestaSeguridadUsuarioSerializer
)

class PerfilUsuarioView(generics.RetrieveUpdateAPIView):
    """Obtiene y actualiza el perfil del usuario autenticado."""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Devolvemos siempre el usuario que está haciendo la petición
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    """Endpoint para cambiar la contraseña del usuario autenticado."""
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Verificar la contraseña antigua
            if not self.object.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["La contraseña actual es incorrecta."]}, status=status.HTTP_400_BAD_REQUEST)
            # Establecer la nueva contraseña
            self.object.set_password(serializer.validated_data.get("new_password"))
            self.object.save()
            return Response({"status": "contraseña cambiada exitosamente"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PreguntaSeguridadViewSet(viewsets.ReadOnlyModelViewSet):
    """Endpoint de solo lectura para listar las preguntas de seguridad disponibles."""
    queryset = PreguntaSeguridad.objects.all()
    serializer_class = PreguntaSeguridadSerializer
    permission_classes = [permissions.IsAuthenticated]

class RespuestaSeguridadUsuarioViewSet(viewsets.ModelViewSet):
    """Endpoint para que el usuario gestione sus propias respuestas de seguridad."""
    serializer_class = RespuestaSeguridadUsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Aseguramos que el usuario solo pueda ver y modificar SUS PROPIAS respuestas.
        return RespuestaSeguridadUsuario.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        # Al crear una nueva respuesta, la asociamos automáticamente al usuario logueado.
        serializer.save(usuario=self.request.user)