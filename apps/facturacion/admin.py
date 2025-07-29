
"""Configuración del admin para la app de facturación."""

from django.contrib import admin
from .models import Factura, FacturaItem


class FacturaItemInline(admin.TabularInline):
    """Inline para items de factura en el admin."""
    model = FacturaItem
    extra = 1


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    """Admin para el modelo Factura."""
    list_display = ('id', 'creador', 'fecha', 'anulada')
    list_filter = ('anulada', 'fecha')
    search_fields = ('creador__username',)
    inlines = [FacturaItemInline]
