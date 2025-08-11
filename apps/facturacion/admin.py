
"""Configuración del admin para la app de facturación."""

from django.contrib import admin
from .models import Factura, FacturaItem
from .models_pagos import Pago


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


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Admin para el modelo Pago."""
    list_display = ('id', 'factura', 'pagado_por', 'tipo_pago', 'monto', 'estado', 'created_at')
    list_filter = ('estado', 'tipo_pago', 'created_at', 'validated_at')
    search_fields = ('factura__numero_factura', 'pagado_por__nombre', 'numero_transaccion')
    readonly_fields = ('created_at', 'validated_at')
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer algunos campos readonly después de la creación."""
        if obj:  # editing an existing object
            return self.readonly_fields + ('factura', 'pagado_por', 'monto')
        return self.readonly_fields
