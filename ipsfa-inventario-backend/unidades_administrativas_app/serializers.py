from rest_framework import serializers
from .models import UnidadAdministrativa

class UnidadAdministrativaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadAdministrativa
        fields = '__all__'
        read_only_fields = ('id', 'fecha_registro', 'ultima_actualizacion')
