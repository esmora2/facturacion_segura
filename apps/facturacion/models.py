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
    
    def puede_editar_usuario(self, user):
        """
        Determina si un usuario puede editar esta factura.
        Solo pueden editar:
        - El usuario que la creó
        - Un usuario con rol Administrador
        - Superusuarios
        Y además debe estar en estado BORRADOR
        """
        if not self.puede_editar():
            return False
        
        if user.is_superuser:
            return True
        if user.role == 'Administrador':
            return True
        if self.creador == user:
            return True
        return False
    
    def puede_anular(self):
        """Una factura puede anularse si está EMITIDA o PAGADA"""
        return self.estado in ['EMITIDA', 'PAGADA']
    
    def puede_anular_usuario(self, user):
        """
        Determina si un usuario puede anular esta factura.
        Solo pueden anular:
        - El usuario que la creó
        - Un usuario con rol Administrador
        - Superusuarios
        Y además debe estar en estado EMITIDA o PAGADA
        """
        if not self.puede_anular():
            return False
        
        if user.is_superuser:
            return True
        if user.role == 'Administrador':
            return True
        if self.creador == user:
            return True
        return False
    
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
        """
        Anular una factura y restituir el stock de todos los productos.
        Usa transacciones atómicas para garantizar consistencia.
        """
        if self.puede_anular():
            with transaction.atomic():
                # Restituir stock de todos los items
                for item in self.items.all():
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()
                
                # Cambiar estado de la factura
                self.estado = 'ANULADA'
                self.anulada = True  # Por compatibilidad
                self.save()
                
                return True
        return False

    def puede_eliminar(self, user):
        """
        Determina si un usuario puede eliminar esta factura.
        Solo pueden eliminar:
        - El usuario que la creó
        - Un usuario con rol Administrador
        - Superusuarios
        """
        if user.is_superuser:
            return True
        if user.role == 'Administrador':
            return True
        if self.creador == user:
            return True
        return False
    
    def delete(self, *args, **kwargs):
        """
        Al eliminar una factura, restituir automáticamente el stock de todos los items.
        Solo se pueden eliminar facturas en estado BORRADOR.
        """
        with transaction.atomic():
            # Restituir stock de todos los items antes de eliminar
            for item in self.items.all():
                if not self.anulada and self.estado != 'ANULADA':
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()
            
            # Eliminar la factura (esto eliminará los items automáticamente por CASCADE)
            super().delete(*args, **kwargs)

class FacturaItem(models.Model):
    factura = models.ForeignKey(Factura, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"

    def save(self, *args, **kwargs):
        """
        Al crear un item de factura, disminuir el stock del producto.
        Usa transacciones para garantizar consistencia.
        """
        creating = self.pk is None
        
        if creating:
            # Verificar stock disponible antes de crear
            if self.cantidad > self.producto.stock:
                raise ValueError(f"Stock insuficiente para {self.producto.nombre}. "
                               f"Stock disponible: {self.producto.stock}, "
                               f"Cantidad solicitada: {self.cantidad}")
        
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            # Solo disminuir stock al crear y si la factura no está anulada
            if creating and not self.factura.anulada and self.factura.estado != 'ANULADA':
                producto = self.producto
                producto.stock -= self.cantidad
                if producto.stock < 0:
                    raise ValueError(f"Error: Stock negativo para {producto.nombre}")
                producto.save()

    def delete(self, *args, **kwargs):
        """
        Al eliminar un item de factura, restituir el stock del producto.
        Usa transacciones para garantizar consistencia.
        """
        with transaction.atomic():
            # Restituir stock antes de eliminar
            if not self.factura.anulada and self.factura.estado != 'ANULADA':
                producto = self.producto
                producto.stock += self.cantidad
                producto.save()
            super().delete(*args, **kwargs)