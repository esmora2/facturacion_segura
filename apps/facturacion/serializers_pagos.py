"""Serializers para el sistema de pagos."""

from rest_framework import serializers
from pagos.models import Pago
from .models import Factura
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class PagoSerializer(serializers.ModelSerializer):
    """Serializer para mostrar datos de pagos."""
    factura_numero = serializers.CharField(source='factura.numero', read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    validador_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Pago
        fields = '__all__'
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
            raise serializers.ValidationError("La factura debe estar en estado PENDIENTE o EMITIDA para poder recibir pagos")
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
                    'monto': "El monto debe coincidir con el total de la factura"
                })

        # Verificar que la factura no tenga pagos pendientes
        if 'factura' in data:
            pagos_pendientes = Pago.objects.filter(
                factura=data['factura'],
                estado='PENDIENTE'
            ).exclude(pk=self.instance.pk if self.instance else None)

            if pagos_pendientes.exists():
                raise serializers.ValidationError({
                    'factura': "La factura ya tiene pagos pendientes de validación"
                })

        return data

    def get_cliente_nombre(self, obj):
        """Obtiene el nombre del cliente desde la factura."""
        if obj.factura and obj.factura.cliente:
            return f"{obj.factura.cliente.nombre} {obj.factura.cliente.apellido or ''}".strip()
        return None

    def get_validador_nombre(self, obj):
        """Obtiene el nombre del validador."""
        if obj.validado_por:
            return f"{obj.validado_por.first_name} {obj.validado_por.last_name}".strip()
        return None

    def create(self, validated_data):
        """Crear un nuevo pago."""
        validated_data['estado'] = 'PENDIENTE'
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Actualizar pago existente."""
        # Solo permitir actualizar ciertos campos si el pago está pendiente
        if instance.estado != 'PENDIENTE':
            validated_data.pop('factura', None)
            validated_data.pop('monto', None)
            validated_data.pop('metodo_pago', None)

        return super().update(instance, validated_data)


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
            raise serializers.ValidationError("La factura debe estar en estado PENDIENTE o EMITIDA para poder recibir pagos")
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
                    'monto': "El monto debe coincidir con el total de la factura"
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
