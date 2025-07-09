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
    roles = models.ManyToManyField(Role)

    def __str__(self):
        return f"{self.nombre} ({', '.join(role.name for role in self.roles.all())})"