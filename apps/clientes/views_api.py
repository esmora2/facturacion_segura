from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.usuarios.permissions import ClientePermission
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el módulo de Clientes.
    Acceso permitido solo a: Administrador, Secretario
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, ClientePermission]

    def get_queryset(self):
        """
        Filtrar queryset basado en el rol del usuario.
        Solo Administradores y Secretarios pueden ver clientes.
        """
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Secretario']:
            return Cliente.objects.all()
        return Cliente.objects.none()
