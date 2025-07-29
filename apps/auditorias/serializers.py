
"""Serializers para la app de auditorías."""

from rest_framework import serializers
from .models import LogAuditoria


class LogAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo LogAuditoria."""
    usuario = serializers.StringRelatedField()  # Muestra el nombre del usuario

    class Meta:
        model = LogAuditoria
        fields = '__all__'
