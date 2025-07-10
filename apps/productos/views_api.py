from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.usuarios.permissions import ProductoPermission
from rest_framework.exceptions import PermissionDenied
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el módulo de Productos.
    - Administrador, Bodega: Acceso completo (CRUD)
    - Ventas: Solo lectura (GET)
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated, ProductoPermission]

    def get_queryset(self):
        """
        Filtrar queryset basado en el rol del usuario.
        Administradores, personal de Bodega y personal de Ventas pueden ver productos.
        """
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Bodega', 'Ventas']:
            return Producto.objects.all()
        return Producto.objects.none()

    def list(self, request, *args, **kwargs):
        """
        Listar productos.
        Permitido para: Administrador, Bodega, Ventas (solo lectura)
        """
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'Bodega', 'Ventas']):
            raise PermissionDenied("No tienes permiso para acceder a los productos")
        return super().list(request, *args, **kwargs)