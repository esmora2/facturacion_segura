#!/usr/bin/env python3
"""
Test real de la API para verificar que roles es opcional.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.clientes.models import Cliente, Role

User = get_user_model()

def test_api_real():
    print("=== Test API Real - Roles Opcionales ===")
    
    # Crear o obtener usuario admin
    admin_user, created = User.objects.get_or_create(
        username='testadmin',
        defaults={
            'email': 'admin@test.com',
            'password': 'testpass123',
            'role': 'Administrador'
        }
    )
    if created:
        admin_user.set_password('testpass123')
        admin_user.save()
    
    client = APIClient()
    client.force_authenticate(user=admin_user)
    
    # Limpiar clientes existentes
    Cliente.objects.filter(email__in=[
        'sinroles@test.com',
        'conroles@test.com',
        'rolesvac@test.com'
    ]).delete()
    
    print("\n1. Crear cliente SIN roles:")
    data1 = {
        "nombre": "Cliente Sin Roles",
        "email": "sinroles@test.com",
        "telefono": "123456789",
        "activo": True
    }
    
    response1 = client.post('/api/clientes/', data1, format='json')
    print(f"Status: {response1.status_code}")
    if response1.status_code == 201:
        print(f"Cliente creado: {response1.data['nombre']}")
        print(f"Roles: {response1.data['roles']}")
    else:
        print(f"Error: {response1.data}")
    
    print("\n2. Crear cliente CON roles:")
    Role.objects.get_or_create(name='Ventas')
    data2 = {
        "nombre": "Cliente Con Roles",
        "email": "conroles@test.com",
        "telefono": "123456789",
        "activo": True,
        "roles": [{"name": "Ventas"}]
    }
    
    response2 = client.post('/api/clientes/', data2, format='json')
    print(f"Status: {response2.status_code}")
    if response2.status_code == 201:
        print(f"Cliente creado: {response2.data['nombre']}")
        print(f"Roles: {response2.data['roles']}")
    else:
        print(f"Error: {response2.data}")
    
    print("\n3. Crear cliente con roles VACÍOS:")
    data3 = {
        "nombre": "Cliente Roles Vacíos",
        "email": "rolesvac@test.com",
        "telefono": "123456789",
        "activo": True,
        "roles": []
    }
    
    response3 = client.post('/api/clientes/', data3, format='json')
    print(f"Status: {response3.status_code}")
    if response3.status_code == 201:
        print(f"Cliente creado: {response3.data['nombre']}")
        print(f"Roles: {response3.data['roles']}")
    else:
        print(f"Error: {response3.data}")
    
    print("\n4. Listar todos los clientes:")
    response4 = client.get('/api/clientes/')
    print(f"Status: {response4.status_code}")
    if response4.status_code == 200:
        for cliente in response4.data:
            print(f"- {cliente['nombre']}: {len(cliente['roles'])} roles")
    
    print("\n✅ Test completado!")

if __name__ == '__main__':
    test_api_real()
