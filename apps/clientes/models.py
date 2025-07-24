import secrets
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=20, choices=[
        ('Administrador', 'Administrador'),
        ('Secretario', 'Secretario'),
        ('Bodega', 'Bodega'),
        ('Ventas', 'Ventas'),
    ], unique=True)

    def __str__(self):
        return self.name

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    activo = models.BooleanField(default=True)
    roles = models.ManyToManyField(Role, blank=True)

    def __str__(self):
        roles_list = [role.name for role in self.roles.all()]
        if roles_list:
            return f"{self.nombre} ({', '.join(roles_list)})"
        return self.nombre
    @property
    def is_authenticated(self):
        return True
    
class ClienteToken(models.Model):
    cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE, related_name='token')
    key = models.CharField(max_length=40, unique=True, default='')

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(20)  # 20 bytes = 40 caracteres hexadecimales
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Token for {self.cliente.nombre}'