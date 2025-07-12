from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Proveedor
from .serializers import ProveedorSerializer

class ProveedorViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, editar y eliminar Proveedores.
    """
    queryset = Proveedor.objects.all().order_by('nombre_proveedor') # Obtiene todos los Proveedores, ordenados por nombre
    serializer_class = ProveedorSerializer

    # Permisos: Solo usuarios autenticados pueden interactuar con esta API.
    # Ajusta según tus necesidades (ej. IsAuthenticatedOrReadOnly si quieres permitir lectura anónima)
    permission_classes = [permissions.IsAuthenticated]