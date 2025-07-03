# ipsfa-inventario-backend/bienes_app/admin.py
from django.contrib import admin
from .models import Bien, MovimientoBien, DepreciacionMensual # Importa DepreciacionMensual

@admin.register(Bien) # Usa el decorador para registrar
class BienAdmin(admin.ModelAdmin):
    list_display = ('codigo_patrimonial', 'descripcion', 'marca', 'modelo', 'estado_bien', 'fecha_adquisicion', 'ubicacion_fisica_especifica')
    list_filter = ('estado_bien', 'marca', 'fecha_adquisicion', 'ubicacion_fisica_especifica')
    search_fields = ('codigo_patrimonial', 'codigo_anterior', 'descripcion', 'serial', 'marca', 'modelo')
    # readonly_fields = ('fecha_creacion', 'fecha_actualizacion') # Campos que no se pueden editar en el admin
    # Puedes añadir más personalizaciones aquí

# Forma alternativa de registrar (sin decorador):
# admin.site.register(Bien, BienAdmin)

@admin.register(MovimientoBien)
class MovimientoBienAdmin(admin.ModelAdmin):
    list_display = ('bien', 'tipo_movimiento', 'fecha_movimiento', 'unidad_origen', 'unidad_destino', 'usuario_registra')
    list_filter = ('tipo_movimiento', 'fecha_movimiento', 'usuario_registra')
    search_fields = ('bien__descripcion', 'bien__codigo_patrimonial', 'numero_oficio_referencia', 'motivo_desincorporacion')
    autocomplete_fields = ['bien', 'unidad_origen', 'unidad_destino', 'usuario_registra'] # Para búsquedas más fáciles en el admin

    fieldsets = (
        (None, {
            'fields': ('bien', 'tipo_movimiento', 'fecha_movimiento', 'usuario_registra')
        }),
        ('Detalles del Traslado (si aplica)', {
            'classes': ('collapse',), # Para que aparezca colapsado si no es el foco
            'fields': ('unidad_origen', 'unidad_destino', 'responsable_anterior_nombre', 'responsable_nuevo_nombre', 'ubicacion_anterior_especifica', 'ubicacion_nueva_especifica'),
        }),
        ('Detalles de Desincorporación (si aplica)', {
            'classes': ('collapse',),
            'fields': ('motivo_desincorporacion', 'numero_oficio_referencia'),
        }),
        ('Observaciones Adicionales', {
            'fields': ('observaciones_movimiento',),
        }),
    )
    # Para que autocomplete_fields funcione bien, los modelos referenciados (Bien, UnidadAdministrativa, User)
    # deben tener search_fields definidos en sus respectivos ModelAdmin.

# NUEVO REGISTRO PARA LOS CÁLCULOS DE DEPRECIACIÓN
@admin.register(DepreciacionMensual)
class DepreciacionMensualAdmin(admin.ModelAdmin):
    list_display = (
        'bien', 
        'anio', 
        'mes', 
        'valor_depreciado_mes', 
        'depreciacion_acumulada', 
        'valor_neto_en_libros', 
        'fecha_calculo'
    )
    list_filter = ('anio', 'mes', 'fecha_calculo')
    search_fields = ('bien__descripcion', 'bien__codigo_patrimonial')
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False