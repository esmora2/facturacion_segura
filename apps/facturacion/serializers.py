from rest_framework import serializers
from .models import Factura, FacturaItem
from apps.productos.models import Producto
from apps.clientes.models import Cliente

class FacturaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaItem
        fields = ['id', 'producto', 'cantidad', 'factura']
        read_only_fields = ['id', 'factura']

    def validate(self, data):
        producto = data['producto']
        cantidad = data['cantidad']
        if cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que 0")
        if producto.stock < cantidad:
            raise serializers.ValidationError(f"No hay suficiente stock para {producto.nombre}")
        return data

class FacturaSerializer(serializers.ModelSerializer):
    items = FacturaItemSerializer(many=True, required=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())

    class Meta:
        model = Factura
        fields = ['id', 'creador', 'cliente', 'fecha', 'anulada', 'items']
        read_only_fields = ['id', 'creador', 'fecha', 'anulada']

    def validate(self, attrs):
        if not attrs.get('items'):
            raise serializers.ValidationError("Debe incluir al menos un ítem")
        if not attrs.get('cliente'):
            raise serializers.ValidationError("El cliente es obligatorio")
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        cliente = validated_data.pop('cliente')
        creator = self.context['request'].user
        validated_data.pop('creador', None)  # Eliminar creador de validated_data para evitar duplicados
        factura = Factura.objects.create(creador=creator, cliente=cliente, **validated_data)
        for item_data in items_data:
            FacturaItem.objects.create(factura=factura, **item_data)
        return factura