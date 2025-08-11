
"""Modelos para la app de clientes."""

from django.db import models
from django.contrib.auth.models import AbstractUser


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


class Cliente(AbstractUser):
    """Modelo para clientes que hereda de AbstractUser para usar autenticación estándar."""
    
    # Campos específicos de cliente
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    roles = models.ManyToManyField(Role, blank=True)
    
    # Campo de rol para compatibilidad con el sistema de usuarios
    role = models.CharField(max_length=20, default='Cliente')
    
    # Usar username como campo principal de login
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre']
    
    # Evitar conflictos con el modelo User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='cliente_set',
        related_query_name='cliente',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='cliente_set',
        related_query_name='cliente',
    )
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        """Representación legible del cliente."""
        roles_list = [role.name for role in self.roles.all()]
        if roles_list:
            return f"{self.nombre} ({', '.join(roles_list)})"
        return f"{self.nombre} - {self.email}"

    def save(self, *args, **kwargs):
        """Asegurar que el rol siempre sea 'Cliente' al guardar."""
        self.role = 'Cliente'
        # Usar is_active en lugar de activo para compatibilidad
        self.is_active = self.activo
        super().save(*args, **kwargs)


# ClienteToken eliminado - se usa el sistema estándar de tokens de Django REST Framework
