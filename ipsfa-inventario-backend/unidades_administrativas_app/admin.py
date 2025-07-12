from django.contrib import admin
from .models import UnidadAdministrativa

@admin.register(UnidadAdministrativa)
class UnidadAdministrativaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activa', 'fecha_registro', 'ultima_actualizacion')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activa',)
