
"""Serializers para la app de clientes."""

from rest_framework import serializers
from .models import Cliente, Role


class ClienteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Cliente."""
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = '__all__'

    def get_roles(self, obj):
        """Serializar roles como lista de objetos con name."""
        return [{"name": role.name} for role in obj.roles.all()]

    def create(self, validated_data):
        """Crear un cliente y asignar roles si se proveen en la request."""
        request = self.context.get('request')
        roles_data = []
        if request and hasattr(request, 'data'):
            roles_data = request.data.get('roles', [])
        cliente = Cliente.objects.create(**validated_data)
        for role_data in roles_data:
            if isinstance(role_data, dict) and 'name' in role_data:
                role, _ = Role.objects.get_or_create(name=role_data['name'])
                cliente.roles.add(role)
        return cliente

    def update(self, instance, validated_data):
        """Actualizar un cliente y sus roles si se proveen en la request."""
        request = self.context.get('request')
        roles_data = None
        if request and hasattr(request, 'data') and 'roles' in request.data:
            roles_data = request.data.get('roles', [])
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.email = validated_data.get('email', instance.email)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.activo = validated_data.get('activo', instance.activo)
        instance.save()
        if roles_data is not None:
            instance.roles.clear()
            for role_data in roles_data:
                if isinstance(role_data, dict) and 'name' in role_data:
                    role, _ = Role.objects.get_or_create(name=role_data['name'])
                    instance.roles.add(role)
        return instance
