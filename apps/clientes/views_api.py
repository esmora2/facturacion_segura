from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.usuarios.permissions import ClientePermission
from .models import Cliente
from .serializers import ClienteSerializer

# 🔽 Importar modelo de auditorías
from apps.auditorias.models import LogAuditoria


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

    @action(detail=True, methods=['post'], url_path='eliminar-con-motivo')
    def eliminar_con_motivo(self, request, pk=None):
        """
        Endpoint personalizado para eliminar un cliente con motivo de auditoría.
        """
        cliente = get_object_or_404(Cliente, pk=pk)
        motivo = request.data.get('motivo')

        if not motivo:
            return Response({'error': 'El motivo es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Registrar auditoría
        LogAuditoria.objects.create(
            modelo_afectado='Cliente',
            objeto_id=cliente.id,
            descripcion_objeto=str(cliente),
            motivo=motivo,
            usuario=request.user
        )

        cliente.delete()
        return Response({'mensaje': 'Cliente eliminado con motivo registrado.'}, status=status.HTTP_204_NO_CONTENT)
