from django.db import models, transaction
from django.conf import settings
from apps.productos.models import Producto

class Factura(models.Model):
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    anulada = models.BooleanField(default=False)

    def __str__(self):
        return f"Factura #{self.id} - {'Anulada' if self.anulada else 'Activa'}"

    def anular(self):
        if not self.anulada:
            with transaction.atomic():
                for item in self.items.all():
                    producto = item.producto
                    producto.stock += item.cantidad
                    producto.save()
                self.anulada = True
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
            # Al crear, reducir stock
            producto = self.producto
            producto.stock -= self.cantidad
            producto.save()

    def delete(self, *args, **kwargs):
        # Opcional: al borrar el item de la factura se devuelve stock
        producto = self.producto
        producto.stock += self.cantidad
        producto.save()
        super().delete(*args, **kwargs)
