# ipsfa-inventario-backend/bienes_app/admin.py
from django.contrib import admin
from .models import Bien, MovimientoBien, DepreciacionMensual, Categoria

@admin.register(Bien) # Usa el decorador para registrar
class BienAdmin(admin.ModelAdmin):
    list_display = ('codigo_patrimonial', 'descripcion', 'categoria', 'marca', 'modelo', 'estado_bien', 'unidad_administrativa_actual')
    list_filter = ('estado_bien', 'marca', 'categoria', 'unidad_administrativa_actual')
    search_fields = ('codigo_patrimonial', 'descripcion', 'serial', 'marca', 'modelo')
    autocomplete_fields = ['categoria', 'unidad_administrativa_actual']

# Forma alternativa de registrar (sin decorador):
# admin.site.register(Bien, BienAdmin)

@admin.register(MovimientoBien)
class MovimientoBienAdmin(admin.ModelAdmin):
    list_display = ('bien', 'tipo_movimiento', 'fecha_movimiento', 'unidad_origen', 'unidad_destino', 'usuario_registra')
    list_filter = ('tipo_movimiento', 'fecha_movimiento')
    search_fields = ('bien__descripcion', 'bien__codigo_patrimonial')
    autocomplete_fields = ['bien', 'unidad_origen', 'unidad_destino', 'usuario_registra']

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
    
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)