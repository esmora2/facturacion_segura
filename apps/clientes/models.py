from django.db import models

class Cliente(models.Model):
    ADMINISTRADOR = 'Administrador'
    SECRETARIO = 'Secretario'
    BODEGA = 'Bodega'
    VENTAS = 'Ventas'

    ROLE_CHOICES = [
        (ADMINISTRADOR, 'Administrador'),
        (SECRETARIO, 'Secretario'),
        (BODEGA, 'Bodega'),
        (VENTAS, 'Ventas'),
    ]

    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    roles = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.nombre} ({self.roles})"
