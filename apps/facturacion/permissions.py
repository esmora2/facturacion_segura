"""Permisos personalizados para el sistema de pagos."""

from rest_framework.permissions import BasePermission


class AllowClientTokenAuth(BasePermission):
    """
    Permiso que permite acceso sin autenticación Django para endpoints de clientes.
    Estos endpoints usan su propio sistema de autenticación con ClienteToken.
    """
    def has_permission(self, request, view):
        # Siempre permitir acceso - la autenticación se maneja en la vista
        return True


class PagosRolePermission(BasePermission):
    """
    Permiso que requiere rol 'pagos' o 'Administrador' para acceder a pagos.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_superuser or 
            request.user.role in ['Administrador', 'pagos']
        )
