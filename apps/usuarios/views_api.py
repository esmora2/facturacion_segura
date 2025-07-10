from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import User
from .serializers import UserSerializer
from .permissions import AdminOnlyPermission

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Endpoint para obtener información del usuario autenticado"""
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)


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
