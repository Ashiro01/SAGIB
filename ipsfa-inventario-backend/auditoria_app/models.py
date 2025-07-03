# auditoria_app/models.py

from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    # QUIÉN: El usuario que realizó la acción.
    # Usamos settings.AUTH_USER_MODEL para referenciar al modelo de usuario activo.
    # on_delete=models.SET_NULL: si se elimina un usuario, sus logs no se borran,
    # simplemente el campo 'usuario' queda en nulo.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario"
    )

    # CUÁNDO: La fecha y hora exactas del evento.
    # auto_now_add=True: se establece automáticamente al crear el registro.
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha y Hora"
    )

    # QUÉ: La acción que se realizó.
    accion = models.CharField(
        max_length=100,
        verbose_name="Acción Realizada"
    )

    # DÓNDE: La dirección IP desde donde se realizó la acción.
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP"
    )

    # SOBRE QUÉ: Detalles del objeto afectado (opcional pero muy útil).
    # Ejemplo: 'Bien', 'Proveedor', 'Usuario'
    entidad_afectada = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Entidad Afectada"
    )
    # Ejemplo: el ID del bien, proveedor o usuario que se modificó.
    id_entidad_afectada = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID de la Entidad Afectada"
    )

    # DETALLES: Un resumen legible de la acción.
    # Ejemplo: "Usuario 'admin' creó el bien 'Laptop HP ProBook'."
    detalles = models.TextField(
        verbose_name="Detalles de la Acción"
    )

    def __str__(self):
        # Representación legible del objeto en el admin de Django.
        usuario_str = self.usuario.username if self.usuario else "Sistema"
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {usuario_str} - {self.accion}"

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Logs de Auditoría"
        ordering = ['-timestamp'] # Ordenar por más reciente primero