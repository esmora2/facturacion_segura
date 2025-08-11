#!/usr/bin/env python3

import os
import sys
import django

# Configurar Django
sys.path.append('/home/erickxse/visual/woekspace2p/sistema-facturacion/facturacion_segura')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from apps.clientes.models import ClienteToken, Cliente

# Verificar tokens de clientes
print("Tokens de clientes existentes:")
print("=" * 50)
for token in ClienteToken.objects.all():
    print(f"Cliente: {token.cliente.nombre}")
    print(f"Email: {token.cliente.email}")
    print(f"Token: {token.key}")
    print(f"Activo: {token.cliente.activo}")
    print("-" * 30)

print("\nClientes registrados:")
print("=" * 50)
for cliente in Cliente.objects.all():
    print(f"ID: {cliente.id}")
    print(f"Username: {cliente.username}")
    print(f"Email: {cliente.email}")
    print(f"Nombre: {cliente.nombre}")
    print(f"Activo: {cliente.activo}")
    print(f"Role: {cliente.role}")
    print(f"Password: {'Sí' if cliente.password else 'No'}")
    print("-" * 30)
