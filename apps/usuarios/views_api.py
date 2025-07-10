from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model, authenticate
from .models import User
from .serializers import UserSerializer
from .permissions import AdminOnlyPermission
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Endpoint para obtener información del usuario autenticado"""
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_password(request):
    """
    Endpoint para validar la contraseña del usuario autenticado.
    Útil para operaciones críticas como eliminación permanente.
    
    Request Body:
    {
        "password": "contraseña_del_usuario"
    }
    
    Response:
    - 200: Contraseña válida
    - 400: Datos inválidos o contraseña incorrecta
    - 401: Usuario no autenticado
    """
    try:
        password = request.data.get('password')
        
        if not password:
            return Response({
                'error': 'La contraseña es requerida',
                'valid': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar la contraseña usando authenticate
        user = authenticate(
            username=request.user.username,
            password=password
        )
        
        if user is not None and user == request.user:
            # Log de seguridad (sin mostrar la contraseña)
            logger.info(f"Validación de contraseña exitosa para usuario: {request.user.username}")
            
            return Response({
                'message': 'Contraseña válida',
                'valid': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'role': getattr(request.user, 'role', None)
                }
            }, status=status.HTTP_200_OK)
        
        else:
            # Log de seguridad para intentos fallidos
            logger.warning(f"Intento de validación de contraseña fallido para usuario: {request.user.username}")
            
            return Response({
                'error': 'Contraseña incorrecta',
                'valid': False
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error en validación de contraseña: {str(e)}")
        return Response({
            'error': 'Error interno del servidor',
            'valid': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios.
    Solo accesible por Administradores.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, AdminOnlyPermission]

    def get_queryset(self):
        """Solo administradores pueden ver la lista de usuarios"""
        user = self.request.user
        if user.is_superuser or user.role == 'Administrador':
            return User.objects.all()
        return User.objects.none()

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Activar/desactivar usuario"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        status_text = "activado" if user.is_active else "desactivado"
        return Response({
            'status': f'Usuario {status_text} correctamente',
            'is_active': user.is_active
        })

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        """Cambiar rol de usuario"""
        user = self.get_object()
        new_role = request.data.get('role')
        
        if new_role not in [choice[0] for choice in User.ROLE_CHOICES]:
            return Response({
                'error': 'Rol no válido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.role = new_role
        user.save()
        
        return Response({
            'status': f'Rol cambiado a {new_role}',
            'role': user.role
        })

    @action(detail=False, methods=['get'])
    def roles(self, request):
        """Obtener lista de roles disponibles"""
        return Response({
            'roles': [{'value': choice[0], 'label': choice[1]} for choice in User.ROLE_CHOICES]
        })
