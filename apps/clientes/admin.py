
"""Configuración del admin para la app de clientes."""

from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin para el modelo Role."""
    list_display = ['id', 'name']
    search_fields = ['name']


# NOTA: El modelo Cliente ha sido migrado al modelo User en apps/usuarios/admin.py
# Los clientes ahora se administran como usuarios con role='Cliente'
