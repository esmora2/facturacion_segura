"""Autenticación unificada para usuarios y clientes."""

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from apps.usuarios.models import User
from apps.clientes.models import Cliente


class UnifiedTokenAuthentication(TokenAuthentication):
    """
    Autenticación que maneja tanto usuarios del sistema como clientes.
    """
    
    def authenticate_credentials(self, key):
        """
        Buscar el token tanto en usuarios como en clientes.
        """
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo o eliminado.')

        # Verificar si es un cliente (tiene campo 'activo') o un usuario del sistema
        user = token.user
        
        # Si es un cliente, verificar el campo 'activo'
        if hasattr(user, 'activo') and not user.activo:
            raise exceptions.AuthenticationFailed('Cliente inactivo.')
        
        return (user, token)


class ClienteOrUserTokenAuthentication(TokenAuthentication):
    """
    Autenticación que funciona para ambos tipos de usuarios.
    """
    
    def authenticate_credentials(self, key):
        """Autenticar tanto usuarios como clientes."""
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido.')
        
        user = token.user
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo.')
        
        # Si es un cliente, verificar también el campo 'activo'
        if hasattr(user, 'activo') and not user.activo:
            raise exceptions.AuthenticationFailed('Cliente inactivo.')
        
        return (user, token)
