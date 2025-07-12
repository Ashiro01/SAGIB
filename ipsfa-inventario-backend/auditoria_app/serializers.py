# auditoria_app/serializers.py
from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source='usuario.username', read_only=True, default='Sistema')

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'timestamp',
            'usuario_username',
            'accion',
            'ip_address',
            'entidad_afectada',
            'id_entidad_afectada',
            'detalles',
        ]
        read_only_fields = fields # Todos los campos son de solo lectura