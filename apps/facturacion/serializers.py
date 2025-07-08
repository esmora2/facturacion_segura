from rest_framework import serializers
from .models import Factura, FacturaItem

class FacturaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacturaItem
        fields = ['id', 'producto', 'cantidad', 'factura']
        read_only_fields = ['id', 'factura']


class FacturaSerializer(serializers.ModelSerializer):
    items = FacturaItemSerializer(many=True, required=True)

    class Meta:
        model = Factura
        fields = ['id', 'creador', 'fecha', 'anulada', 'items']
        read_only_fields = ['id', 'creador', 'fecha', 'anulada']


    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        
        # Remueve creador si vino en el input
        validated_data.pop('creador', None)
        
        creator = self.context['request'].user
        factura = Factura.objects.create(creador=creator, **validated_data)
        
        for item_data in items_data:
            FacturaItem.objects.create(factura=factura, **item_data)
        
        return factura




