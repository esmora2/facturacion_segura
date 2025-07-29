
"""Serializers para la app de facturación."""

from django.db import transaction
from rest_framework import serializers

from apps.clientes.models import Cliente
from .models import Factura, FacturaItem


class FacturaItemSerializer(serializers.ModelSerializer):
    """Serializer para el modelo FacturaItem."""
    class Meta:
        model = FacturaItem
        fields = ['id', 'producto', 'cantidad', 'factura']
        read_only_fields = ['id', 'factura']

    def validate(self, data):
        """Validar cantidad y stock del producto."""
        producto = data['producto']
        cantidad = data['cantidad']
        if cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que 0")
        if producto.stock < cantidad:
            error_msg = f"No hay suficiente stock para {producto.nombre}"
            raise serializers.ValidationError(error_msg)
        return data


class FacturaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Factura."""
    items = FacturaItemSerializer(many=True, required=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    iva = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Factura
        fields = ['id', 'creador', 'cliente', 'fecha', 'estado', 'numero_factura',
                  'anulada', 'subtotal', 'iva', 'total', 'items']
        read_only_fields = ['id', 'creador', 'fecha', 'numero_factura', 'anulada',
                            'subtotal', 'iva', 'total']

    def validate(self, attrs):
        """Validar que la factura tenga al menos un ítem y un cliente."""
        if not attrs.get('items'):
            raise serializers.ValidationError("Debe incluir al menos un ítem")
        if not attrs.get('cliente'):
            raise serializers.ValidationError("El cliente es obligatorio")
        return attrs

    def create(self, validated_data):
        """Crear una factura con transacciones seguras y disminuir stock automáticamente."""
        items_data = validated_data.pop('items')
        cliente = validated_data.pop('cliente')
        creator = self.context['request'].user
        validated_data.pop('creador', None)
        with transaction.atomic():
            for item_data in items_data:
                producto = item_data['producto']
                cantidad = item_data['cantidad']
                if cantidad > producto.stock:
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {producto.nombre}. "
                        f"Stock disponible: {producto.stock}, "
                        f"Cantidad solicitada: {cantidad}"
                    )
            factura = Factura.objects.create(creador=creator, cliente=cliente, **validated_data)
            for item_data in items_data:
                FacturaItem.objects.create(factura=factura, **item_data)
            factura.calcular_totales()
            factura.save()
            return factura

    def update(self, instance, validated_data):
        """Actualizar una factura solo si está en borrador, manejando stock y transacciones."""
        if not instance.puede_editar():
            raise serializers.ValidationError("No se puede editar una factura que ya ha sido emitida")
        items_data = validated_data.pop('items', None)
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if items_data is not None:
                for item_data in items_data:
                    producto = item_data['producto']
                    cantidad = item_data['cantidad']
                    stock_actual_usado = sum(
                        item.cantidad for item in instance.items.filter(producto=producto)
                    )
                    stock_disponible = producto.stock + stock_actual_usado
                    if cantidad > stock_disponible:
                        raise serializers.ValidationError(
                            f"Stock insuficiente para {producto.nombre}. "
                            f"Stock disponible: {stock_disponible}, "
                            f"Cantidad solicitada: {cantidad}"
                        )
                instance.items.all().delete()
                for item_data in items_data:
                    FacturaItem.objects.create(factura=instance, **item_data)
        return instance
