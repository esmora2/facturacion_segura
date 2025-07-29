
"""Configuración del admin para la app de usuarios."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    """Admin personalizado para el modelo User."""
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')

admin.site.register(User, CustomUserAdmin)
