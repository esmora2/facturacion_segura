from rest_framework import serializers
from .models import LogAuditoria

class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()  # Muestra el nombre del usuario

    class Meta:
        model = LogAuditoria
        fields = '__all__'
