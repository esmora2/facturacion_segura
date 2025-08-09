
"""Modelos para la app de usuarios."""

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Modelo de usuario extendido con roles."""
    ADMINISTRADOR = 'Administrador'
    SECRETARIO = 'Secretario'
    BODEGA = 'Bodega'
    VENTAS = 'Ventas'
    PAGOS = 'Pagos'

    ROLE_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (SECRETARIO, 'Secretario'),
        (BODEGA, 'Bodega'),
        (VENTAS, 'Ventas'),
        (PAGOS, 'Pagos'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        """Representación legible del usuario."""
        return f'{self.username} ({self.role})'
