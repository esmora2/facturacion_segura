#!/usr/bin/env python
"""
Test para validar permisos de emisión de facturas.
Solo el creador o un Administrador pueden emitir facturas.
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
from apps.facturacion.models import Factura, FacturaItem
from apps.clientes.models import Cliente
from apps.productos.models import Producto

User = get_user_model()

class TestFacturaEmitirPermissions(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuarios con diferentes roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='Administrador'
        )
        
        self.ventas_user = User.objects.create_user(
            username='ventas',
            email='ventas@test.com',
            password='testpass123',
            role='Ventas'
        )
        
        self.otro_ventas = User.objects.create_user(
            username='otro_ventas',
            email='otro_ventas@test.com',
            password='testpass123',
            role='Ventas'
        )
        
        # Crear cliente y producto
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            email='cliente@test.com',
            telefono='123456789'
        )
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio=100.00,
            stock=50
        )
        
        # Cliente API
        self.client = APIClient()

    def crear_factura_con_items(self, creador):
        """Crear una factura con items para pruebas"""
        factura = Factura.objects.create(
            creador=creador,
            cliente=self.cliente,
            estado='BORRADOR'
        )
        
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto,
            cantidad=2
        )
        
        return factura

    def test_creador_puede_emitir_factura(self):
        """El creador de la factura puede emitirla"""
        factura = self.crear_factura_con_items(self.ventas_user)
        
        self.client.force_authenticate(user=self.ventas_user)
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Factura emitida correctamente')
        self.assertIn('numero_factura', response.data)
        
        # Verificar que la factura cambió de estado
        factura.refresh_from_db()
        self.assertEqual(factura.estado, 'EMITIDA')
        self.assertIsNotNone(factura.numero_factura)

    def test_admin_puede_emitir_cualquier_factura(self):
        """Un administrador puede emitir cualquier factura"""
        factura = self.crear_factura_con_items(self.ventas_user)
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'Factura emitida correctamente')
        
        # Verificar que la factura cambió de estado
        factura.refresh_from_db()
        self.assertEqual(factura.estado, 'EMITIDA')

    def test_otro_usuario_no_puede_emitir_factura(self):
        """Un usuario que no creó la factura no puede emitirla"""
        factura = self.crear_factura_con_items(self.ventas_user)
        
        self.client.force_authenticate(user=self.otro_ventas)
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Solo el creador de la factura', response.data['error'])
        
        # Verificar que la factura NO cambió de estado
        factura.refresh_from_db()
        self.assertEqual(factura.estado, 'BORRADOR')

    def test_no_puede_emitir_factura_ya_emitida(self):
        """No se puede emitir una factura que ya está emitida"""
        factura = self.crear_factura_con_items(self.ventas_user)
        factura.emitir()  # Emitir la factura primero
        
        self.client.force_authenticate(user=self.ventas_user)
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Solo se pueden emitir facturas en estado borrador', response.data['error'])

    def test_no_puede_emitir_factura_sin_items(self):
        """No se puede emitir una factura sin items"""
        factura = Factura.objects.create(
            creador=self.ventas_user,
            cliente=self.cliente,
            estado='BORRADOR'
        )
        # No agregamos items
        
        self.client.force_authenticate(user=self.ventas_user)
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No se puede emitir una factura sin items', response.data['error'])

    def test_respuesta_completa_emision_exitosa(self):
        """Verificar que la respuesta de emisión incluye todos los campos esperados"""
        factura = self.crear_factura_con_items(self.ventas_user)
        
        self.client.force_authenticate(user=self.ventas_user)
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar campos de respuesta
        expected_fields = ['status', 'factura_id', 'numero_factura', 'estado', 'fecha_emision']
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        self.assertEqual(response.data['estado'], 'EMITIDA')
        self.assertEqual(response.data['factura_id'], factura.id)


if __name__ == '__main__':
    # Ejecutar tests específicos
    import unittest
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFacturaEmitirPermissions)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resultados
    if result.wasSuccessful():
        print("\n✅ Todos los tests de emisión de facturas pasaron correctamente")
    else:
        print(f"\n❌ {len(result.failures)} test(s) fallaron")
        print(f"❌ {len(result.errors)} error(es) encontrados")
