# auditoria_app/admin.py

from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista de logs
    list_display = ('timestamp', 'usuario', 'accion', 'entidad_afectada', 'id_entidad_afectada', 'ip_address')
    # Filtros que aparecerán en la barra lateral
    list_filter = ('timestamp', 'accion', 'usuario')
    # Campos en los que se podrá buscar
    search_fields = ('usuario__username', 'detalles', 'ip_address', 'entidad_afectada')

    # Hacemos que el panel de admin sea de solo lectura para los logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False