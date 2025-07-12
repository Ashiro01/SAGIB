from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import AuditLog
from .serializers import AuditLogSerializer
import django_filters.rest_framework

class AuditLogFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = AuditLog
        fields = {
            'timestamp': ['gte', 'lte'], # gte (mayor o igual), lte (menor o igual)
            'usuario__username': ['exact', 'icontains'], # exacto o insensible a mayúsculas/minúsculas
            'accion': ['exact'],
        }

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint de solo lectura para ver los Logs de Auditoría.
    Permite filtrar por rango de fecha, usuario y acción.
    """
    queryset = AuditLog.objects.all().order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser] # Solo administradores pueden ver los logs
    
    # Habilitar filtros avanzados
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter]
    filterset_class = AuditLogFilter
    
    # Habilitar búsqueda simple (adicional a los filtros)
    search_fields = ['detalles', 'ip_address']