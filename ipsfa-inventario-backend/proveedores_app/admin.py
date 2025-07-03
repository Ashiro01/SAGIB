# ipsfa-inventario-backend/proveedores_app/admin.py
from django.contrib import admin
from .models import Proveedor # Importa tu modelo Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre_proveedor', 'rif', 'contacto_principal_nombre', 'contacto_principal_email', 'activo', 'fecha_registro')
    list_filter = ('activo', 'fecha_registro')
    search_fields = ('nombre_proveedor', 'rif', 'contacto_principal_nombre', 'contacto_principal_email')
    list_editable = ('activo',) # Permite editar el estado 'activo' directamente en la lista
    readonly_fields = ('fecha_registro', 'ultima_actualizacion')