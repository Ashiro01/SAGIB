from .serializers import ChangePasswordSerializer
from rest_framework import permissions
from rest_framework import generics
from django.core.cache import cache # Usaremos el caché de Django para el token temporal
import uuid # Para generar tokens únicos

# --- Vistas para el Flujo de Restablecimiento de Contraseña ---
from rest_framework import status

class GetSecurityQuestionsView(generics.GenericAPIView):
    """
    Recibe un username y devuelve las preguntas de seguridad asociadas.
    No requiere autenticación.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Nombre de usuario requerido.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username=username)
            respuestas = RespuestaSeguridadUsuario.objects.filter(usuario=user)
            if not respuestas.exists():
                return Response({'error': 'El usuario no tiene preguntas de seguridad configuradas.'}, status=status.HTTP_404_NOT_FOUND)

            # Devolvemos solo el texto y el ID de las preguntas
            preguntas = [{'id': r.pregunta.id, 'texto': r.pregunta.texto} for r in respuestas]
            return Response(preguntas, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class VerifySecurityAnswersView(generics.GenericAPIView):
    """
    Verifica las respuestas a las preguntas de seguridad. Si son correctas,
    genera y devuelve un token de reseteo de contraseña de un solo uso.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        respuestas_enviadas = request.data.get('respuestas') # Espera una lista de {pregunta_id, respuesta_plana}

        if not username or not respuestas_enviadas:
            return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            respuestas_guardadas = RespuestaSeguridadUsuario.objects.filter(usuario=user)

            if len(respuestas_enviadas) != respuestas_guardadas.count():
                 return Response({'error': 'El número de respuestas no coincide.'}, status=status.HTTP_400_BAD_REQUEST)

            todas_correctas = True
            for resp_enviada in respuestas_enviadas:
                pregunta_id = resp_enviada.get('pregunta_id')
                respuesta_plana = resp_enviada.get('respuesta_plana')

                try:
                    respuesta_guardada = respuestas_guardadas.get(pregunta_id=pregunta_id)
                    if not respuesta_guardada.check_respuesta(respuesta_plana):
                        todas_correctas = False
                        break
                except RespuestaSeguridadUsuario.DoesNotExist:
                    todas_correctas = False
                    break

            if todas_correctas:
                # Generar un token de reseteo temporal (válido por 10 minutos)
                reset_token = str(uuid.uuid4())
                cache.set(f"reset_token_{reset_token}", user.username, timeout=600)
                return Response({'reset_token': reset_token}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Una o más respuestas son incorrectas.'}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class SetNewPasswordView(generics.GenericAPIView):
    """
    Establece una nueva contraseña para un usuario usando un token de reseteo válido.
    """
    serializer_class = ChangePasswordSerializer # Reutilizamos este para la validación de contraseñas
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        reset_token = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')

        if not reset_token or not new_password or not new_password_confirm:
             return Response({'error': 'Datos incompletos.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != new_password_confirm:
            return Response({'error': 'Las contraseñas no coinciden.'}, status=status.HTTP_400_BAD_REQUEST)

        username = cache.get(f"reset_token_{reset_token}")

        if not username:
            return Response({'error': 'El token de reseteo es inválido o ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            # Invalidar el token después de usarlo
            cache.delete(f"reset_token_{reset_token}")
            return Response({'status': 'Contraseña restablecida exitosamente.'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'Usuario asociado al token no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
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