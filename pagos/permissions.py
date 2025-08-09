"""Permisos personalizados para la app de pagos."""

from rest_framework.permissions import BasePermission


class PagoPermission(BasePermission):
    """
    Permisos para el módulo de pagos.
    - Administrador, Pagos: Acceso completo
    - Otros roles: Sin acceso
    """
    
    def has_permission(self, request, view):
        """Verificar permisos a nivel de vista."""
        if not request.user.is_authenticated:
            return False
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Solo usuarios con rol Administrador o Pagos
        return request.user.role in ['Administrador', 'Pagos']
    
    def has_object_permission(self, request, view, obj):
        """Verificar permisos a nivel de objeto."""
        # Usar los mismos permisos que has_permission
        return self.has_permission(request, view)


class ClientePagoPermission(BasePermission):
    """
    Permisos para que los clientes accedan a sus propios pagos.
    """
    
    def has_permission(self, request, view):
        """Verificar que esté autenticado (cliente o usuario)."""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Verificar que el cliente solo acceda a sus propios pagos."""
        # Si es un usuario del sistema con rol Administrador o Pagos
        if hasattr(request.user, 'role'):
            return request.user.role in ['Administrador', 'Pagos'] or request.user.is_superuser
        
        # Si es un cliente autenticado con token personalizado
        return obj.pagado_por == request.user


class ValidadorPagoPermission(BasePermission):
    """
    Permisos específicos para validar pagos.
    Solo Administradores y usuarios con rol Pagos.
    """
    
    def has_permission(self, request, view):
        """Verificar permisos para validar pagos."""
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in ['Administrador', 'Pagos']
