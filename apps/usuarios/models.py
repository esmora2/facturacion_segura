from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
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

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f'{self.username} ({self.role})'
