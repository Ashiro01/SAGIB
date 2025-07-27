from django.contrib import admin
from .models import PreguntaSeguridadUsuario

# Register your models here.

@admin.register(PreguntaSeguridadUsuario)
class PreguntaSeguridadUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario',)
    search_fields = ('usuario__username',)
    readonly_fields = ('respuesta_1_hash', 'respuesta_2_hash')
