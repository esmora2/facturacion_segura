"""Modelos para la app de pagos."""

from decimal import Decimal
from django.db import models, transaction
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.facturacion.models import Factura


class Pago(models.Model):
    """Modelo para pagos de facturas."""
    
    TIPO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
    ]
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]
    
    # Información básica del pago
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE, 
        related_name='pagos'
    )
    tipo_pago = models.CharField(
        max_length=20, 
        choices=TIPO_PAGO_CHOICES
    )
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    numero_transaccion = models.CharField(
        max_length=100,
        help_text="Código o comprobante de la transacción"
    )
    observaciones = models.TextField(
        blank=True,
        help_text="Comentarios opcionales sobre el pago"
    )
    
    # Estado y seguimiento
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente'
    )
    
    # Usuarios involucrados
    pagado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pagos_realizados',
        limit_choices_to={'role': 'Cliente'},
        help_text="Cliente que realizó el pago"
    )
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_validados',
        help_text="Usuario que validó el pago"
    )
    
    # Fechas
    fecha_pago = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha cuando se registró el pago"
    )
    fecha_validacion = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha cuando se validó el pago"
    )
    
    class Meta:
        ordering = ['-fecha_pago']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
    
    def __str__(self):
        """Representación legible del pago."""
        return f"Pago #{self.id} - Factura #{self.factura.numero_factura or self.factura.id} - {self.get_estado_display()}"
    
    def clean(self):
        """Validaciones del modelo."""
        super().clean()
        
        # Validar que el monto sea positivo
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor que cero")
        
        # Validar que la factura no esté anulada
        if self.factura.estado == 'ANULADA':
            raise ValidationError("No se puede pagar una factura anulada")
        
        # Validar que la factura no esté ya pagada
        if self.factura.estado == 'PAGADA':
            raise ValidationError("Esta factura ya está pagada")
        
        # Validar que el monto no exceda el total de la factura
        if self.monto > self.factura.total:
            raise ValidationError(
                f"El monto del pago (${self.monto}) no puede ser mayor "
                f"al total de la factura (${self.factura.total})"
            )
        
        # Validar que el cliente que paga sea el mismo de la factura
        if self.pagado_por != self.factura.cliente:
            raise ValidationError(
                "Solo el cliente de la factura puede realizar el pago"
            )
    
    def save(self, *args, **kwargs):
        """Guardar el pago con validaciones."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def aprobar(self, usuario_validador):
        """Aprobar el pago y actualizar la factura."""
        if self.estado != 'pendiente':
            raise ValidationError("Solo se pueden aprobar pagos pendientes")
        
        with transaction.atomic():
            # Actualizar estado del pago
            self.estado = 'aprobado'
            self.validado_por = usuario_validador
            self.fecha_validacion = timezone.now()
            self.save()
            
            # Actualizar estado de la factura
            self.factura.estado = 'PAGADA'
            self.factura.save()
        
        return True
    
    def rechazar(self, usuario_validador, motivo_rechazo=None):
        """Rechazar el pago."""
        if self.estado != 'pendiente':
            raise ValidationError("Solo se pueden rechazar pagos pendientes")
        
        with transaction.atomic():
            # Actualizar estado del pago
            self.estado = 'rechazado'
            self.validado_por = usuario_validador
            self.fecha_validacion = timezone.now()
            
            # Agregar motivo del rechazo a observaciones
            if motivo_rechazo:
                if self.observaciones:
                    self.observaciones += f"\n\nMotivo del rechazo: {motivo_rechazo}"
                else:
                    self.observaciones = f"Motivo del rechazo: {motivo_rechazo}"
            
            self.save()
            
            # La factura mantiene su estado actual (EMITIDA)
        
        return True
    
    def puede_validar_usuario(self, user):
        """Verificar si un usuario puede validar este pago."""
        # Solo usuarios con rol 'Pagos' o 'Administrador' pueden validar
        return user.is_superuser or user.role in ['Administrador', 'Pagos']
    
    @property
    def esta_pendiente(self):
        """Verificar si el pago está pendiente."""
        return self.estado == 'pendiente'
    
    @property
    def esta_aprobado(self):
        """Verificar si el pago está aprobado."""
        return self.estado == 'aprobado'
    
    @property
    def esta_rechazado(self):
        """Verificar si el pago está rechazado."""
        return self.estado == 'rechazado'


class HistorialPago(models.Model):
    """Modelo para historial de cambios en pagos (auditoría)."""
    
    pago = models.ForeignKey(
        Pago,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    estado_anterior = models.CharField(max_length=20)
    estado_nuevo = models.CharField(max_length=20)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_cambio']
        verbose_name = 'Historial de Pago'
        verbose_name_plural = 'Historiales de Pagos'
    
    def __str__(self):
        """Representación legible del historial."""
        return f"Pago #{self.pago.id}: {self.estado_anterior} → {self.estado_nuevo}"
