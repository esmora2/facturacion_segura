
"""Serializers para la app de clientes."""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role

User = get_user_model()


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para clientes (usuarios con role='Cliente')."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'nombre', 'telefono', 'is_active', 'role', 'date_joined']
        read_only_fields = ['role']  # El rol no debe ser modificable desde esta API

    def validate_role(self, value):
        """Asegurar que solo se permitan clientes."""
        if value != 'Cliente':
            raise serializers.ValidationError("Solo se permiten usuarios con rol Cliente")
        return value


class ClienteLoginSerializer(serializers.Serializer):
    """Serializer para login de clientes."""
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128)


class ClienteCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear clientes con password."""
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'nombre', 'telefono']
    
    def create(self, validated_data):
        """Crear cliente con password encriptado."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.role = 'Cliente'
        user.is_active = True
        user.save()
        return user
