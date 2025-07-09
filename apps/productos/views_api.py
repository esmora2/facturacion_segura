from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Producto
from .serializers import ProductoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Bodega']:
            return Producto.objects.all()
        return Producto.objects.none()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'Bodega']):
            raise PermissionDenied("No tienes permiso para acceder a los productos")
        return super().list(request, *args, **kwargs)