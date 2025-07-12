# auditoria_app/signals.py

from django.contrib.sessions.models import Session
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db import models
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from .models import AuditLog
from .middleware import get_current_request # Importamos la función del middleware

def log_action(usuario, ip_address, accion, entidad, entidad_id, detalles):
    """Función centralizada para crear una entrada de log."""
    AuditLog.objects.create(
        usuario=usuario,
        ip_address=ip_address,
        accion=accion,
        entidad_afectada=entidad,
        id_entidad_afectada=entidad_id,
        detalles=detalles
    )

@receiver([post_save, post_delete])
def log_model_change(sender, instance, **kwargs):
    ignored_models = [AuditLog, Session, OutstandingToken, BlacklistedToken]

    if sender in ignored_models:
        return

    request = get_current_request()
    if not request:
        return

    # Evitar el log 'ACTUALIZAR_USUARIO' en cada login/refresh
    is_user_update = sender == User and 'created' in kwargs and not kwargs.get('created', False)
    is_token_request = request.path.startswith('/api/token/')
    if is_user_update and is_token_request:
        return

    # Obtenemos usuario y IP de la petición
    user = request.user if request.user.is_authenticated else None
    ip_address = request.META.get('REMOTE_ADDR')

    # Determinamos si es creación, actualización o eliminación
    if 'created' in kwargs and kwargs['created']:
        accion = f'CREAR_{sender._meta.verbose_name.upper()}'
        detalles = f"Se creó el objeto '{str(instance)}' (ID: {instance.pk})."
    elif 'created' in kwargs and not kwargs['created']:
        accion = f'ACTUALIZAR_{sender._meta.verbose_name.upper()}'
        detalles = f"Se actualizó el objeto '{str(instance)}' (ID: {instance.pk})."
    else: # Es un post_delete
        accion = f'ELIMINAR_{sender._meta.verbose_name.upper()}'
        detalles = f"Se eliminó el objeto '{str(instance)}' (ID: {instance.pk})."

    log_action(
        usuario=user,
        ip_address=ip_address,
        accion=accion,
        entidad=sender._meta.verbose_name, # Nombre legible del modelo
        entidad_id=instance.pk,
        detalles=detalles
    )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_address = request.META.get('REMOTE_ADDR')
    detalles = f"Usuario '{user.username}' inició sesión exitosamente."
    log_action(
        usuario=user,
        ip_address=ip_address,
        accion='INICIO_SESION_EXITOSO',
        entidad='Usuario',
        entidad_id=user.pk,
        detalles=detalles
    )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip_address = request.META.get('REMOTE_ADDR')
    username = credentials.get('username', 'desconocido')
    detalles = f"Intento fallido de inicio de sesión para el usuario '{username}'."
    log_action(
        usuario=None,
        ip_address=ip_address,
        accion='INICIO_SESION_FALLIDO',
        entidad='Sistema',
        entidad_id=None,
        detalles=detalles
    )