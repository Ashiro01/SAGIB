from django.contrib.auth.models import User, Group
from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
import logging
from rest_framework_simplejwt.views import TokenObtainPairView, TokenBlacklistView
from django.contrib.auth.signals import user_logged_in
from auditoria_app.signals import log_action

from .serializers import UserSerializer, GroupSerializer

# Configurar un logger básico si aún no está configurado
logger = logging.getLogger(__name__)

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        logger.info(f"Intentando eliminar al usuario: {instance.username} (ID: {instance.id}) por el usuario {request.user.username}")

        # Proteger superusuario especial
        if instance.username == 'espantaviejas3000' and not request.user.is_superuser:
            logger.warning(f"Intento no autorizado de eliminar a {instance.username} por {request.user.username}")
            return Response({'detail': 'Solo el superusuario puede eliminar este usuario.'}, status=status.HTTP_403_FORBIDDEN)
        if instance.username == 'admin':
            logger.warning(f"Intento no autorizado de eliminar al administrador principal {instance.username} por {request.user.username}")
            return Response({'detail': 'El usuario administrador principal no puede ser eliminado.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user_id_to_delete = instance.id
            username_deleted = instance.username
            logger.info(f"Antes de llamar a instance.delete() para el usuario {username_deleted} (ID: {user_id_to_delete})")
            instance.delete()
            logger.info(f"Después de llamar a instance.delete() para el usuario {username_deleted} (ID: {user_id_to_delete})")

            # Verificar si el usuario aún existe después de delete()
            try:
                still_exists = User.objects.filter(pk=user_id_to_delete).exists()
                if still_exists:
                    logger.error(f"¡ERROR CRÍTICO! El usuario {username_deleted} (ID: {user_id_to_delete}) todavía existe en la BD después de delete().")
                else:
                    logger.info(f"Confirmado: El usuario con el antiguo ID {user_id_to_delete} ({username_deleted}) ya no existe en la BD.")
            except Exception as e_check:
                logger.error(f"Error al verificar la existencia del usuario (ID: {user_id_to_delete}) después de delete(): {str(e_check)}")
            
            return Response({'detail': f'Usuario {username_deleted} eliminado correctamente.'}, status=status.HTTP_200_OK)
        except ProtectedError as pe:
            logger.error(f"Error ProtectedError al eliminar a {username_deleted}: {str(pe)}")
            return Response({'detail': 'No se puede eliminar el usuario porque está referenciado por otros registros.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error inesperado al eliminar a {username_deleted}: {str(e)}")
            return Response({'detail': f'Error inesperado: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, editar y eliminar Grupos (Roles).
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            user_logged_in.send(sender=user.__class__, request=request, user=user)
        return response

class CustomTokenBlacklistView(TokenBlacklistView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().post(request, *args, **kwargs)

        user = request.user
        ip_address = request.META.get('REMOTE_ADDR')
        detalles = f"Usuario '{user.username}' cerró sesión exitosamente."

        try:
            # Llama al método original para invalidar el token
            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                log_action(
                    usuario=user,
                    ip_address=ip_address,
                    accion='CIERRE_SESION_EXITOSO',
                    entidad='Usuario',
                    entidad_id=user.pk,
                    detalles=detalles
                )
            return response
        except Exception as e:
            # Manejar el caso en que el token ya haya expirado o sea inválido
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
