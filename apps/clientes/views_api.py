"""API views para la gestión de clientes."""

# Django imports
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

# Rest Framework imports
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Silk imports
from silk.profiling.profiler import silk_profile

# Apps imports
from apps.auditorias.models import LogAuditoria
from apps.usuarios.permissions import AdminOnlyPermission, ClientePermission

# Local imports
from .serializers import ClienteSerializer

User = get_user_model()


class ClienteViewSet(viewsets.ModelViewSet):
    swagger_tags = ['👨‍💼 Gestión de Clientes']
    """
    ViewSet para el módulo de Clientes (usuarios con role='Cliente').
    - Administrador, Secretario: Acceso completo (CRUD)
    - Ventas: Solo lectura (GET)
    """
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated, ClientePermission]

    def get_queryset(self):
        """
        Filtrar queryset basado en el rol del usuario.
        Administradores, Secretarios y personal de Ventas pueden ver clientes.
        Solo retorna usuarios con role='Cliente'.
        """
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Secretario', 'Ventas']:
            # Filtrar solo usuarios con role='Cliente' y optimizar consultas
            return User.objects.filter(role='Cliente').select_related().prefetch_related('factura_set')
        return User.objects.none()

    @silk_profile(name='ClienteViewSet.list')
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
    @silk_profile(name='ClienteViewSet.eliminar_con_motivo')
    def eliminar_con_motivo(self, request, pk=None):
        """
        Endpoint personalizado para eliminar un cliente con motivo de auditoría.
        """
        cliente = get_object_or_404(User, pk=pk, role='Cliente')
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

    @silk_profile(name='ClienteViewSet.destroy')
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


from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(method='post', tags=['👨‍💼 Gestión de Clientes'])
@api_view(['POST'])
@permission_classes([IsAuthenticated, AdminOnlyPermission])
@silk_profile(name='generar_token_cliente')
def generar_token_cliente(_, cliente_id):
    """Genera un token estándar de Django REST Framework para un cliente específico."""
    try:
        from rest_framework.authtoken.models import Token
        
        cliente = User.objects.get(pk=cliente_id, role='Cliente')
        token, created = Token.objects.get_or_create(user=cliente)
        
        return Response({
            'token': token.key, 
            'cliente_id': cliente.id,
            'created': created,
            'message': 'Cliente puede usar este token con /api/token/ o en headers Authorization: Token <token_key>'
        })
    except User.DoesNotExist:
        return Response({'error': 'Cliente no encontrado'}, status=404)
    except Exception as exc:
        return Response({'error': str(exc)}, status=500)
