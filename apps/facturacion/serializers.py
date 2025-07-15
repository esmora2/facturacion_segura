from rest_framework import serializers
from django.db import transaction
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
    
    # Campos calculados de solo lectura
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
        if not attrs.get('items'):
            raise serializers.ValidationError("Debe incluir al menos un ítem")
        if not attrs.get('cliente'):
            raise serializers.ValidationError("El cliente es obligatorio")
        return attrs

    def create(self, validated_data):
        """
        Crear una factura con transacciones seguras.
        Al crear, disminuir stock automáticamente.
        """
        items_data = validated_data.pop('items')
        cliente = validated_data.pop('cliente')
        creator = self.context['request'].user
        validated_data.pop('creador', None)
        
        with transaction.atomic():
            # Verificar stock disponible antes de crear la factura
            for item_data in items_data:
                producto = item_data['producto']
                cantidad = item_data['cantidad']
                if cantidad > producto.stock:
                    raise serializers.ValidationError(
                        f"Stock insuficiente para {producto.nombre}. "
                        f"Stock disponible: {producto.stock}, "
                        f"Cantidad solicitada: {cantidad}"
                    )
            
            # Crear la factura
            factura = Factura.objects.create(creador=creator, cliente=cliente, **validated_data)
            
            # Crear los items (el stock se reduce automáticamente en el modelo)
            for item_data in items_data:
                FacturaItem.objects.create(factura=factura, **item_data)
            
            # Recalcular totales después de crear todos los items
            factura.calcular_totales()
            factura.save()
            
            return factura

    def update(self, instance, validated_data):
        """
        Solo permitir actualización si está en borrador.
        Maneja transacciones seguras para el stock.
        """
        if not instance.puede_editar():
            raise serializers.ValidationError("No se puede editar una factura que ya ha sido emitida")
        
        items_data = validated_data.pop('items', None)
        
        with transaction.atomic():
            # Actualizar campos básicos
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            
            # Si se proporcionan items, actualizar la relación
            if items_data is not None:
                # Verificar stock disponible para los nuevos items
                for item_data in items_data:
                    producto = item_data['producto']
                    cantidad = item_data['cantidad']
                    
                    # Calcular stock disponible considerando que se liberará el actual
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
                
                # Restaurar stock de los items actuales (se hace automáticamente en delete())
                instance.items.all().delete()
                
                # Crear nuevos items (stock se reduce automáticamente en save())
                for item_data in items_data:
                    FacturaItem.objects.create(factura=instance, **item_data)
        
        return instance