"""Serializers para la app de pagos."""

from rest_framework import serializers
from django.core.exceptions import ValidationError
from apps.facturacion.models import Factura
from apps.clientes.models import Cliente
from .models import Pago, HistorialPago


class PagoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Pago."""
    
    # Campos adicionales para mostrar información relacionada
    factura_numero = serializers.CharField(source='factura.numero_factura', read_only=True)
    factura_total = serializers.DecimalField(source='factura.total', max_digits=10, decimal_places=2, read_only=True)
    cliente_nombre = serializers.CharField(source='pagado_por.nombre', read_only=True)
    validador_nombre = serializers.CharField(source='validado_por.username', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id', 'factura', 'factura_numero', 'factura_total',
            'tipo_pago', 'monto', 'numero_transaccion', 'observaciones',
            'estado', 'pagado_por', 'cliente_nombre', 'validado_por', 'validador_nombre',
            'fecha_pago', 'fecha_validacion'
        ]
        read_only_fields = [
            'id', 'estado', 'validado_por', 'fecha_pago', 'fecha_validacion',
            'factura_numero', 'factura_total', 'cliente_nombre', 'validador_nombre'
        ]
    
    def validate_factura(self, value):
        """Validar que la factura existe y puede ser pagada."""
        if not value:
            raise serializers.ValidationError("La factura es requerida")
        
        if value.estado == 'ANULADA':
            raise serializers.ValidationError("No se puede pagar una factura anulada")
        
        if value.estado == 'PAGADA':
            raise serializers.ValidationError("Esta factura ya está pagada")
        
        return value
    
    def validate_monto(self, value):
        """Validar que el monto sea válido."""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero")
        
        return value
    
    def validate(self, attrs):
        """Validaciones a nivel de objeto."""
        factura = attrs.get('factura')
        monto = attrs.get('monto')
        pagado_por = attrs.get('pagado_por')
        
        if factura and monto:
            # Validar que el monto no exceda el total de la factura
            if monto > factura.total:
                raise serializers.ValidationError(
                    f"El monto del pago (${monto}) no puede ser mayor "
                    f"al total de la factura (${factura.total})"
                )
        
        if factura and pagado_por:
            # Validar que el cliente que paga sea el mismo de la factura
            if pagado_por != factura.cliente:
                raise serializers.ValidationError(
                    "Solo el cliente de la factura puede realizar el pago"
                )
        
        return attrs


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear pagos (API de clientes)."""
    
    class Meta:
        model = Pago
        fields = [
            'factura', 'tipo_pago', 'monto', 'numero_transaccion', 'observaciones'
        ]
    
    def create(self, validated_data):
        """Crear un pago asignando automáticamente el cliente autenticado."""
        # El cliente se obtiene del contexto (usuario autenticado)
        request = self.context.get('request')
        if hasattr(request, 'user') and hasattr(request.user, 'id'):
            # Si es un usuario del sistema (rol cliente)
            try:
                cliente = Cliente.objects.get(email=request.user.email)
                validated_data['pagado_por'] = cliente
            except Cliente.DoesNotExist:
                raise serializers.ValidationError(
                    "No se encontró un cliente asociado con este usuario"
                )
        else:
            # Si es un cliente autenticado con token personalizado
            validated_data['pagado_por'] = request.user
        
        return super().create(validated_data)


class PagoDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para mostrar información completa del pago."""
    
    factura_info = serializers.SerializerMethodField()
    cliente_info = serializers.SerializerMethodField()
    validador_info = serializers.SerializerMethodField()
    historial = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = '__all__'
        extra_fields = ['factura_info', 'cliente_info', 'validador_info', 'historial']
    
    def get_factura_info(self, obj):
        """Información detallada de la factura."""
        return {
            'id': obj.factura.id,
            'numero_factura': obj.factura.numero_factura,
            'total': obj.factura.total,
            'estado': obj.factura.get_estado_display(),
            'fecha': obj.factura.fecha
        }
    
    def get_cliente_info(self, obj):
        """Información del cliente que pagó."""
        return {
            'id': obj.pagado_por.id,
            'nombre': obj.pagado_por.nombre,
            'email': obj.pagado_por.email
        }
    
    def get_validador_info(self, obj):
        """Información del usuario que validó (si existe)."""
        if obj.validado_por:
            return {
                'id': obj.validado_por.id,
                'username': obj.validado_por.username,
                'role': obj.validado_por.role
            }
        return None
    
    def get_historial(self, obj):
        """Historial de cambios del pago."""
        historial = obj.historial.all()[:5]  # Últimos 5 cambios
        return HistorialPagoSerializer(historial, many=True).data


class HistorialPagoSerializer(serializers.ModelSerializer):
    """Serializer para el historial de pagos."""
    
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    
    class Meta:
        model = HistorialPago
        fields = [
            'id', 'estado_anterior', 'estado_nuevo', 'usuario', 'usuario_nombre',
            'fecha_cambio', 'observaciones'
        ]
        read_only_fields = fields


class PagoValidacionSerializer(serializers.Serializer):
    """Serializer para validar (aprobar/rechazar) pagos."""
    
    accion = serializers.ChoiceField(choices=['aprobar', 'rechazar'], required=True)
    motivo = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Motivo del rechazo (requerido si la acción es rechazar)"
    )
    
    def validate(self, attrs):
        """Validar que se proporcione motivo para rechazos."""
        accion = attrs.get('accion')
        motivo = attrs.get('motivo')
        
        if accion == 'rechazar' and not motivo:
            raise serializers.ValidationError(
                "El motivo es requerido cuando se rechaza un pago"
            )
        
        return attrs


class PagoPendienteSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar pagos pendientes."""
    
    factura_numero = serializers.CharField(source='factura.numero_factura', read_only=True)
    factura_total = serializers.DecimalField(source='factura.total', max_digits=10, decimal_places=2, read_only=True)
    cliente_nombre = serializers.CharField(source='pagado_por.nombre', read_only=True)
    cliente_email = serializers.EmailField(source='pagado_por.email', read_only=True)
    dias_pendiente = serializers.SerializerMethodField()
    
    class Meta:
        model = Pago
        fields = [
            'id', 'factura', 'factura_numero', 'factura_total',
            'tipo_pago', 'monto', 'numero_transaccion',
            'cliente_nombre', 'cliente_email', 'fecha_pago', 'dias_pendiente'
        ]
    
    def get_dias_pendiente(self, obj):
        """Calcular días que lleva pendiente el pago."""
        from django.utils import timezone
        delta = timezone.now() - obj.fecha_pago
        return delta.days
