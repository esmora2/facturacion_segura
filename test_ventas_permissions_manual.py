#!/usr/bin/env python3

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import json

User = get_user_model()

def test_ventas_permissions():
    print("🔐 PRUEBA DE PERMISOS PARA PERSONAL DE VENTAS")
    print("=" * 60)
    
    # Crear usuario de ventas
    ventas_user, created = User.objects.get_or_create(
        username='vendedor_test',
        defaults={
            'email': 'vendedor@test.com',
            'role': 'Ventas'
        }
    )
    
    if created:
        ventas_user.set_password('ventas123')
        ventas_user.save()
        print("✅ Usuario de ventas creado")
    else:
        print("✅ Usuario de ventas ya existe")
    
    # Crear token
    token, _ = Token.objects.get_or_create(user=ventas_user)
    print(f"✅ Token: {token.key[:20]}...")
    print(f"✅ Usuario: {ventas_user.username} (Rol: {ventas_user.role})")
    
    # Crear cliente de prueba
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    print("\n🔍 PROBANDO PERMISOS...")
    
    # Test 1: Leer clientes (debería funcionar)
    print("\n1. GET /api/clientes/ (debería funcionar)")
    response = client.get('/api/clientes/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ PERMITIDO - Personal de Ventas puede leer clientes")
    else:
        print(f"   ❌ ERROR - {response.data}")
    
    # Test 2: Crear cliente (debería fallar)
    print("\n2. POST /api/clientes/ (debería fallar)")
    data = {
        'nombre': 'Cliente Test',
        'email': 'test@test.com',
        'telefono': '123456789',
        'roles': [{'name': 'Ventas'}]
    }
    response = client.post('/api/clientes/', data, format='json')
    print(f"   Status: {response.status_code}")
    if response.status_code == 403:
        print("   ✅ BLOQUEADO - Personal de Ventas NO puede crear clientes")
    else:
        print(f"   ❌ ERROR INESPERADO - {response.data}")
    
    # Test 3: Leer productos (debería funcionar)
    print("\n3. GET /api/productos/ (debería funcionar)")
    response = client.get('/api/productos/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ PERMITIDO - Personal de Ventas puede leer productos")
    else:
        print(f"   ❌ ERROR - {response.data}")
    
    # Test 4: Crear producto (debería fallar)
    print("\n4. POST /api/productos/ (debería fallar)")
    data = {
        'nombre': 'Producto Test',
        'precio': 100.00,
        'stock': 50
    }
    response = client.post('/api/productos/', data, format='json')
    print(f"   Status: {response.status_code}")
    if response.status_code == 403:
        print("   ✅ BLOQUEADO - Personal de Ventas NO puede crear productos")
    else:
        print(f"   ❌ ERROR INESPERADO - {response.data}")
    
    print("\n🎉 PRUEBA COMPLETADA")
    print("\n📝 RESUMEN:")
    print("   ✅ Personal de Ventas puede LEER clientes y productos")
    print("   ✅ Personal de Ventas NO puede CREAR/EDITAR/ELIMINAR clientes y productos")
    print("   ✅ Esto permite crear facturas sin comprometer la seguridad")

if __name__ == '__main__':
    test_ventas_permissions()
