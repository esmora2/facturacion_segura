from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.facturacion.models import Factura
from apps.clientes.models import Cliente, Role

User = get_user_model()

class FacturaEditPermissionsUnitTestCase(TestCase):
    """
    Test unitario para verificar los métodos de permisos en el modelo Factura
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            role='Administrador'
        )
        
        self.ventas_user1 = User.objects.create_user(
            username='ventas1',
            password='ventas123',
            role='Ventas'
        )
        
        self.ventas_user2 = User.objects.create_user(
            username='ventas2',
            password='ventas456',
            role='Ventas'
        )
        
        # Crear datos de prueba
        self.role = Role.objects.create(name='Ventas')
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            email='cliente@test.com',
            telefono='123456789'
        )
        self.cliente.roles.add(self.role)
        
        # Crear factura en borrador por ventas1
        self.factura_borrador = Factura.objects.create(
            creador=self.ventas_user1,
            cliente=self.cliente,
            estado='BORRADOR'
        )
        
        # Crear factura emitida por ventas1
        self.factura_emitida = Factura.objects.create(
            creador=self.ventas_user1,
            cliente=self.cliente,
            estado='EMITIDA'
        )
    
    def test_creador_puede_editar_factura_borrador(self):
        """Test que el creador puede editar su factura en borrador"""
        result = self.factura_borrador.puede_editar_usuario(self.ventas_user1)
        self.assertTrue(result)
    
    def test_admin_puede_editar_factura_borrador(self):
        """Test que admin puede editar cualquier factura en borrador"""
        result = self.factura_borrador.puede_editar_usuario(self.admin_user)
        self.assertTrue(result)
    
    def test_otro_usuario_no_puede_editar_factura_borrador(self):
        """Test que otro usuario NO puede editar factura de otro en borrador"""
        result = self.factura_borrador.puede_editar_usuario(self.ventas_user2)
        self.assertFalse(result)
    
    def test_creador_no_puede_editar_factura_emitida(self):
        """Test que ni el creador puede editar factura emitida"""
        result = self.factura_emitida.puede_editar_usuario(self.ventas_user1)
        self.assertFalse(result)
    
    def test_admin_no_puede_editar_factura_emitida(self):
        """Test que ni admin puede editar factura emitida"""
        result = self.factura_emitida.puede_editar_usuario(self.admin_user)
        self.assertFalse(result)
    
    def test_superuser_puede_editar_factura_borrador(self):
        """Test que superuser puede editar factura en borrador"""
        superuser = User.objects.create_superuser(
            username='super',
            password='super123',
            email='super@test.com'
        )
        result = self.factura_borrador.puede_editar_usuario(superuser)
        self.assertTrue(result)
    
    def test_superuser_no_puede_editar_factura_emitida(self):
        """Test que ni superuser puede editar factura emitida"""
        superuser = User.objects.create_superuser(
            username='super',
            password='super123',
            email='super@test.com'
        )
        result = self.factura_emitida.puede_editar_usuario(superuser)
        self.assertFalse(result)

print("Tests creados para validar permisos de edición de facturas")
print("Ejecutar con: python3 manage.py test test_factura_edit_unit_permissions -v 2")
