"""API views para la gestión de pagos."""

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes, action, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from silk.profiling.profiler import silk_profile

# Autenticación personalizada para clientes
from apps.clientes.authentication import ClienteTokenAuthentication
from apps.usuarios.permissions import AdminOnlyPermission
from apps.auditorias.models import LogAuditoria
from .permissions import PagoPermission

from .models import Pago, HistorialPago
from .serializers import (
    PagoSerializer, PagoCreateSerializer, PagoDetailSerializer,
    PagoPendienteSerializer, PagoValidacionSerializer
)


class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión completa de pagos.
    Solo administradores y usuarios con rol Pagos pueden acceder.
    """
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated, PagoPermission]
    
    def get_queryset(self):
        """Obtener queryset optimizado con filtros personalizados."""
        queryset = Pago.objects.select_related(
            'factura', 'pagado_por', 'validado_por'
        ).order_by('-fecha_pago')
        
        # Aplicar filtros basados en parámetros de query
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        tipo_pago = self.request.query_params.get('tipo_pago', None)
        if tipo_pago:
            queryset = queryset.filter(tipo_pago=tipo_pago)
        
        cliente_id = self.request.query_params.get('factura__cliente', None)
        if cliente_id:
            try:
                cliente_id = int(cliente_id)
                queryset = queryset.filter(factura__cliente_id=cliente_id)
            except (ValueError, TypeError):
                # Si el ID no es válido, devolver queryset vacío
                queryset = queryset.none()
        
        pagado_por = self.request.query_params.get('pagado_por', None)
        if pagado_por:
            try:
                pagado_por = int(pagado_por)
                queryset = queryset.filter(pagado_por_id=pagado_por)
            except (ValueError, TypeError):
                queryset = queryset.none()
        
        return queryset
    
    def get_serializer_class(self):
        """Seleccionar serializer según la acción."""
        if self.action == 'retrieve':
            return PagoDetailSerializer
        elif self.action in ['list'] and self.request.GET.get('pendientes'):
            return PagoPendienteSerializer
        return PagoSerializer
    
    @action(detail=False, methods=['get'])
    def pendientes(self, request):
        """Listar solo pagos pendientes."""
        pagos_pendientes = self.get_queryset().filter(estado='pendiente')
        serializer = PagoPendienteSerializer(pagos_pendientes, many=True)
        return Response({
            'count': pagos_pendientes.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    @silk_profile(name='PagoViewSet.validar')
    def validar(self, request, pk=None):
        """Validar (aprobar o rechazar) un pago."""
        pago = self.get_object()
        
        if not pago.puede_validar_usuario(request.user):
            raise PermissionDenied("No tienes permisos para validar este pago")
        
        if not pago.esta_pendiente:
            return Response(
                {'error': 'Este pago ya ha sido validado'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PagoValidacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        accion = serializer.validated_data['accion']
        motivo = serializer.validated_data.get('motivo', '')
        
        try:
            # Registrar en historial antes del cambio
            estado_anterior = pago.estado
            
            if accion == 'aprobar':
                pago.aprobar(request.user)
                mensaje = f'Pago #{pago.id} aprobado exitosamente'
                
                # Enviar notificación
                self._enviar_notificacion_aprobacion(pago)
                
            elif accion == 'rechazar':
                pago.rechazar(request.user, motivo)
                mensaje = f'Pago #{pago.id} rechazado'
                
                # Enviar notificación
                self._enviar_notificacion_rechazo(pago, motivo)
            
            # Registrar en auditoría
            LogAuditoria.objects.create(
                modelo_afectado='Pago',
                objeto_id=pago.id,
                descripcion_objeto=str(pago),
                motivo=f"Pago {accion} - {motivo}" if motivo else f"Pago {accion}",
                usuario=request.user
            )
            
            # Registrar en historial de pagos
            HistorialPago.objects.create(
                pago=pago,
                estado_anterior=estado_anterior,
                estado_nuevo=pago.estado,
                usuario=request.user,
                observaciones=motivo
            )
            
            return Response({
                'success': True,
                'message': mensaje,
                'pago_id': pago.id,
                'nuevo_estado': pago.estado,
                'fecha_validacion': pago.fecha_validacion
            })
            
        except Exception as e:
            return Response(
                {'error': f'Error al validar el pago: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtener estadísticas de pagos."""
        from django.db.models import Count, Sum
        from django.utils import timezone
        from datetime import timedelta
        
        # Estadísticas generales
        total_pagos = self.get_queryset().count()
        pagos_pendientes = self.get_queryset().filter(estado='pendiente').count()
        pagos_aprobados = self.get_queryset().filter(estado='aprobado').count()
        pagos_rechazados = self.get_queryset().filter(estado='rechazado').count()
        
        # Monto total de pagos aprobados
        monto_total_aprobado = self.get_queryset().filter(
            estado='aprobado'
        ).aggregate(Sum('monto'))['monto__sum'] or 0
        
        # Pagos de los últimos 30 días
        hace_30_dias = timezone.now() - timedelta(days=30)
        pagos_recientes = self.get_queryset().filter(
            fecha_pago__gte=hace_30_dias
        ).count()
        
        # Distribución por tipo de pago
        tipos_pago = self.get_queryset().values('tipo_pago').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_pagos': total_pagos,
            'pagos_pendientes': pagos_pendientes,
            'pagos_aprobados': pagos_aprobados,
            'pagos_rechazados': pagos_rechazados,
            'monto_total_aprobado': float(monto_total_aprobado),
            'pagos_ultimos_30_dias': pagos_recientes,
            'distribucion_tipos_pago': tipos_pago
        })
    
    def _enviar_notificacion_aprobacion(self, pago):
        """Enviar notificación de aprobación."""
        try:
            asunto = f"Pago Aprobado - Factura #{pago.factura.numero_factura or pago.factura.id}"
            mensaje = f"""
Estimado/a {pago.pagado_por.nombre},

Su pago ha sido APROBADO exitosamente.

Detalles del pago:
- Pago ID: #{pago.id}
- Factura: #{pago.factura.numero_factura or pago.factura.id}
- Monto: ${pago.monto}
- Tipo de pago: {pago.get_tipo_pago_display()}

La factura ahora aparece como PAGADA en el sistema.

Sistema de Facturación Segura
            """
            
            send_mail(
                asunto, mensaje, settings.EMAIL_HOST_USER,
                [pago.pagado_por.email], fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando email de aprobación: {e}")
    
    def _enviar_notificacion_rechazo(self, pago, motivo):
        """Enviar notificación de rechazo."""
        try:
            asunto = f"Pago Rechazado - Factura #{pago.factura.numero_factura or pago.factura.id}"
            mensaje = f"""
Estimado/a {pago.pagado_por.nombre},

Su pago ha sido RECHAZADO.

Motivo: {motivo}

Por favor, revise la información y vuelva a intentar.

Sistema de Facturación Segura
            """
            
            send_mail(
                asunto, mensaje, settings.EMAIL_HOST_USER,
                [pago.pagado_por.email], fail_silently=True
            )
        except Exception as e:
            print(f"Error enviando email de rechazo: {e}")


@api_view(['POST'])
@authentication_classes([ClienteTokenAuthentication])
@permission_classes([IsAuthenticated])
@silk_profile(name='registrar_pago_cliente')
def registrar_pago_cliente(request):
    """
    API para que los clientes registren pagos usando token personalizado.
    Este endpoint usa autenticación por token de cliente.
    """
    try:
        # El cliente se obtiene del sistema de autenticación personalizado
        cliente = request.user
        
        # Validar que el request tenga los datos necesarios
        serializer = PagoCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Verificar que la factura pertenezca al cliente autenticado
        factura = serializer.validated_data['factura']
        if factura.cliente != cliente:
            return Response(
                {'error': 'Solo puede pagar sus propias facturas'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Crear el pago
        pago = serializer.save()
        
        # Registrar en auditoría
        LogAuditoria.objects.create(
            modelo_afectado='Pago',
            objeto_id=pago.id,
            descripcion_objeto=str(pago),
            motivo=f"Pago registrado por cliente via API - {pago.tipo_pago}",
            usuario=None  # No hay usuario del sistema, es un cliente
        )
        
        # Respuesta exitosa
        response_serializer = PagoSerializer(pago)
        return Response({
            'success': True,
            'message': 'Pago registrado exitosamente. Está pendiente de validación.',
            'pago': response_serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'Error al registrar el pago: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@authentication_classes([ClienteTokenAuthentication])
@permission_classes([IsAuthenticated])
def mis_pagos_api(request):
    """
    API para que los clientes consulten sus propios pagos.
    """
    try:
        cliente = request.user
        pagos = Pago.objects.filter(pagado_por=cliente).select_related(
            'factura', 'validado_por'
        ).order_by('-fecha_pago')
        
        serializer = PagoSerializer(pagos, many=True)
        return Response({
            'count': pagos.count(),
            'pagos': serializer.data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener los pagos: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def facturas_pendientes_pago(request):
    """
    API para obtener facturas del cliente que están pendientes de pago.
    Puede usar tanto autenticación de usuario como de cliente.
    """
    try:
        # Determinar el cliente según el tipo de autenticación
        if hasattr(request.user, 'email'):
            # Usuario del sistema
            from apps.clientes.models import Cliente
            try:
                cliente = Cliente.objects.get(email=request.user.email)
            except Cliente.DoesNotExist:
                return Response(
                    {'error': 'No se encontró un cliente asociado'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Cliente autenticado con token personalizado
            cliente = request.user
        
        # Obtener facturas emitidas que no estén pagadas
        from apps.facturacion.models import Factura
        facturas_pendientes = Factura.objects.filter(
            cliente=cliente,
            estado='EMITIDA'  # Solo facturas emitidas pueden ser pagadas
        ).select_related('creador')
        
        # Serializar las facturas
        facturas_data = []
        for factura in facturas_pendientes:
            facturas_data.append({
                'id': factura.id,
                'numero_factura': factura.numero_factura,
                'total': factura.total,
                'fecha': factura.fecha,
                'estado': factura.get_estado_display(),
                'creador': factura.creador.username
            })
        
        return Response({
            'count': len(facturas_data),
            'facturas_pendientes': facturas_data
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error al obtener las facturas: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
