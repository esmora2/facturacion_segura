#!/usr/bin/env python3
"""
Test para verificar los endpoints de visualización y descarga de PDF de facturas.
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

class TestFacturaPDFEndpoints(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
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
        
        # Crear factura con items
        self.factura = Factura.objects.create(
            creador=self.ventas_user,
            cliente=self.cliente,
            estado='EMITIDA'
        )
        
        FacturaItem.objects.create(
            factura=self.factura,
            producto=self.producto,
            cantidad=2
        )
        
        self.client = APIClient()

    def test_view_pdf_endpoint(self):
        """Test para endpoint de visualización de PDF"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/facturas/{self.factura.id}/view_pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline', response['Content-Disposition'])
        self.assertIn('factura_', response['Content-Disposition'])
        
        # Verificar que el contenido es un PDF (comienza con %PDF)
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_download_pdf_endpoint(self):
        """Test para endpoint de descarga de PDF"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/facturas/{self.factura.id}/download_pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('factura_', response['Content-Disposition'])
        
        # Verificar que el contenido es un PDF
        self.assertTrue(response.content.startswith(b'%PDF'))

    def test_pdf_con_numero_factura_fallback(self):
        """Test para verificar el fallback cuando no hay número de factura"""
        # Crear factura sin número oficial (borrador)
        factura_borrador = Factura.objects.create(
            creador=self.ventas_user,
            cliente=self.cliente,
            estado='BORRADOR'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/facturas/{factura_borrador.id}/view_pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe usar el ID como fallback
        self.assertIn(f'factura_{factura_borrador.id}.pdf', response['Content-Disposition'])

    def test_pdf_con_factura_emitida(self):
        """Test para factura emitida con número oficial"""
        # Emitir la factura para que tenga número oficial
        self.factura.numero_factura = "FAC-000001"
        self.factura.save()
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/facturas/{self.factura.id}/view_pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('FAC-000001', response['Content-Disposition'])

    def test_pdf_permisos_usuario(self):
        """Test para verificar permisos de usuario"""
        # Crear usuario sin permisos
        user_sin_permisos = User.objects.create_user(
            username='sinpermisos',
            email='sinpermisos@test.com',
            password='testpass123',
            role='Secretario'  # No tiene acceso a facturas
        )
        
        self.client.force_authenticate(user=user_sin_permisos)
        
        response = self.client.get(f'/api/facturas/{self.factura.id}/view_pdf/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_pdf_factura_sin_items(self):
        """Test para factura sin items"""
        # Crear factura sin items
        factura_sin_items = Factura.objects.create(
            creador=self.ventas_user,
            cliente=self.cliente,
            estado='BORRADOR'
        )
        
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(f'/api/facturas/{factura_sin_items.id}/view_pdf/')
        
        # Debe generar PDF aunque no tenga items
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_pdf_filename_correcto(self):
        """Test para verificar que el nombre del archivo es correcto"""
        self.factura.numero_factura = "FAC-000123"
        self.factura.save()
        
        self.client.force_authenticate(user=self.admin_user)
        
        # Test view_pdf
        response = self.client.get(f'/api/facturas/{self.factura.id}/view_pdf/')
        expected_filename = f"factura_{self.factura.numero_factura}.pdf"
        self.assertIn(expected_filename, response['Content-Disposition'])
        
        # Test download_pdf
        response = self.client.get(f'/api/facturas/{self.factura.id}/download_pdf/')
        self.assertIn(expected_filename, response['Content-Disposition'])

    def test_content_disposition_headers(self):
        """Test para verificar headers de Content-Disposition"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Test para visualización (inline)
        response = self.client.get(f'/api/facturas/{self.factura.id}/view_pdf/')
        self.assertIn('inline', response['Content-Disposition'])
        
        # Test para descarga (attachment)
        response = self.client.get(f'/api/facturas/{self.factura.id}/download_pdf/')
        self.assertIn('attachment', response['Content-Disposition'])


if __name__ == '__main__':
    # Ejecutar tests específicos
    import unittest
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFacturaPDFEndpoints)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resultados
    if result.wasSuccessful():
        print("\n✅ Todos los tests de PDF endpoints pasaron correctamente")
    else:
        print(f"\n❌ {len(result.failures)} test(s) fallaron")
        print(f"❌ {len(result.errors)} error(es) encontrados")
