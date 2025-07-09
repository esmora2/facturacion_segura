from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer para el modelo User"""
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 
                 'is_active', 'date_joined', 'password', 'confirm_password']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        # Validar contraseñas solo si se están actualizando
        if 'password' in attrs:
            password = attrs.get('password')
            confirm_password = attrs.get('confirm_password')
            
            if password != confirm_password:
                raise serializers.ValidationError("Las contraseñas no coinciden")
            
            # Validar fortaleza de la contraseña
            validate_password(password)
        
        return attrs

    def create(self, validated_data):
        # Remover confirm_password antes de crear
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user

    def update(self, instance, validated_data):
        # Remover confirm_password antes de actualizar
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        # Actualizar campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Actualizar contraseña si se proporcionó
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de usuarios"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'role', 'role_display', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']
