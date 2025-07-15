from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.usuarios.permissions import ProductoPermission
from rest_framework.exceptions import PermissionDenied
from .models import Producto
from .serializers import ProductoSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from apps.auditorias.models import LogAuditoria


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

    @action(detail=True, methods=['post'], url_path='eliminar-con-motivo')
    def eliminar_con_motivo(self, request, pk=None):
        """
        Eliminar un producto con motivo, registrando auditoría.
        Solo permitido para Administrador o Bodega.
        """
        producto = get_object_or_404(Producto, pk=pk)
        motivo = request.data.get('motivo')

        if not motivo:
            return Response({'error': 'El motivo es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar permisos
        user = request.user
        if not (user.is_superuser or user.role in ['Administrador', 'Bodega']):
            return Response({'error': 'No tienes permiso para eliminar este producto.'}, status=403)

        # Registrar en auditoría
        LogAuditoria.objects.create(
            modelo_afectado='Producto',
            objeto_id=producto.id,
            descripcion_objeto=str(producto),
            motivo=motivo,
            usuario=user
        )

        producto.delete()
        return Response({'mensaje': 'Producto eliminado y registrado en auditoría.'}, status=status.HTTP_204_NO_CONTENT)
    
    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribir destroy para crear log de auditoría automáticamente
        """
        producto = self.get_object()
        
        # Obtener motivo del request.data
        motivo = request.data.get('motivo', 'Eliminación sin motivo especificado')
        
        # Crear log de auditoría ANTES de eliminar
        LogAuditoria.objects.create(
            modelo_afectado='Producto',
            objeto_id=producto.id,
            descripcion_objeto=f"{producto.nombre} - ${producto.precio}",
            motivo=motivo,
            usuario=request.user
        )
        
        # Eliminar el producto
        producto.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)