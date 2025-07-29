
"""Serializers para la app de productos."""

from rest_framework import serializers
from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Producto."""
    class Meta:
        model = Producto
        fields = '__all__'
