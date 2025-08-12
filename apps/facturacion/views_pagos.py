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
from pagos.models import Pago
from .serializers_pagos import (
    PagoSerializer,
    PagoCreateSerializer,
    PagoValidacionSerializer,
    FacturaClienteSerializer
)
# from apps.clientes.models import Cliente, ClienteToken  # Ya no se usan - migrado a User model
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


"""
NOTA: Las funciones registrar_pago_cliente y facturas_cliente en este archivo
están OBSOLETAS y han sido reemplazadas por las versiones en pagos/views_api.py
que usan autenticación estándar de Django.

Las funciones obsoletas usaban ClienteToken personalizado que ya no existe.
Ahora se usa el sistema estándar: /api/token/ + Authorization: Token <token>
"""

# Funciones obsoletas comentadas - ver pagos/views_api.py para las nuevas implementaciones

# @api_view(['POST'])
# @permission_classes([AllowClientTokenAuth])
# def registrar_pago_cliente(request):
#     """OBSOLETO - Ver pagos/views_api.py"""
#     pass

# @api_view(['GET'])
# @permission_classes([AllowClientTokenAuth])
# def facturas_cliente(request):
#     """OBSOLETO - Ver pagos/views_api.py"""
#     pass


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
