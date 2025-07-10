#!/usr/bin/env python3
"""
Script simple para debuggear el problema con roles en clientes.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from apps.clientes.serializers import ClienteSerializer
from apps.clientes.models import Role, Cliente

def test_serializer():
    print("=== Testing Cliente Serializer ===")
    
    # Limpiar datos existentes
    Cliente.objects.filter(email='test@test.com').delete()
    
    # Crear rol
    role, created = Role.objects.get_or_create(name='Administrador')
    print(f"Role created: {created}, Role: {role}")
    
    # Test 1: Sin roles
    print("\n1. Testing sin roles:")
    data1 = {
        'nombre': 'Cliente Sin Roles',
        'email': 'sinroles@test.com',
        'telefono': '123456789',
        'activo': True
    }
    
    serializer1 = ClienteSerializer(data=data1)
    print(f"Is valid: {serializer1.is_valid()}")
    if serializer1.is_valid():
        cliente1 = serializer1.save()
        print(f"Cliente creado: {cliente1}")
        print(f"Roles count: {cliente1.roles.count()}")
    else:
        print(f"Errors: {serializer1.errors}")
    
    # Test 2: Con roles vacíos
    print("\n2. Testing con roles vacíos:")
    data2 = {
        'nombre': 'Cliente Roles Vacíos',
        'email': 'rolesvac@test.com',
        'telefono': '123456789',
        'activo': True,
        'roles': []
    }
    
    serializer2 = ClienteSerializer(data=data2)
    print(f"Is valid: {serializer2.is_valid()}")
    if serializer2.is_valid():
        cliente2 = serializer2.save()
        print(f"Cliente creado: {cliente2}")
        print(f"Roles count: {cliente2.roles.count()}")
    else:
        print(f"Errors: {serializer2.errors}")
    
    # Test 3: Con roles
    print("\n3. Testing con roles:")
    data3 = {
        'nombre': 'Cliente Con Roles',
        'email': 'conroles@test.com',
        'telefono': '123456789',
        'activo': True,
        'roles': [{'name': 'Administrador'}]
    }
    
    serializer3 = ClienteSerializer(data=data3)
    print(f"Is valid: {serializer3.is_valid()}")
    if serializer3.is_valid():
        cliente3 = serializer3.save()
        print(f"Cliente creado: {cliente3}")
        print(f"Roles count: {cliente3.roles.count()}")
        print(f"Roles: {[r.name for r in cliente3.roles.all()]}")
    else:
        print(f"Errors: {serializer3.errors}")

if __name__ == '__main__':
    test_serializer()
