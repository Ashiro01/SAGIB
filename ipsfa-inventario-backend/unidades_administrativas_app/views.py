from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import UnidadAdministrativa
from .serializers import UnidadAdministrativaSerializer

# Create your views here.

class UnidadAdministrativaViewSet(viewsets.ModelViewSet):
    """
    API endpoint que permite ver, crear, editar y eliminar Unidades Administrativas.
    """
    queryset = UnidadAdministrativa.objects.all().order_by('nombre')
    serializer_class = UnidadAdministrativaSerializer
    permission_classes = [permissions.IsAuthenticated]
