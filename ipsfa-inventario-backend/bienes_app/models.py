# ipsfa-inventario-backend/bienes_app/models.py
from django.db import models
from django.utils import timezone # Para la fecha de adquisición por defecto
from django.contrib.auth.models import User # Para el usuario que realiza la acción
from unidades_administrativas_app.models import UnidadAdministrativa

# Podríamos definir choices (opciones) para campos como 'estado_bien' aquí
ESTADO_BIEN_CHOICES = [
    ('NUEVO', 'Nuevo'),
    ('BUENO', 'Bueno'),
    ('REGULAR', 'Regular'),
    ('MALO', 'Malo'),
    ('EN_REPARACION', 'En Reparación'),
    ('OBSOLETO', 'Obsoleto'),
    ('DESINCORPORADO', 'Desincorporado'),
]

MOTIVO_ADQUISICION_CHOICES = [
    ('COMPRA_DIRECTA', 'Compra Directa'),
    ('LICITACION', 'Licitación Pública'),
    ('DACION_PAGO', 'Dación en Pago'),
    ('DONACION', 'Donación'),
    ('TRANSFERENCIA', 'Transferencia de Otros Organismos'),
    ('CONSTRUCCION_PROPIA', 'Construcción Propia'),
    ('RECUPERACION', 'Recuperación de Bienes'),
    ('COMODATO', 'Comodato'),
    ('ARRENDAMIENTO', 'Arrendamiento con Opción de Compra'),
    ('HERENCIA', 'Herencia o Legado'),
    ('OTRO', 'Otro'),
]

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría de Bien"
        verbose_name_plural = "Categorías de Bienes"
        ordering = ['nombre']

class Bien(models.Model):
    # --- Información Básica y de Identificación ---
    codigo_patrimonial = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, # Puede ser blank si se genera automáticamente
        null=True,  # Permitir null si se genera después
        verbose_name="Código Patrimonial (Generado por el Sistema)"
    )
    codigo_anterior = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Código de Inventario Anterior"
    )
    descripcion = models.TextField(verbose_name="Descripción del Bien")
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Categoría"
    )

    # --- Detalles del Bien ---
    marca = models.CharField(max_length=100, blank=True, null=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, null=True, verbose_name="Modelo")
    serial = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="Serial del Fabricante") # Serial debería ser único si existe
    cantidad = models.PositiveIntegerField(default=1, verbose_name="Cantidad")

    # --- Información de Adquisición ---
    fecha_adquisicion = models.DateField(default=timezone.now, verbose_name="Fecha de Adquisición")
    n_orden_compra_factura = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="N° Orden de Compra o Factura"
    )
    # Relación con el modelo Proveedor
    proveedor = models.ForeignKey(
        'proveedores_app.Proveedor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Proveedor"
    ) 

    motivo_adquisicion = models.CharField(
        max_length=50,
        choices=MOTIVO_ADQUISICION_CHOICES,
        default='COMPRA_DIRECTA',
        verbose_name="Motivo de Adquisición"
    )

    valor_unitario_bs = models.DecimalField(
        max_digits=19, # Suficiente para números grandes (ej: miles de billones)
        decimal_places=2, 
        verbose_name="Valor Unitario en Bs."
    )
    valor_unitario_usd = models.DecimalField(
        max_digits=19, 
        decimal_places=2, 
        blank=True, 
        null=True, # El valor en USD puede ser opcional
        verbose_name="Valor Unitario en $"
    )

    ubicacion_fisica_especifica = models.CharField(max_length=255, verbose_name="Ubicación Física Específica")
    
    unidad_administrativa_actual = models.ForeignKey(
        UnidadAdministrativa, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bienes_asignados',
        verbose_name="Unidad Administrativa Actual"
    )

    responsable_asignado_nombre = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre del Responsable Asignado")
    responsable_asignado_cargo = models.CharField(max_length=150, blank=True, null=True, verbose_name="Cargo del Responsable Asignado")
    METODO_DEPRECIACION_CHOICES = [
        ('LINEA_RECTA', 'Línea Recta'),
        ('SALDO_DECRECIENTE', 'Saldo Decreciente'),
    ]
    vida_util_estimada_anios = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Vida Útil Estimada (Años)"
    )
    valor_residual = models.DecimalField(
        max_digits=19,
        decimal_places=2,
        default=0.00,
        verbose_name="Valor Residual o de Salvamento (Bs.)"
    )
    metodo_depreciacion = models.CharField(
        max_length=50,
        choices=METODO_DEPRECIACION_CHOICES,
        blank=True,
        null=True,
        verbose_name="Método de Depreciación"
    )

    estado_bien = models.CharField(
        max_length=20,
        choices=ESTADO_BIEN_CHOICES,
        default='NUEVO',
        verbose_name="Estado del Bien"
    )
    observaciones = models.TextField(blank=True, null=True, verbose_name="Observaciones")

    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")


    def __str__(self):
        return f"{self.codigo_patrimonial} - {self.descripcion}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Guarda primero para obtener el ID
        if is_new and not self.codigo_patrimonial:
            year = self.fecha_creacion.year if self.fecha_creacion else timezone.now().year
            self.codigo_patrimonial = f"IPSFA-BM-{year}-{self.pk:05d}"
            super().save(update_fields=['codigo_patrimonial'])

    class Meta:
        verbose_name = "Bien"
        verbose_name_plural = "Bienes"
        ordering = ['-fecha_creacion', 'descripcion'] # Orden por defecto al consultar

class MovimientoBien(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('INCORPORACION', 'Incorporación'),
        ('TRASLADO', 'Traslado'),
        ('DESINCORPORACION', 'Desincorporación'),
        ('ACTUALIZACION_ESTADO', 'Actualización de Estado'),
        # Podrías añadir más tipos si es necesario
    ]

    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='movimientos', verbose_name="Bien Afectado")
    tipo_movimiento = models.CharField(max_length=30, choices=TIPO_MOVIMIENTO_CHOICES, verbose_name="Tipo de Movimiento")
    fecha_movimiento = models.DateTimeField(default=timezone.now, verbose_name="Fecha y Hora del Movimiento")

    # Campos específicos para Traslados (pueden ser null para otros tipos de movimientos)
    unidad_origen = models.ForeignKey(
        UnidadAdministrativa, # Usar string si el modelo está en otra app
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='movimientos_origen',
        verbose_name="Unidad de Origen"
    )
    unidad_destino = models.ForeignKey(
        UnidadAdministrativa, # Usar string si el modelo está en otra app
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='movimientos_destino',
        verbose_name="Unidad de Destino"
    )
    responsable_anterior_nombre = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre del Responsable Anterior")
    responsable_nuevo_nombre = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre del Responsable Nuevo")
    ubicacion_anterior_especifica = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ubicación Física Anterior")
    ubicacion_nueva_especifica = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ubicación Física Nueva")

    # Campos para Desincorporaciones (pueden ser null para otros tipos)
    motivo_desincorporacion = models.TextField(blank=True, null=True, verbose_name="Motivo de Desincorporación/Movimiento")
    numero_oficio_referencia = models.CharField(max_length=100, blank=True, null=True, verbose_name="N° Oficio o Documento de Referencia")
    # Considerar un campo para el estado final del bien en desincorporaciones, si es diferente al tipo de movimiento

    # Auditoría del movimiento
    usuario_registra = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, # Quién registró el movimiento
        null=True, 
        blank=True, # Puede ser null si es un proceso automático, aunque es raro
        related_name='movimientos_registrados',
        verbose_name="Usuario que Registra"
    )
    observaciones_movimiento = models.TextField(blank=True, null=True, verbose_name="Observaciones del Movimiento")

    fecha_creacion_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación del Registro")

    def __str__(self):
        return f"{self.get_tipo_movimiento_display()} - {self.bien.descripcion} - {self.fecha_movimiento.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Movimiento de Bien"
        verbose_name_plural = "Movimientos de Bienes"
        ordering = ['-fecha_movimiento', '-fecha_creacion_registro']

class DepreciacionMensual(models.Model):
    bien = models.ForeignKey(Bien, on_delete=models.CASCADE, related_name='depreciaciones', verbose_name="Bien Depreciado")
    mes = models.PositiveIntegerField(verbose_name="Mes del Cálculo")
    anio = models.PositiveIntegerField(verbose_name="Año del Cálculo")

    valor_depreciado_mes = models.DecimalField(max_digits=19, decimal_places=2, verbose_name="Valor Depreciado en el Mes")
    depreciacion_acumulada = models.DecimalField(max_digits=19, decimal_places=2, verbose_name="Depreciación Acumulada")
    valor_neto_en_libros = models.DecimalField(max_digits=19, decimal_places=2, verbose_name="Valor Neto en Libros")

    fecha_calculo = models.DateTimeField(auto_now_add=True, verbose_name="Fecha del Cálculo")

    class Meta:
        unique_together = ('bien', 'mes', 'anio')
        verbose_name = "Cálculo de Depreciación"
        verbose_name_plural = "Cálculos de Depreciación"
        ordering = ['-anio', '-mes']

    def __str__(self):
        return f"Depreciación de '{self.bien.descripcion}' para {self.mes}/{self.anio}"