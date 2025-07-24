from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from .models import ClienteToken

class ClienteTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Token '):
            return None
        key = auth_header.split(' ')[1]
        try:
            token = ClienteToken.objects.get(key=key)
        except ClienteToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Token inválido')
        return (token.cliente, None)
