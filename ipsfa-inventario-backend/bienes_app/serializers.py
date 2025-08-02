# ipsfa-inventario-backend/bienes_app/serializers.py
from rest_framework import serializers
from .models import Bien, MovimientoBien, Categoria
from django.contrib.auth.models import User
from unidades_administrativas_app.models import UnidadAdministrativa 

class BienSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    unidad_administrativa_actual_nombre = serializers.CharField(
        source='unidad_administrativa_actual.nombre',
        read_only=True,
        required=False
    )
    unidad_administrativa_actual = serializers.PrimaryKeyRelatedField(
        queryset=UnidadAdministrativa.objects.all(),
        allow_null=True,
        required=False
    )
    proveedor_nombre = serializers.CharField(source='proveedor.nombre_proveedor', read_only=True)
    proveedor_rif = serializers.CharField(source='proveedor.rif', read_only=True)

    class Meta:
        model = Bien
        fields = [
            'id', 'codigo_patrimonial', 'codigo_anterior', 'descripcion', 
            'marca', 'modelo', 'serial', 'cantidad', 'fecha_adquisicion',
            'n_orden_compra_factura', 'proveedor', 'proveedor_nombre', 'proveedor_rif',
            'motivo_adquisicion',
            'valor_unitario_bs', 'valor_unitario_usd',
            'ubicacion_fisica_especifica', 'responsable_asignado_nombre', 
            'responsable_asignado_cargo',
            'vida_util_estimada_anios',
            'valor_residual',
            'metodo_depreciacion',
            'estado_bien', 'observaciones', 
            'fecha_creacion', 'fecha_actualizacion',
            'unidad_administrativa_actual',
            'unidad_administrativa_actual_nombre',
            'categoria',
            'categoria_nombre',
        ]
        read_only_fields = ('id', 'fecha_creacion', 'fecha_actualizacion', 'unidad_administrativa_actual_nombre', 'categoria_nombre')

    # def get_estado_bien_display(self, obj):
    #     return obj.get_estado_bien_display()

class MovimientoBienSerializer(serializers.ModelSerializer):
    bien = serializers.PrimaryKeyRelatedField(queryset=Bien.objects.all())
    unidad_origen = serializers.PrimaryKeyRelatedField(
        queryset=UnidadAdministrativa.objects.all(), 
        allow_null=True, 
        required=False
    )
    unidad_destino = serializers.PrimaryKeyRelatedField(
        queryset=UnidadAdministrativa.objects.all(),
        allow_null=True,
        required=False
    )
    usuario_registra = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        required=False, # Puede ser seteado automáticamente en la vista
        allow_null=True
    )

    class Meta:
        model = MovimientoBien
        fields = '__all__' 
        read_only_fields = ('id', 'fecha_creacion_registro')

    def validate(self, data):
        tipo_movimiento = data.get('tipo_movimiento')
        bien = data.get('bien')

        if tipo_movimiento == 'TRASLADO':
            if not data.get('unidad_origen'):
                raise serializers.ValidationError({"unidad_origen": "La unidad de origen es requerida para traslados."})
            if not data.get('unidad_destino'):
                raise serializers.ValidationError({"unidad_destino": "La unidad de destino es requerida para traslados."})
            if not data.get('ubicacion_nueva_especifica'):
                raise serializers.ValidationError({"ubicacion_nueva_especifica": "La nueva ubicación física es requerida para traslados."})
            # Ajuste: Si es la misma unidad, al menos el responsable o la ubicación específica deben cambiar.
            if data.get('unidad_origen') == data.get('unidad_destino'):
                if data.get('responsable_anterior_nombre') == data.get('responsable_nuevo_nombre') and \
                   data.get('ubicacion_anterior_especifica') == data.get('ubicacion_nueva_especifica'):
                     raise serializers.ValidationError({"detail": "Para un traslado dentro de la misma unidad, debe cambiar el responsable, la ubicación específica, o ambos."})

        elif tipo_movimiento == 'DESINCORPORACION':
            if not data.get('motivo_desincorporacion'):
                raise serializers.ValidationError({"motivo_desincorporacion": "El motivo de desincorporación es requerido."})
            if not data.get('numero_oficio_referencia'):
                raise serializers.ValidationError({"numero_oficio_referencia": "El número de oficio o acta es requerido para desincorporaciones."})

        if bien and bien.estado_bien == 'DESINCORPORADO' and tipo_movimiento != 'INCORPORACION':
             raise serializers.ValidationError({"bien": f"El bien '{bien.descripcion}' ya se encuentra desincorporado y no puede ser modificado o trasladado de esta forma."})
        
        # Validación para el caso de incorporación de un bien previamente desincorporado
        if bien and bien.estado_bien == 'DESINCORPORADO' and tipo_movimiento == 'INCORPORACION':
            pass

        return data
    
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'