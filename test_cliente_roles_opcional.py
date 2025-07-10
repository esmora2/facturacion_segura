#!/usr/bin/env python
"""
Test para verificar que el campo roles en Cliente es opcional.
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.clientes.models import Cliente, Role
from apps.clientes.serializers import ClienteSerializer

User = get_user_model()

class TestClienteRolesOpcional(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='Administrador'
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

    def test_crear_cliente_sin_roles(self):
        """Verificar que se puede crear un cliente sin especificar roles"""
        data = {
            "nombre": "Cliente Sin Roles",
            "email": "sinroles@test.com",
            "telefono": "123456789",
            "activo": True
        }
        
        response = self.client.post('/api/clientes/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Cliente Sin Roles')
        self.assertEqual(len(response.data['roles']), 0)
        
        # Verificar en base de datos
        cliente = Cliente.objects.get(email='sinroles@test.com')
        self.assertEqual(cliente.roles.count(), 0)

    def test_crear_cliente_con_roles_vacios(self):
        """Verificar que se puede crear un cliente con roles = []"""
        data = {
            "nombre": "Cliente Roles Vacios",
            "email": "rolesvaciosr@test.com",
            "telefono": "123456789",
            "activo": True,
            "roles": []
        }
        
        response = self.client.post('/api/clientes/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['roles']), 0)

    def test_crear_cliente_con_roles(self):
        """Verificar que aún se puede crear un cliente con roles especificados"""
        # Crear rol si no existe
        Role.objects.get_or_create(name='Administrador')
        
        data = {
            "nombre": "Cliente Con Roles",
            "email": "conroles@test.com",
            "telefono": "123456789",
            "activo": True,
            "roles": [{"name": "Administrador"}]
        }
        
        response = self.client.post('/api/clientes/', data, format='json')
        
        # Debug: mostrar error si falla
        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error response: {response.status_code}")
            print(f"Response data: {response.data}")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['roles']), 1)
        self.assertEqual(response.data['roles'][0]['name'], 'Administrador')

    def test_actualizar_cliente_sin_roles(self):
        """Verificar que se puede actualizar un cliente sin especificar roles"""
        # Crear cliente con roles
        Role.objects.get_or_create(name='Ventas')
        cliente = Cliente.objects.create(
            nombre="Cliente Original",
            email="original@test.com",
            telefono="123456789"
        )
        role = Role.objects.get(name='Ventas')
        cliente.roles.add(role)
        
        # Actualizar sin mencionar roles
        data = {
            "nombre": "Cliente Actualizado",
            "telefono": "987654321"
        }
        
        response = self.client.patch(f'/api/clientes/{cliente.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Cliente Actualizado')
        # Los roles deben mantenerse
        self.assertEqual(len(response.data['roles']), 1)

    def test_actualizar_cliente_limpiando_roles(self):
        """Verificar que se puede limpiar los roles de un cliente"""
        # Crear cliente con roles
        Role.objects.get_or_create(name='Secretario')
        cliente = Cliente.objects.create(
            nombre="Cliente Con Roles",
            email="conroles2@test.com",
            telefono="123456789"
        )
        role = Role.objects.get(name='Secretario')
        cliente.roles.add(role)
        
        # Actualizar limpiando roles
        data = {
            "nombre": "Cliente Sin Roles",
            "roles": []
        }
        
        response = self.client.patch(f'/api/clientes/{cliente.id}/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['roles']), 0)
        
        # Verificar en base de datos
        cliente.refresh_from_db()
        self.assertEqual(cliente.roles.count(), 0)

    def test_serializer_directo_sin_roles(self):
        """Test directo del serializer sin roles"""
        data = {
            "nombre": "Test Serializer",
            "email": "serializer@test.com",
            "telefono": "555-0123",
            "activo": True
        }
        
        serializer = ClienteSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        cliente = serializer.save()
        self.assertEqual(cliente.nombre, "Test Serializer")
        self.assertEqual(cliente.roles.count(), 0)

    def test_modelo_str_sin_roles(self):
        """Verificar que el método __str__ funciona correctamente sin roles"""
        cliente = Cliente.objects.create(
            nombre="Cliente Test",
            email="test@test.com"
        )
        
        # Sin roles, debe mostrar solo el nombre
        self.assertEqual(str(cliente), "Cliente Test")
        
        # Con roles, debe mostrar nombre y roles
        Role.objects.get_or_create(name='Bodega')
        role = Role.objects.get(name='Bodega')
        cliente.roles.add(role)
        
        self.assertEqual(str(cliente), "Cliente Test (Bodega)")


if __name__ == '__main__':
    # Ejecutar tests específicos
    import unittest
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestClienteRolesOpcional)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resultados
    if result.wasSuccessful():
        print("\n✅ Todos los tests de roles opcionales pasaron correctamente")
    else:
        print(f"\n❌ {len(result.failures)} test(s) fallaron")
        print(f"❌ {len(result.errors)} error(es) encontrados")
