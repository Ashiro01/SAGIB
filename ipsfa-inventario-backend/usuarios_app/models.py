from django.db import models
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password

class PreguntaSeguridadUsuario(models.Model):
    # Relación uno a uno con el usuario. Cada usuario tendrá un único registro de preguntas.
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='preguntas_seguridad'
    )

    # Pregunta 1
    pregunta_1 = models.CharField(max_length=255, verbose_name="Pregunta de Seguridad 1")
    # La respuesta se guarda hasheada, nunca en texto plano.
    respuesta_1_hash = models.CharField(max_length=128, verbose_name="Respuesta de Seguridad 1 (Hasheada)")

    # Pregunta 2
    pregunta_2 = models.CharField(max_length=255, verbose_name="Pregunta de Seguridad 2")
    respuesta_2_hash = models.CharField(max_length=128, verbose_name="Respuesta de Seguridad 2 (Hasheada)")

    # Método para guardar una respuesta de forma segura (hasheada)
    def set_respuesta1(self, respuesta_plana):
        self.respuesta_1_hash = make_password(respuesta_plana.lower().strip())

    def set_respuesta2(self, respuesta_plana):
        self.respuesta_2_hash = make_password(respuesta_plana.lower().strip())

    # Método para verificar si una respuesta es correcta
    def check_respuesta1(self, respuesta_plana):
        return check_password(respuesta_plana.lower().strip(), self.respuesta_1_hash)

    def check_respuesta2(self, respuesta_plana):
        return check_password(respuesta_plana.lower().strip(), self.respuesta_2_hash)

    def __str__(self):
        return f"Preguntas de seguridad para {self.usuario.username}"

    class Meta:
        verbose_name = "Preguntas de Seguridad de Usuario"
        verbose_name_plural = "Preguntas de Seguridad de Usuarios"
