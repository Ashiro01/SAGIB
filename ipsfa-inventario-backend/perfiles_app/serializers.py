# perfiles_app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import PerfilUsuario, PreguntaSeguridad, RespuestaSeguridadUsuario

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerfilUsuario
        fields = ['foto_perfil']

class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer para los detalles del usuario que él mismo puede editar."""
    perfil = PerfilUsuarioSerializer(required=False)
    rol = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'perfil', 'rol', 'nombre_completo']
        read_only_fields = ['username'] # El username no se puede cambiar

    def get_rol(self, obj):
        """Obtiene el rol principal del usuario (primer grupo)"""
        if obj.groups.exists():
            return obj.groups.first().name
        return 'Usuario'

    def get_nombre_completo(self, obj):
        """Obtiene el nombre completo del usuario"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return obj.username

    def update(self, instance, validated_data):
        perfil_data = validated_data.pop('perfil', {})
        perfil = instance.perfil

        # Actualizar campos del User
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Actualizar campos del Perfil (la foto)
        if perfil_data.get('foto_perfil') is not None:
             perfil.foto_perfil = perfil_data.get('foto_perfil', perfil.foto_perfil)
             perfil.save()

        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para el cambio de contraseña."""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Las nuevas contraseñas no coinciden."})
        return data

class PreguntaSeguridadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreguntaSeguridad
        fields = ['id', 'texto']

class RespuestaSeguridadUsuarioSerializer(serializers.ModelSerializer):
    # Para lectura, mostramos el texto de la pregunta
    pregunta_texto = serializers.CharField(source='pregunta.texto', read_only=True)

    # Para escritura, solo necesitamos el ID de la pregunta y la respuesta en texto plano
    pregunta = serializers.PrimaryKeyRelatedField(queryset=PreguntaSeguridad.objects.all(), write_only=True)
    respuesta_plana = serializers.CharField(write_only=True, required=True, label="Respuesta")

    class Meta:
        model = RespuestaSeguridadUsuario
        fields = ['id', 'pregunta', 'pregunta_texto', 'respuesta_plana']
        read_only_fields = ['id', 'pregunta_texto']

    def create(self, validated_data):
        respuesta_plana = validated_data.pop('respuesta_plana')
        respuesta = RespuestaSeguridadUsuario(**validated_data)
        respuesta.set_respuesta(respuesta_plana) # Usamos el método del modelo para hashear
        respuesta.save()
        return respuesta