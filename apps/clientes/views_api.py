from rest_framework import viewsets, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from apps.usuarios.permissions import AdminOnlyPermission
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.usuarios.permissions import ClientePermission
from .models import Cliente, ClienteToken
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
    
    def destroy(self, request, *args, **kwargs):
        """
        Sobrescribir destroy para crear log de auditoría automáticamente
        """
        cliente = self.get_object()
        
        # Obtener motivo del request.data
        motivo = request.data.get('motivo', 'Eliminación sin motivo especificado')
        
        # Crear log de auditoría ANTES de eliminar
        LogAuditoria.objects.create(
            modelo_afectado='Cliente',
            objeto_id=cliente.id,
            descripcion_objeto=f"{cliente.nombre} ({cliente.email})",
            motivo=motivo,
            usuario=request.user
        )
        
        # Eliminar el cliente
        cliente.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminOnlyPermission])
def generar_token_cliente(request, cliente_id):
    try:
        cliente = Cliente.objects.get(pk=cliente_id)
        token, _ = ClienteToken.objects.get_or_create(cliente=cliente)
        return Response({'token': token.key, 'cliente_id': cliente.id})
    except Cliente.DoesNotExist:
        return Response({'error': 'Cliente no encontrado'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)