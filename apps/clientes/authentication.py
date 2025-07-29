
"""Autenticación personalizada para clientes por token."""

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import ClienteToken


class ClienteTokenAuthentication(BaseAuthentication):
    """Autenticación por token para clientes."""
    def authenticate(self, request):
        """Autentica un cliente usando un token en el header Authorization."""
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return None
        key = auth_header.split(' ')[1]
        try:
            token = ClienteToken.objects.get(key=key)
        except ClienteToken.DoesNotExist as exc:
            raise exceptions.AuthenticationFailed('Token inválido') from exc
        return (token.cliente, None)
