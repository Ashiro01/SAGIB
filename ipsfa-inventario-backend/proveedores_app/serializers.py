# ipsfa-inventario-backend/proveedores_app/serializers.py
from rest_framework import serializers
from .models import Proveedor # Importa tu modelo Proveedor

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__' # Incluye todos los campos del modelo Proveedor
        # O puedes ser específico:
        # fields = [
        # 'id', 'nombre_proveedor', 'rif', 'direccion_fiscal',
        # 'contacto_principal_nombre', 'contacto_principal_email', 
        # 'contacto_principal_telefono', 'activo', 
        # 'fecha_registro', 'ultima_actualizacion'
        # ]
        read_only_fields = ('id', 'fecha_registro', 'ultima_actualizacion') # Campos que no se envían al crear/actualizar