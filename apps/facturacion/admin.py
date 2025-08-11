
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
    list_display = ('id', 'numero_factura', 'creador', 'cliente', 'estado', 'total', 'fecha')
    list_filter = ('estado', 'anulada', 'fecha')
    search_fields = ('numero_factura', 'creador__username', 'cliente__nombre')
    inlines = [FacturaItemInline]
    readonly_fields = ('subtotal', 'iva', 'total', 'numero_factura')
