from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class RoleBasedPermission(BasePermission):
    """
    Permiso personalizado para verificar roles específicos.
    Uso: permission_classes = [RoleBasedPermission]
    Requiere definir required_roles en la vista.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Los superusuarios tienen acceso total
        if request.user.is_superuser:
            return True

        # Verificar si la vista tiene roles requeridos definidos
        if hasattr(view, 'required_roles'):
            required_roles = view.required_roles
            if request.user.role in required_roles:
                return True
            else:
                raise PermissionDenied(
                    f"No tienes permiso para acceder a este recurso. "
                    f"Rol requerido: {', '.join(required_roles)}. "
                    f"Tu rol actual: {request.user.role or 'Sin rol asignado'}"
                )

        return False


class ClientePermission(BasePermission):
    """Permiso específico para el módulo de Clientes"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Acceso completo para Administradores y Secretarios
        if request.user.role in ['Administrador', 'Secretario']:
            return True

        # Acceso de solo lectura para personal de Ventas
        if request.user.role == 'Ventas':
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            else:
                raise PermissionDenied(
                    "El personal de Ventas solo puede consultar información de clientes (solo lectura)"
                )

        error_msg = (
            "Solo los Administradores, Secretarios y personal de Ventas "
            "(solo lectura) pueden acceder al módulo de Clientes"
        )
        raise PermissionDenied(error_msg)


"""Permissions for the usuarios app."""

from rest_framework.permissions import BasePermission

class ProductoPermission(BasePermission):
    """Permiso específico para el módulo de Productos"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Acceso completo para Administradores y personal de Bodega
        if request.user.role in ['Administrador', 'Bodega']:
            return True

        # Acceso de solo lectura para personal de Ventas
        if request.user.role == 'Ventas':
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return True
            else:
                error_msg = (
                    "El personal de Ventas solo puede consultar información "
                    "de productos (solo lectura)"
                )
                raise PermissionDenied(error_msg)

        error_msg = (
            "Solo los Administradores, personal de Bodega y personal de Ventas "
            "(solo lectura) pueden acceder al módulo de Productos"
        )
        raise PermissionDenied(error_msg)


class FacturaPermission(BasePermission):
    """Permiso específico para el módulo de Facturación"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        # Administradores y Ventas tienen acceso completo
        if request.user.role in ['Administrador', 'Ventas']:
            return True

        # Los clientes solo pueden acceder a view_pdf y download_pdf
        if request.user.role == 'Cliente' and view.action in ['view_pdf', 'download_pdf']:
            return True

        raise PermissionDenied(
            "Solo los Administradores y personal de Ventas pueden acceder al módulo de Facturación"
        )


class AdminOnlyPermission(BasePermission):
    """Permiso solo para Administradores"""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser or request.user.role == 'Administrador':
            return True

        raise PermissionDenied(
            "Solo los Administradores pueden realizar esta acción"
        )
