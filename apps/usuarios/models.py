
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
    CLIENTE = 'Cliente'

    ROLE_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (SECRETARIO, 'Secretario'),
        (BODEGA, 'Bodega'),
        (VENTAS, 'Ventas'),
        (PAGOS, 'Pagos'),
        (CLIENTE, 'Cliente'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    
    # Campos específicos para clientes
    nombre = models.CharField(max_length=255, blank=True, null=True, help_text="Nombre completo del cliente")
    telefono = models.CharField(max_length=20, blank=True, null=True, help_text="Teléfono del cliente")

    def is_cliente(self):
        """Verifica si el usuario es un cliente."""
        return self.role == self.CLIENTE
    
    def is_admin(self):
        """Verifica si el usuario es administrador."""
        return self.role == self.ADMINISTRADOR

    def __str__(self):
        """Representación legible del usuario."""
        if self.is_cliente() and self.nombre:
            return f'{self.nombre} - {self.email}'
        return f'{self.username} ({self.role})'
