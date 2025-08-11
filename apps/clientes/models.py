
"""Modelos para la app de clientes."""

from django.db import models


class Role(models.Model):
    """Modelo para roles de cliente."""
    name = models.CharField(
        max_length=20,
        choices=[
            ('Administrador', 'Administrador'),
            ('Secretario', 'Secretario'),
            ('Bodega', 'Bodega'),
            ('Ventas', 'Ventas'),
        ],
        unique=True
    )

    def __str__(self):
        """Representación legible del rol."""
        return str(self.name)


# NOTA: El modelo Cliente ha sido migrado al modelo User en apps/usuarios/models.py
# Los clientes ahora son usuarios con role='Cliente'
# Todos los datos de clientes han sido migrados exitosamente al modelo User
