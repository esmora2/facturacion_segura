#!/usr/bin/env python
"""
Test para validar la generación de números de factura secuenciales.
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

class TestFacturaNumeroGeneracion(TestCase):
    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
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
        
        self.client = APIClient()

    def crear_factura_con_items(self):
        """Crear una factura con items para pruebas"""
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente,
            estado='BORRADOR'
        )
        
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto,
            cantidad=2
        )
        
        return factura

    def test_numero_factura_secuencial(self):
        """Verificar que los números de factura sean secuenciales"""
        self.client.force_authenticate(user=self.user)
        
        # Crear y emitir primera factura
        factura1 = self.crear_factura_con_items()
        response1 = self.client.post(f'/api/facturas/{factura1.id}/emitir/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Crear y emitir segunda factura
        factura2 = self.crear_factura_con_items()
        response2 = self.client.post(f'/api/facturas/{factura2.id}/emitir/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Crear y emitir tercera factura
        factura3 = self.crear_factura_con_items()
        response3 = self.client.post(f'/api/facturas/{factura3.id}/emitir/')
        self.assertEqual(response3.status_code, status.HTTP_200_OK)
        
        # Verificar números secuenciales
        numero1 = response1.data['numero_factura']
        numero2 = response2.data['numero_factura']
        numero3 = response3.data['numero_factura']
        
        # Extraer números secuenciales
        seq1 = int(numero1.split('-')[1])
        seq2 = int(numero2.split('-')[1])
        seq3 = int(numero3.split('-')[1])
        
        # Verificar que sean consecutivos
        self.assertEqual(seq2, seq1 + 1)
        self.assertEqual(seq3, seq2 + 1)

    def test_formato_numero_factura(self):
        """Verificar que el formato del número sea correcto"""
        self.client.force_authenticate(user=self.user)
        
        factura = self.crear_factura_con_items()
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero = response.data['numero_factura']
        
        # Verificar formato FAC-XXXXXX
        self.assertTrue(numero.startswith('FAC-'))
        self.assertEqual(len(numero), 10)  # FAC- + 6 dígitos
        
        # Verificar que la parte numérica son 6 dígitos con padding
        parte_numerica = numero.split('-')[1]
        self.assertEqual(len(parte_numerica), 6)
        self.assertTrue(parte_numerica.isdigit())

    def test_numero_unico_por_factura(self):
        """Verificar que cada factura tenga un número único"""
        self.client.force_authenticate(user=self.user)
        
        numeros_generados = set()
        
        # Emitir múltiples facturas
        for i in range(5):
            factura = self.crear_factura_con_items()
            response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            numero = response.data['numero_factura']
            
            # Verificar que el número no se haya usado antes
            self.assertNotIn(numero, numeros_generados)
            numeros_generados.add(numero)

    def test_numero_persiste_en_base_datos(self):
        """Verificar que el número se guarde correctamente en la base de datos"""
        self.client.force_authenticate(user=self.user)
        
        factura = self.crear_factura_con_items()
        response = self.client.post(f'/api/facturas/{factura.id}/emitir/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        numero_response = response.data['numero_factura']
        
        # Recargar factura desde base de datos
        factura.refresh_from_db()
        
        # Verificar que coincidan
        self.assertEqual(factura.numero_factura, numero_response)
        self.assertEqual(factura.estado, 'EMITIDA')


if __name__ == '__main__':
    # Ejecutar tests específicos
    import unittest
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFacturaNumeroGeneracion)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resultados
    if result.wasSuccessful():
        print("\n✅ Todos los tests de generación de números pasaron correctamente")
    else:
        print(f"\n❌ {len(result.failures)} test(s) fallaron")
        print(f"❌ {len(result.errors)} error(es) encontrados")
