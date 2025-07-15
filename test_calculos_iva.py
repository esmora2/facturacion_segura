from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.facturacion.models import Factura, FacturaItem
from apps.clientes.models import Cliente
from apps.productos.models import Producto
from decimal import Decimal

User = get_user_model()

class TestCalculosIVA(TestCase):
    """
    Tests para verificar que los cálculos del IVA del 15% funcionen correctamente.
    """
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario
        self.user = User.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='testpass123',
            role='Administrador'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            email='cliente@test.com',
            telefono='123456789'
        )
        
        # Crear productos
        self.producto1 = Producto.objects.create(
            nombre='Producto 1',
            precio=Decimal('100.00'),
            stock=50
        )
        
        self.producto2 = Producto.objects.create(
            nombre='Producto 2',
            precio=Decimal('50.00'),
            stock=30
        )
    
    def test_calcular_totales_factura_simple(self):
        """Test para calcular totales con un solo producto"""
        # Crear factura
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        # Agregar item
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto1,
            cantidad=2
        )
        
        # Recalcular totales
        totales = factura.calcular_totales()
        
        # Verificar cálculos
        expected_subtotal = Decimal('200.00')  # 2 * 100.00
        expected_iva = expected_subtotal * Decimal('0.15')  # 15% de IVA
        expected_total = expected_subtotal + expected_iva
        
        self.assertEqual(totales['subtotal'], expected_subtotal)
        self.assertEqual(totales['iva'], expected_iva)
        self.assertEqual(totales['total'], expected_total)
        
        # Verificar que se guardó en la base de datos
        factura.refresh_from_db()
        self.assertEqual(factura.subtotal, expected_subtotal)
        self.assertEqual(factura.iva, expected_iva)
        self.assertEqual(factura.total, expected_total)
    
    def test_calcular_totales_factura_multiple_productos(self):
        """Test para calcular totales con múltiples productos"""
        # Crear factura
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        # Agregar items
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto1,
            cantidad=1
        )
        
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto2,
            cantidad=3
        )
        
        # Recalcular totales
        totales = factura.calcular_totales()
        
        # Verificar cálculos
        expected_subtotal = Decimal('250.00')  # 1*100.00 + 3*50.00
        expected_iva = expected_subtotal * Decimal('0.15')  # 15% de IVA
        expected_total = expected_subtotal + expected_iva
        
        self.assertEqual(totales['subtotal'], expected_subtotal)
        self.assertEqual(totales['iva'], expected_iva)
        self.assertEqual(totales['total'], expected_total)
    
    def test_factura_sin_items(self):
        """Test para factura sin items"""
        # Crear factura sin items
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        # Recalcular totales
        totales = factura.calcular_totales()
        
        # Verificar que todo sea 0
        self.assertEqual(totales['subtotal'], Decimal('0'))
        self.assertEqual(totales['iva'], Decimal('0'))
        self.assertEqual(totales['total'], Decimal('0'))
    
    def test_actualizar_totales_al_agregar_item(self):
        """Test para verificar que se actualicen totales al agregar items"""
        # Crear factura
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        # Verificar que inicia en 0
        self.assertEqual(factura.subtotal, Decimal('0'))
        self.assertEqual(factura.iva, Decimal('0'))
        self.assertEqual(factura.total, Decimal('0'))
        
        # Agregar item
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto1,
            cantidad=1
        )
        
        # Verificar que se actualizaron los totales
        factura.refresh_from_db()
        expected_subtotal = Decimal('100.00')
        expected_iva = expected_subtotal * Decimal('0.15')
        expected_total = expected_subtotal + expected_iva
        
        self.assertEqual(factura.subtotal, expected_subtotal)
        self.assertEqual(factura.iva, expected_iva)
        self.assertEqual(factura.total, expected_total)
    
    def test_actualizar_totales_al_eliminar_item(self):
        """Test para verificar que se actualicen totales al eliminar items"""
        # Crear factura con items
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        item1 = FacturaItem.objects.create(
            factura=factura,
            producto=self.producto1,
            cantidad=1
        )
        
        item2 = FacturaItem.objects.create(
            factura=factura,
            producto=self.producto2,
            cantidad=2
        )
        
        # Verificar totales iniciales
        factura.refresh_from_db()
        initial_subtotal = factura.subtotal
        initial_iva = factura.iva
        initial_total = factura.total
        
        # Eliminar un item
        item1.delete()
        
        # Verificar que se actualizaron los totales
        factura.refresh_from_db()
        expected_subtotal = Decimal('100.00')  # Solo 2 * 50.00
        expected_iva = expected_subtotal * Decimal('0.15')
        expected_total = expected_subtotal + expected_iva
        
        self.assertEqual(factura.subtotal, expected_subtotal)
        self.assertEqual(factura.iva, expected_iva)
        self.assertEqual(factura.total, expected_total)
        
        # Verificar que el total disminuyó
        self.assertLess(factura.total, initial_total)
    
    def test_porcentaje_iva_correcto(self):
        """Test para verificar que el porcentaje de IVA sea exactamente 15%"""
        # Crear factura
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        # Agregar item
        FacturaItem.objects.create(
            factura=factura,
            producto=self.producto1,
            cantidad=1
        )
        
        # Verificar que el IVA es exactamente 15%
        factura.refresh_from_db()
        porcentaje_calculado = factura.iva / factura.subtotal
        self.assertEqual(porcentaje_calculado, Decimal('0.15'))
        
        # Verificar que la constante es correcta
        self.assertEqual(Factura.IVA_PORCENTAJE, Decimal('0.15'))
    
    def test_precision_decimal(self):
        """Test para verificar la precisión de los decimales"""
        # Crear factura
        factura = Factura.objects.create(
            creador=self.user,
            cliente=self.cliente
        )
        
        # Crear producto con precio que genere decimales
        producto_decimal = Producto.objects.create(
            nombre='Producto Decimal',
            precio=Decimal('33.33'),
            stock=10
        )
        
        # Agregar item
        FacturaItem.objects.create(
            factura=factura,
            producto=producto_decimal,
            cantidad=1
        )
        
        # Verificar que los decimales se manejen correctamente
        factura.refresh_from_db()
        self.assertEqual(factura.subtotal, Decimal('33.33'))
        
        # Calcular IVA esperado (redondeado a 2 decimales)
        iva_esperado = (Decimal('33.33') * Decimal('0.15')).quantize(Decimal('0.01'))
        total_esperado = factura.subtotal + iva_esperado
        
        self.assertEqual(factura.iva, iva_esperado)
        self.assertEqual(factura.total, total_esperado)
