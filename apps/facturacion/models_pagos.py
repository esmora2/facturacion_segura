"""Modelos para el sistema de pagos."""

from django.db import models
from django.conf import settings
from .models import Factura
from apps.clientes.models import Cliente


class Pago(models.Model):
    """Modelo para registrar pagos de facturas."""
    
    TIPOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
    ]
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    # Campos principales
    factura = models.ForeignKey(
        Factura, 
        on_delete=models.CASCADE, 
        related_name='pagos'
    )
    tipo_pago = models.CharField(
        max_length=20, 
        choices=TIPOS_PAGO
    )
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    numero_transaccion = models.CharField(
        max_length=100,
        help_text="Código o comprobante de la transacción"
    )
    observacion = models.TextField(
        blank=True, 
        null=True,
        help_text="Comentarios adicionales sobre el pago"
    )
    estado = models.CharField(
        max_length=20, 
        choices=ESTADOS, 
        default='pendiente'
    )
    
    # Referencias a usuarios
    pagado_por = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pagos_realizados',
        help_text="Cliente que realizó el pago"
    )
    validado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pagos_validados',
        help_text="Usuario que aprobó o rechazó el pago"
    )
    
    # Campos de tiempo
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Fecha y hora de validación"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago {self.get_tipo_pago_display()} - {self.monto} - {self.get_estado_display()}"

    def puede_validar(self):
        """Verifica si el pago puede ser validado."""
        return self.estado == 'pendiente'

    def aprobar(self, validador):
        """Aprueba el pago y actualiza la factura."""
        if not self.puede_validar():
            raise ValueError("El pago no está en estado pendiente")
        
        from django.utils import timezone
        
        self.estado = 'aprobado'
        self.validado_por = validador
        self.validated_at = timezone.now()
        self.save()
        
        # Actualizar estado de la factura a pagada
        self.factura.marcar_pagada()

    def rechazar(self, validador, motivo=None):
        """Rechaza el pago."""
        if not self.puede_validar():
            raise ValueError("El pago no está en estado pendiente")
        
        from django.utils import timezone
        
        self.estado = 'rechazado'
        self.validado_por = validador
        self.validated_at = timezone.now()
        if motivo:
            self.observacion = f"{self.observacion or ''}\nMotivo rechazo: {motivo}".strip()
        self.save()

    def clean(self):
        """Validaciones del modelo."""
        from django.core.exceptions import ValidationError
        
        if self.monto <= 0:
            raise ValidationError("El monto debe ser mayor a 0")
        
        if self.factura.estado == 'PAGADA':
            raise ValidationError("No se puede registrar un pago para una factura ya pagada")
        
        if self.factura.estado == 'ANULADA':
            raise ValidationError("No se puede registrar un pago para una factura anulada")
        
        if self.monto != self.factura.total:
            raise ValidationError(
                f"El monto del pago ({self.monto}) debe coincidir con el total de la factura ({self.factura.total})"
            )
