# ipsfa-inventario-backend/bienes_app/serializers.py
from rest_framework import serializers
from .models import Bien, MovimientoBien # Asegúrate de importar MovimientoBien
from django.contrib.auth.models import User
from unidades_administrativas_app.models import UnidadAdministrativa 

class BienSerializer(serializers.ModelSerializer):
    # Si quieres que algunos campos sean de solo lectura en la API (ej. generados por el sistema)
    # puedes definirlos aquí. Por ejemplo:
    # codigo_patrimonial = serializers.CharField(read_only=True, allow_null=True)
    # fecha_creacion = serializers.DateTimeField(read_only=True)
    # fecha_actualizacion = serializers.DateTimeField(read_only=True)

    # Para campos 'choice' como estado_bien, DRF los maneja bien por defecto.
    # Si quieres mostrar el "display name" (ej. "Nuevo") además del valor guardado ("NUEVO")
    # podrías añadir un campo SerializerMethodField:
    # estado_bien_display = serializers.CharField(source='get_estado_bien_display', read_only=True)

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

    class Meta:
        model = Bien
        fields = [
            'id', 'codigo_patrimonial', 'codigo_anterior', 'descripcion', 
            'marca', 'modelo', 'serial', 'cantidad', 'fecha_adquisicion',
            'n_orden_compra_factura', 'nombre_proveedor', 
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
        ]
        read_only_fields = ('id', 'fecha_creacion', 'fecha_actualizacion', 'unidad_administrativa_actual_nombre')

    # def get_estado_bien_display(self, obj):
    #     return obj.get_estado_bien_display()

class MovimientoBienSerializer(serializers.ModelSerializer):
    # Para mostrar información legible en lugar de solo IDs (opcional, para lectura)
    # bien_detalle = BienSerializer(source='bien', read_only=True) 
    # unidad_origen_detalle = UnidadAdministrativaSerializer(source='unidad_origen', read_only=True) # Necesitarías UnidadAdministrativaSerializer
    # unidad_destino_detalle = UnidadAdministrativaSerializer(source='unidad_destino', read_only=True) # Necesitarías UnidadAdministrativaSerializer
    # usuario_registra_username = serializers.CharField(source='usuario_registra.username', read_only=True)

    # Para la creación, usualmente enviaremos los IDs de las FK
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
            # Aquí podrías decidir si esto es permitido o no.
            # Si es permitido, asegúrate de que la lógica en perform_create del ViewSet maneje correctamente
            # el cambio de estado del bien (ej. a 'NUEVO' o 'BUENO').
            # Por ahora, no añadiré una validación que lo impida, asumiendo que perform_create lo manejará.
            pass # Permitir, será manejado en la vista

        return data