
"""Configuración del admin para la app de clientes."""

from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Admin para el modelo Cliente."""
    list_display = ['id', 'nombre', 'email', 'telefono', 'get_roles', 'activo']

    def get_roles(self, obj):
        """Devuelve los roles del cliente como string."""
        return ", ".join([role.name for role in obj.roles.all()])
    get_roles.short_description = 'Roles'
