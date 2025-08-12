"""Autenticación unificada para usuarios y clientes."""

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model

User = get_user_model()


class UnifiedTokenAuthentication(TokenAuthentication):
    """
    Autenticación que maneja usuarios del sistema con diferentes roles incluyendo clientes.
    """
    
    def authenticate_credentials(self, key):
        """
        Buscar el token y validar el usuario.
        """
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed('Token inválido.') from exc

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo o eliminado.')

        return (token.user, token)


class ClienteOrUserTokenAuthentication(TokenAuthentication):
    """
    Autenticación que funciona para todos los tipos de usuarios incluyendo clientes.
    """
    
    def authenticate_credentials(self, key):
        """Autenticar usuarios con cualquier rol."""
        model = self.get_model()
        
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed('Token inválido.') from exc
        
        user = token.user
        
        # Verificar que el usuario esté activo
        if not user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo.')
        
        return (user, token)
