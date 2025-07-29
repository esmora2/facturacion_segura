
"""Configuración del admin para la app de productos."""

from django.contrib import admin
from .models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Admin para el modelo Producto."""
    list_display = ('nombre', 'stock', 'precio')
    search_fields = ('nombre',)
    list_filter = ('stock',)
