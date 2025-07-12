# ipsfa-inventario-backend/proveedores_app/models.py
from django.db import models
from django.utils import timezone

class Proveedor(models.Model):
    nombre_proveedor = models.CharField(max_length=255, unique=True, verbose_name="Nombre del Proveedor")
    rif = models.CharField(max_length=20, unique=True, blank=True, null=True, verbose_name="RIF del Proveedor") # Registro de Información Fiscal
    direccion_fiscal = models.TextField(blank=True, null=True, verbose_name="Dirección Fiscal")
    contacto_principal_nombre = models.CharField(max_length=150, blank=True, null=True, verbose_name="Nombre del Contacto Principal")
    contacto_principal_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name="Email del Contacto Principal")
    contacto_principal_telefono = models.CharField(max_length=50, blank=True, null=True, verbose_name="Teléfono del Contacto Principal")

    # Podríamos añadir más campos como:
    # tipo_proveedor = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tipo de Proveedor (Ej: Bienes, Servicios)")
    # pagina_web = models.URLField(blank=True, null=True, verbose_name="Página Web")
    # notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    activo = models.BooleanField(default=True, verbose_name="Proveedor Activo") # Para poder desactivar proveedores sin eliminarlos

    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    def __str__(self):
        return self.nombre_proveedor

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['nombre_proveedor']