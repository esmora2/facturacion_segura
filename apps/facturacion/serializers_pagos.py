"""Serializers para el sistema de pagos."""

from rest_framework import serializers
from .models_pagos import Pago
from .models import Factura
from apps.clientes.models import Cliente


class PagoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Pago."""
    
    factura_numero = serializers.CharField(source='factura.numero_factura', read_only=True)
    cliente_nombre = serializers.CharField(source='pagado_por.nombre', read_only=True)
    validador_nombre = serializers.CharField(source='validado_por.get_full_name', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'id',
            'factura',
            'factura_numero',
            'tipo_pago',
            'monto',
            'numero_transaccion',
            'observacion',
            'estado',
            'pagado_por',
            'cliente_nombre',
            'validado_por',
            'validador_nombre',
            'created_at',
            'validated_at',
        ]
        read_only_fields = [
            'id',
            'factura_numero',
            'cliente_nombre',
            'validador_nombre',
            'estado',
            'validado_por',
            'validated_at',
        ]

    def validate_factura(self, value):
        """Valida que la factura pueda recibir pagos."""
        # Estados válidos para pago: PENDIENTE y EMITIDA
        estados_validos = ['PENDIENTE', 'EMITIDA']
        
        if value.estado == 'PAGADA':
            raise serializers.ValidationError("La factura ya está pagada")
        if value.estado == 'ANULADA':
            raise serializers.ValidationError("No se puede pagar una factura anulada")
        if value.estado == 'BORRADOR':
            raise serializers.ValidationError("No se puede pagar una factura en borrador")
        if value.estado not in estados_validos:
            raise serializers.ValidationError(f"La factura debe estar en estado PENDIENTE o EMITIDA para poder recibir pagos")
        return value

    def validate_monto(self, value):
        """Valida que el monto sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value

    def validate(self, data):
        """Validaciones cruzadas."""
        # Verificar que el monto coincida con el total de la factura
        if 'factura' in data and 'monto' in data:
            if data['monto'] != data['factura'].total:
                raise serializers.ValidationError({
                    'monto': f"El monto debe coincidir con el total de la factura ({data['factura'].total})"
                })
        
        # Verificar que el cliente que paga sea el dueño de la factura
        if 'pagado_por' in data and 'factura' in data:
            if data['pagado_por'] != data['factura'].cliente:
                raise serializers.ValidationError({
                    'pagado_por': "Solo el cliente dueño de la factura puede realizar el pago"
                })
        
        return data


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear pagos desde API de cliente."""
    
    class Meta:
        model = Pago
        fields = [
            'factura',
            'tipo_pago',
            'monto',
            'numero_transaccion',
            'observacion',
        ]

    def validate_factura(self, value):
        """Valida que la factura pueda recibir pagos."""
        # Estados válidos para pago: PENDIENTE y EMITIDA
        estados_validos = ['PENDIENTE', 'EMITIDA']
        
        if value.estado == 'PAGADA':
            raise serializers.ValidationError("La factura ya está pagada")
        if value.estado == 'ANULADA':
            raise serializers.ValidationError("No se puede pagar una factura anulada")
        if value.estado == 'BORRADOR':
            raise serializers.ValidationError("No se puede pagar una factura en borrador")
        if value.estado not in estados_validos:
            raise serializers.ValidationError(f"La factura debe estar en estado PENDIENTE o EMITIDA para poder recibir pagos")
        return value

    def validate_monto(self, value):
        """Valida que el monto sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor a 0")
        return value

    def validate(self, data):
        """Validaciones cruzadas."""
        if 'factura' in data and 'monto' in data:
            if data['monto'] != data['factura'].total:
                raise serializers.ValidationError({
                    'monto': f"El monto debe coincidir con el total de la factura ({data['factura'].total})"
                })
        return data


class PagoValidacionSerializer(serializers.Serializer):
    """Serializer para validar (aprobar/rechazar) pagos."""
    
    accion = serializers.ChoiceField(choices=['aprobar', 'rechazar'])
    motivo = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Motivo del rechazo (opcional para aprobación)"
    )

    def validate(self, data):
        """Validar que se proporcione motivo para rechazos."""
        if data['accion'] == 'rechazar' and not data.get('motivo'):
            raise serializers.ValidationError({
                'motivo': 'El motivo es requerido para rechazar un pago'
            })
        return data


class FacturaClienteSerializer(serializers.ModelSerializer):
    """Serializer para mostrar facturas del cliente con información de pagos."""
    
    pagos_count = serializers.IntegerField(source='pagos.count', read_only=True)
    tiene_pagos_pendientes = serializers.SerializerMethodField()
    
    class Meta:
        model = Factura
        fields = [
            'id',
            'numero_factura',
            'fecha',
            'estado',
            'subtotal',
            'iva',
            'total',
            'pagos_count',
            'tiene_pagos_pendientes',
        ]
        read_only_fields = '__all__'
    
    def get_tiene_pagos_pendientes(self, obj):
        """Verifica si la factura tiene pagos pendientes."""
        return obj.pagos.filter(estado='pendiente').exists()
