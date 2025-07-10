from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.usuarios.permissions import ClientePermission
from .models import Cliente
from .serializers import ClienteSerializer

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el módulo de Clientes.
    - Administrador, Secretario: Acceso completo (CRUD)
    - Ventas: Solo lectura (GET)
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, ClientePermission]

    def get_queryset(self):
        """
        Filtrar queryset basado en el rol del usuario.
        Administradores, Secretarios y personal de Ventas pueden ver clientes.
        """
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Secretario', 'Ventas']:
            return Cliente.objects.all()
        return Cliente.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Listar clientes.
        Permitido para: Administrador, Secretario, Ventas (solo lectura)
        """
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'Secretario', 'Ventas']):
            raise PermissionDenied("No tienes permiso para acceder a los clientes")
        return super().list(request, *args, **kwargs)