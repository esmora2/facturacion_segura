from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
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


class PasswordValidationSerializer(serializers.Serializer):
    """
    Serializer para validar contraseñas en operaciones críticas
    """
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Contraseña del usuario para validación"
    )
    
    def validate_password(self, value):
        """
        Validar que la contraseña no esté vacía
        """
        if not value or value.strip() == '':
            raise serializers.ValidationError("La contraseña no puede estar vacía")
        return value
    
    def validate(self, attrs):
        """
        Validar la contraseña contra el usuario del contexto
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuario no autenticado")
        
        password = attrs.get('password')
        user = authenticate(
            username=request.user.username,
            password=password
        )
        
        if user is None or user != request.user:
            raise serializers.ValidationError("Contraseña incorrecta")
        
        return attrs
    
class GenerateUserTokenSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
