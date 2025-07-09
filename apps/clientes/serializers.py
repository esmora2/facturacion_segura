from rest_framework import serializers
from .models import Cliente, Role

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['name']

class ClienteSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True)

    class Meta:
        model = Cliente
        fields = '__all__'

    def create(self, validated_data):
        roles_data = validated_data.pop('roles')
        cliente = Cliente.objects.create(**validated_data)
        for role_data in roles_data:
            role, _ = Role.objects.get_or_create(name=role_data['name'])
            cliente.roles.add(role)
        return cliente

    def update(self, instance, validated_data):
        roles_data = validated_data.pop('roles')
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.email = validated_data.get('email', instance.email)
        instance.telefono = validated_data.get('telefono', instance.telefono)
        instance.activo = validated_data.get('activo', instance.activo)
        instance.save()
        instance.roles.clear()
        for role_data in roles_data:
            role, _ = Role.objects.get_or_create(name=role_data['name'])
            instance.roles.add(role)
        return instance