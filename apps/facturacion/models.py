from django.db import models, transaction
from django.conf import settings
from apps.productos.models import Producto
from apps.clientes.models import Cliente

class Factura(models.Model):
    ESTADOS = [
        ('BORRADOR', 'Borrador'),
        ('EMITIDA', 'Emitida'),
        ('PAGADA', 'Pagada'),
        ('ANULADA', 'Anulada'),
    ]
    
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='BORRADOR')
    anulada = models.BooleanField(default=False)  # Mantener por compatibilidad
    numero_factura = models.CharField(max_length=50, unique=True, null=True, blank=True)

    def __str__(self):
        return f"Factura #{self.id} - {'Anulada' if self.anulada else 'Activa'}"

    def puede_editar(self):
        """Una factura solo puede editarse si está en estado BORRADOR"""
        return self.estado == 'BORRADOR'
    
    def puede_anular(self):
        """Una factura puede anularse si está EMITIDA o PAGADA"""
        return self.estado in ['EMITIDA', 'PAGADA']
    
    def emitir(self):
        """Cambiar estado a EMITIDA y generar número de factura"""
        if self.estado == 'BORRADOR':
            # Generar número de factura secuencial
            ultimo_numero = Factura.objects.filter(
                numero_factura__isnull=False
            ).count()
            self.numero_factura = f"FAC-{(ultimo_numero + 1):06d}"
            self.estado = 'EMITIDA'
            self.save()
            
    def marcar_pagada(self):
        """Marcar factura como pagada"""
        if self.estado == 'EMITIDA':
            self.estado = 'PAGADA'
            self.save()

    def anular(self):
        if self.puede_anular():
            with transaction.atomic():
                for item in self.items.all():
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()
                self.estado = 'ANULADA'
                self.anulada = True  # Por compatibilidad
                self.save()

    def puede_eliminar(self, user):
        if user.is_superuser:
            return True
        if self.creador == user:
            return True
        return False

class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.factura.anulada:
            producto = self.producto
            producto.stock -= self.cantidad
            producto.save()

    def delete(self, *args, **kwargs):
        producto = self.producto
        producto.stock += self.cantidad
        producto.save()
        super().delete(*args, **kwargs)