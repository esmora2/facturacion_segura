
"""Modelos para la app de clientes."""

import secrets
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
        return self.name

class Cliente(models.Model):
    """Modelo para clientes."""
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    roles = models.ManyToManyField(Role, blank=True)

    def __str__(self):
        """Representación legible del cliente."""
        roles_list = [role.name for role in self.roles.all()]
        if roles_list:
            return f"{self.nombre} ({', '.join(roles_list)})"
        return self.nombre

    @property
    def is_authenticated(self):
        """Compatibilidad para autenticación personalizada."""
        return True
class ClienteToken(models.Model):
    """Token único para cada cliente."""
    cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE, related_name='token')
    key = models.CharField(max_length=40, unique=True, default='')

    def save(self, *args, **kwargs):
        """Genera un token si no existe al guardar."""
        if not self.key:
            self.key = secrets.token_hex(20)  # 20 bytes = 40 caracteres hexadecimales
        super().save(*args, **kwargs)

    def __str__(self):
        """Representación legible del token de cliente."""
        return f'Token for {self.cliente.nombre}'
