"""Vistas de autenticación para clientes."""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Cliente
from .serializers import ClienteCreateSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def cliente_register(request):
    """
    Registro de nuevos clientes.
    Después del registro, el cliente puede usar /api/token/ para obtener su token.
    """
    serializer = ClienteCreateSerializer(data=request.data)
    if serializer.is_valid():
        try:
            cliente = serializer.save()
            
            return Response({
                'success': True,
                'message': 'Cliente registrado exitosamente. Use /api/token/ con su username y password para obtener el token de acceso.',
                'user_data': {
                    'id': cliente.id,
                    'username': cliente.username,
                    'email': cliente.email,
                    'nombre': cliente.nombre,
                    'telefono': cliente.telefono,
                    'role': cliente.role
                },
                'next_step': 'POST /api/token/ con {"username": "' + cliente.username + '", "password": "su_password"}'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error al registrar cliente: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cliente_me(request):
    """
    Obtener datos del cliente autenticado.
    Funciona con autenticación estándar de DRF (Token Authentication).
    """
    user = request.user
    
    # Verificar que el usuario autenticado sea un cliente
    if not hasattr(user, 'role') or user.role != 'Cliente':
        return Response({
            'error': 'Solo accesible para clientes'
        }, status=status.HTTP_403_FORBIDDEN)
    
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'nombre': user.nombre,
        'telefono': user.telefono,
        'role': user.role,
        'is_active': user.is_active,
        'date_joined': user.date_joined.isoformat() if user.date_joined else None
    })


# Remover cliente_login ya que usaremos /api/token/ estándar
