from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from apps.facturacion.models import Factura
from apps.clientes.models import Cliente, Role
from apps.productos.models import Producto

User = get_user_model()

class FacturaEditPermissionsTestCase(TestCase):
    """
    Test para verificar que solo el creador y administradores pueden editar facturas
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        
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
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.ventas1_token = Token.objects.create(user=self.ventas_user1)
        self.ventas2_token = Token.objects.create(user=self.ventas_user2)
        
        # Crear datos de prueba
        self.role = Role.objects.create(name='Ventas')
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            email='cliente@test.com',
            telefono='123456789'
        )
        self.cliente.roles.add(self.role)
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio=100.00,
            stock=50
        )
        
        # Crear factura por el usuario ventas1
        self.factura = Factura.objects.create(
            creador=self.ventas_user1,
            cliente=self.cliente,
            estado='BORRADOR'
        )
    
    def test_creador_puede_editar_su_factura(self):
        """Test que el creador puede editar su propia factura"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas1_token.key}')
        
        # Datos para actualización completa con campos requeridos
        data = {
            'cliente': self.cliente.id,
            'items': []  # Sin items para simplificar
        }
        
        response = self.client.patch(f'/api/facturas/{self.factura.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que se actualizó
        self.factura.refresh_from_db()
        self.assertEqual(self.factura.cliente.id, self.cliente.id)
    
    def test_admin_puede_editar_cualquier_factura(self):
        """Test que un administrador puede editar cualquier factura"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Datos para actualización
        data = {
            'estado': 'BORRADOR'
        }
        
        response = self.client.patch(f'/api/facturas/{self.factura.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_otro_usuario_no_puede_editar_factura(self):
        """Test que otro usuario de ventas NO puede editar factura de otro"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas2_token.key}')
        
        # Intentar editar factura creada por ventas1
        data = {
            'estado': 'BORRADOR'
        }
        
        response = self.client.patch(f'/api/facturas/{self.factura.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Solo el creador de la factura o un Administrador pueden editarla', 
                     str(response.data))
    
    def test_no_puede_editar_factura_emitida(self):
        """Test que nadie puede editar una factura ya emitida, ni siquiera el creador"""
        # Cambiar estado a emitida
        self.factura.estado = 'EMITIDA'
        self.factura.save()
        
        # Intentar editar como creador
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas1_token.key}')
        
        data = {
            'estado': 'EMITIDA'
        }
        
        response = self.client.patch(f'/api/facturas/{self.factura.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('No se puede editar una factura que ya ha sido emitida', 
                     str(response.data))
    
    def test_admin_tampoco_puede_editar_factura_emitida(self):
        """Test que ni siquiera el admin puede editar una factura emitida"""
        # Cambiar estado a emitida
        self.factura.estado = 'EMITIDA'
        self.factura.save()
        
        # Intentar editar como admin
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        data = {
            'estado': 'EMITIDA'
        }
        
        response = self.client.patch(f'/api/facturas/{self.factura.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('No se puede editar una factura que ya ha sido emitida', 
                     str(response.data))
    
    def test_put_update_tambien_validado(self):
        """Test que PUT también está validado igual que PATCH"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas2_token.key}')
        
        # Intentar editar con PUT
        data = {
            'cliente': self.cliente.id,
            'estado': 'BORRADOR'
        }
        
        response = self.client.put(f'/api/facturas/{self.factura.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Solo el creador de la factura o un Administrador pueden editarla', 
                     str(response.data))
