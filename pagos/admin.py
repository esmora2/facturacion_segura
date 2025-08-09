"""Configuración del admin para la app de pagos."""

from django.contrib import admin
from django.utils.html import format_html
from .models import Pago, HistorialPago


class HistorialPagoInline(admin.TabularInline):
    """Inline para mostrar historial de pagos."""
    model = HistorialPago
    extra = 0
    readonly_fields = ['estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio']
    can_delete = False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    """Admin para el modelo Pago."""
    
    list_display = [
        'id', 'factura_numero', 'cliente_nombre', 'monto', 
        'tipo_pago', 'estado_colored', 'fecha_pago', 'validado_por'
    ]
    list_filter = ['estado', 'tipo_pago', 'fecha_pago', 'fecha_validacion']
    search_fields = [
        'factura__numero_factura', 'pagado_por__nombre', 'pagado_por__email',
        'numero_transaccion'
    ]
    readonly_fields = ['fecha_pago', 'fecha_validacion']
    date_hierarchy = 'fecha_pago'
    ordering = ['-fecha_pago']
    inlines = [HistorialPagoInline]
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('factura', 'pagado_por', 'monto', 'tipo_pago', 'numero_transaccion')
        }),
        ('Estado y Validación', {
            'fields': ('estado', 'validado_por', 'fecha_pago', 'fecha_validacion')
        }),
        ('Observaciones', {
            'fields': ('observaciones',),
            'classes': ('collapse',)
        }),
    )
    
    def factura_numero(self, obj):
        """Mostrar número de factura."""
        return obj.factura.numero_factura or f"#{obj.factura.id}"
    factura_numero.short_description = 'Factura'
    factura_numero.admin_order_field = 'factura__numero_factura'
    
    def cliente_nombre(self, obj):
        """Mostrar nombre del cliente."""
        return obj.pagado_por.nombre
    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'pagado_por__nombre'
    
    def estado_colored(self, obj):
        """Mostrar estado con colores."""
        colors = {
            'pendiente': '#ffc107',  # amarillo
            'aprobado': '#28a745',   # verde
            'rechazado': '#dc3545'   # rojo
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_colored.short_description = 'Estado'
    estado_colored.admin_order_field = 'estado'
    
    def get_queryset(self, request):
        """Optimizar queryset."""
        return super().get_queryset(request).select_related(
            'factura', 'pagado_por', 'validado_por'
        )
    
    actions = ['aprobar_pagos_seleccionados', 'marcar_como_pendientes']
    
    def aprobar_pagos_seleccionados(self, request, queryset):
        """Acción para aprobar múltiples pagos."""
        pagos_pendientes = queryset.filter(estado='pendiente')
        count = 0
        
        for pago in pagos_pendientes:
            try:
                pago.aprobar(request.user)
                count += 1
            except Exception as e:
                self.message_user(
                    request, 
                    f"Error al aprobar pago #{pago.id}: {str(e)}", 
                    level='ERROR'
                )
        
        if count > 0:
            self.message_user(
                request, 
                f'{count} pago(s) aprobado(s) exitosamente.'
            )
    
    aprobar_pagos_seleccionados.short_description = "Aprobar pagos seleccionados"
    
    def marcar_como_pendientes(self, request, queryset):
        """Acción para marcar pagos como pendientes (solo para testing)."""
        if not request.user.is_superuser:
            self.message_user(
                request, 
                "Solo los superusuarios pueden realizar esta acción.", 
                level='ERROR'
            )
            return
        
        count = queryset.update(estado='pendiente', validado_por=None, fecha_validacion=None)
        self.message_user(
            request, 
            f'{count} pago(s) marcado(s) como pendiente.'
        )
    
    marcar_como_pendientes.short_description = "Marcar como pendientes (solo testing)"


@admin.register(HistorialPago)
class HistorialPagoAdmin(admin.ModelAdmin):
    """Admin para el modelo HistorialPago."""
    
    list_display = [
        'id', 'pago_id', 'estado_anterior', 'estado_nuevo', 
        'usuario', 'fecha_cambio'
    ]
    list_filter = ['estado_anterior', 'estado_nuevo', 'fecha_cambio']
    search_fields = ['pago__id', 'usuario__username']
    readonly_fields = [
        'pago', 'estado_anterior', 'estado_nuevo', 'usuario', 'fecha_cambio'
    ]
    date_hierarchy = 'fecha_cambio'
    ordering = ['-fecha_cambio']
    
    def pago_id(self, obj):
        """Mostrar ID del pago."""
        return f"Pago #{obj.pago.id}"
    pago_id.short_description = 'Pago'
    pago_id.admin_order_field = 'pago__id'
    
    def has_add_permission(self, request):
        """No permitir agregar historiales manualmente."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """No permitir eliminar historiales."""
        return False
    
    def get_queryset(self, request):
        """Optimizar queryset."""
        return super().get_queryset(request).select_related('pago', 'usuario')
