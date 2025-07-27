# perfiles_app/admin.py
from django.contrib import admin
from .models import PerfilUsuario, PreguntaSeguridad, RespuestaSeguridadUsuario

admin.site.register(PerfilUsuario)
admin.site.register(PreguntaSeguridad)
admin.site.register(RespuestaSeguridadUsuario)