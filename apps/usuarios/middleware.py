from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()

class CheckUserIsActiveMiddleware:
    """
    Middleware para verificar que el usuario siga activo y no haya sido eliminado.
    Si el usuario está inactivo o fue eliminado, cierra la sesión automáticamente.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                # Verificar si el usuario aún existe en la base de datos
                current_user = User.objects.get(pk=request.user.pk)
                
                # Verificar si el usuario está inactivo
                if not current_user.is_active:
                    logout(request)
                    
                    # Si es una request de API, devolver JSON
                    if request.path.startswith('/api/'):
                        return JsonResponse({
                            'error': 'Su sesión ha finalizado, contacte con el administrador.',
                            'code': 'USER_INACTIVE'
                        }, status=401)
                    
                    # Para requests web, redirigir con mensaje
                    return redirect(f"{reverse('login')}?inactive=1")
                    
            except User.DoesNotExist:
                # El usuario fue eliminado de la base de datos
                logout(request)
                
                # Si es una request de API, devolver JSON
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'error': 'Su sesión ha finalizado, contacte con el administrador.',
                        'code': 'USER_DELETED'
                    }, status=401)
                
                # Para requests web, redirigir con mensaje
                return redirect(f"{reverse('login')}?deleted=1")
        
        response = self.get_response(request)
        return response


class RoleBasedAccessMiddleware:
    """
    Middleware para verificar que el usuario tenga el rol adecuado para acceder a diferentes módulos.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Mapeo de URLs a roles permitidos
        self.url_role_mapping = {
            '/clientes/': ['Administrador', 'Secretario'],
            '/api/clientes/': ['Administrador', 'Secretario'],
            '/productos/': ['Administrador', 'Bodega'],
            '/api/productos/': ['Administrador', 'Bodega'],
            '/facturacion/': ['Administrador', 'Ventas'],
            '/api/facturas/': ['Administrador', 'Ventas'],
        }

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # Verificar acceso basado en la URL
            for url_pattern, allowed_roles in self.url_role_mapping.items():
                if request.path.startswith(url_pattern):
                    if request.user.role not in allowed_roles:
                        # Si es una request de API, devolver JSON
                        if request.path.startswith('/api/'):
                            return JsonResponse({
                                'error': f'No tienes permiso para acceder a este módulo. Rol requerido: {", ".join(allowed_roles)}',
                                'code': 'INSUFFICIENT_ROLE'
                            }, status=403)
                        
                        # Para requests web, redirigir a home con mensaje
                        messages.error(request, f'No tienes permiso para acceder a este módulo. Rol requerido: {", ".join(allowed_roles)}')
                        return redirect('home')
        
        response = self.get_response(request)
        return response
