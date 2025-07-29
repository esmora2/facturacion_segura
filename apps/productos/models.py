
"""Modelos para la app de productos."""

from django.db import models


class Producto(models.Model):
    """Modelo para productos."""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Representación legible del producto."""
        return str(self.nombre)
