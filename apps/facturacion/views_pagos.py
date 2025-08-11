"""API views para el sistema de pagos."""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

from silk.profiling.profiler import silk_profile

from .models import Factura
from .models_pagos import Pago
from .serializers_pagos import (
    PagoSerializer, 
    PagoCreateSerializer, 
    PagoValidacionSerializer,
    FacturaClienteSerializer
)
from apps.clientes.models import Cliente, ClienteToken
from apps.usuarios.permissions import AdminOnlyPermission
from .permissions import AllowClientTokenAuth, PagosRolePermission


class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pagos.
    - Usuarios con rol 'pagos': pueden ver y validar pagos pendientes
    - Administradores: acceso completo
    """
    serializer_class = PagoSerializer
    permission_classes = [PagosRolePermission]

    def get_queryset(self):
        """Filtrar pagos según el rol del usuario."""
        user = self.request.user
        
        if user.is_superuser or user.role == 'Administrador':
            # Administradores ven todos los pagos
            return Pago.objects.select_related(
                'factura', 'pagado_por', 'validado_por'
            ).all()
        elif user.role == 'pagos':
            # Usuarios con rol pagos solo ven pagos pendientes
            return Pago.objects.filter(estado='pendiente').select_related(
                'factura', 'pagado_por', 'validado_por'
            )
        else:
            return Pago.objects.none()

    @silk_profile(name='PagoViewSet.list')
    def list(self, request, *args, **kwargs):
        """Listar pagos según rol del usuario."""
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'pagos']):
            raise PermissionDenied("No tienes permiso para ver los pagos")
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='validar')
    @silk_profile(name='PagoViewSet.validar')
    def validar_pago(self, request, pk=None):
        """
        Endpoint para aprobar o rechazar pagos.
        Solo usuarios con rol 'pagos' o administradores.
        """
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'pagos']):
            raise PermissionDenied("No tienes permiso para validar pagos")

        pago = get_object_or_404(Pago, pk=pk)
        
        if not pago.puede_validar():
            return Response(
                {'error': 'El pago no está en estado pendiente'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PagoValidacionSerializer(data=request.data)
        if serializer.is_valid():
            accion = serializer.validated_data['accion']
            motivo = serializer.validated_data.get('motivo', '')

            try:
                if accion == 'aprobar':
                    pago.aprobar(user)
                    return Response({
                        'mensaje': 'Pago aprobado exitosamente',
                        'factura_estado': pago.factura.estado
                    })
                elif accion == 'rechazar':
                    pago.rechazar(user, motivo)
                    return Response({
                        'mensaje': 'Pago rechazado exitosamente'
                    })
            except ValueError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowClientTokenAuth])
def registrar_pago_cliente(request):
    """
    Endpoint para que los clientes registren pagos usando su token.
    Header requerido: X-Client-Token: <cliente_token>
    
    IMPORTANTE: Usa AllowClientTokenAuth para bypass de autenticación Django
    """
    # Obtener token del header personalizado
    client_token = request.META.get('HTTP_X_CLIENT_TOKEN', '')
    
    if not client_token:
        return Response(
            {'error': 'Header X-Client-Token requerido'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Verificar token del cliente
        cliente_token = ClienteToken.objects.select_related('cliente').get(key=client_token)
        cliente = cliente_token.cliente
    except ClienteToken.DoesNotExist:
        return Response(
            {'error': 'Token de cliente inválido'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Validar datos del pago
    serializer = PagoCreateSerializer(data=request.data)
    if serializer.is_valid():
        factura_id = serializer.validated_data['factura'].id
        
        # Verificar que la factura pertenezca al cliente
        try:
            factura = Factura.objects.get(id=factura_id, cliente=cliente)
        except Factura.DoesNotExist:
            return Response(
                {'error': 'La factura no existe o no pertenece al cliente'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Crear el pago
        pago = serializer.save(pagado_por=cliente)
        
        # Serializar respuesta
        response_serializer = PagoSerializer(pago)
        return Response({
            'mensaje': 'Pago registrado exitosamente. Será validado por el equipo de pagos.',
            'pago': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowClientTokenAuth])
@silk_profile(name='facturas_cliente')
def facturas_cliente(request):
    """
    Endpoint para que los clientes vean sus facturas pendientes de pago.
    Header requerido: X-Client-Token: <cliente_token>
    
    IMPORTANTE: Usa AllowClientTokenAuth para bypass de autenticación Django
    """
    # Obtener token del header personalizado
    client_token = request.META.get('HTTP_X_CLIENT_TOKEN', '')
    if not client_token:
        return Response(
            {'error': 'Header X-Client-Token requerido'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        # Verificar token del cliente
        cliente_token = ClienteToken.objects.select_related('cliente').get(key=client_token)
        cliente = cliente_token.cliente
    except ClienteToken.DoesNotExist:
        return Response(
            {'error': 'Token de cliente inválido'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Obtener facturas del cliente que no están pagadas ni anuladas
    facturas = Factura.objects.filter(
        cliente=cliente,
        estado__in=['PENDIENTE', 'EMITIDA']
    ).prefetch_related('pagos').order_by('-fecha')
    
    serializer = FacturaClienteSerializer(facturas, many=True)
    return Response({
        'cliente': cliente.nombre,
        'facturas': serializer.data
    })


@api_view(['GET'])
@permission_classes([PagosRolePermission])
@silk_profile(name='pagos_pendientes')
def pagos_pendientes(request):
    """
    Endpoint para que usuarios con rol 'pagos' vean pagos pendientes.
    """
    user = request.user
    if not (user.is_superuser or user.role in ['Administrador', 'pagos']):
        raise PermissionDenied("No tienes permiso para ver pagos pendientes")

    pagos = Pago.objects.filter(estado='pendiente').select_related(
        'factura', 'pagado_por'
    ).order_by('-created_at')
    
    serializer = PagoSerializer(pagos, many=True)
    return Response({
        'total_pendientes': pagos.count(),
        'pagos': serializer.data
    })
