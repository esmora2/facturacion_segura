#!/usr/bin/env python
"""Script para crear usuario de ventas."""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from apps.usuarios.models import User
from rest_framework.authtoken.models import Token

def crear_usuario_ventas():
    """Crear usuario con rol de ventas."""
    try:
        # Verificar si ya existe
        if User.objects.filter(username='usuario_ventas').exists():
            print("❌ El usuario 'usuario_ventas' ya existe")
            user = User.objects.get(username='usuario_ventas')
            print(f"👤 Usuario existente: {user.username} - Rol: {user.role}")
            return
        
        # Crear usuario de ventas
        user_ventas = User.objects.create_user(
            username='usuario_ventas',
            email='ventas@sistema.com',
            password='ventas123',
            first_name='Usuario',
            last_name='Ventas',
            role='Ventas'
        )
        
        # Crear token para el usuario
        token, created = Token.objects.get_or_create(user=user_ventas)
        
        print("✅ Usuario de ventas creado exitosamente:")
        print(f"👤 Username: {user_ventas.username}")
        print(f"📧 Email: {user_ventas.email}")
        print(f"🎯 Rol: {user_ventas.role}")
        print(f"🔑 Token: {token.key}")
        print(f"🔒 Contraseña: ventas123")
        
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")

if __name__ == "__main__":
    crear_usuario_ventas()
