# perfiles_app/models.py
from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True, verbose_name="Foto de Perfil")

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

class PreguntaSeguridad(models.Model):
    texto = models.CharField(max_length=255, unique=True, verbose_name="Texto de la Pregunta")

    def __str__(self):
        return self.texto

class RespuestaSeguridadUsuario(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='respuestas_seguridad')
    pregunta = models.ForeignKey(PreguntaSeguridad, on_delete=models.CASCADE)
    # NUNCA guardamos la respuesta en texto plano. La hasheamos.
    respuesta_hash = models.CharField(max_length=128, verbose_name="Respuesta Hasheada")

    def set_respuesta(self, respuesta_plana):
        self.respuesta_hash = make_password(respuesta_plana.lower().strip())

    def check_respuesta(self, respuesta_plana):
        return check_password(respuesta_plana.lower().strip(), self.respuesta_hash)

    def __str__(self):
        return f"Respuesta de {self.usuario.username} a '{self.pregunta.texto[:30]}...'"

    class Meta:
        unique_together = ('usuario', 'pregunta') # Un usuario solo puede tener una respuesta por pregunta