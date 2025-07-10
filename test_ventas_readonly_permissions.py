from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from apps.clientes.models import Cliente, Role
from apps.productos.models import Producto

User = get_user_model()

class VentasReadOnlyPermissionsTestCase(TestCase):
    """
    Test para verificar que el personal de Ventas tiene acceso de solo lectura
    a clientes y productos
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        
        # Crear usuarios con diferentes roles
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            role='Administrador'
        )
        
        self.ventas_user = User.objects.create_user(
            username='ventas',
            password='ventas123',
            role='Ventas'
        )
        
        self.secretario_user = User.objects.create_user(
            username='secretario',
            password='secretario123',
            role='Secretario'
        )
        
        self.bodega_user = User.objects.create_user(
            username='bodega',
            password='bodega123',
            role='Bodega'
        )
        
        # Crear tokens
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.ventas_token = Token.objects.create(user=self.ventas_user)
        self.secretario_token = Token.objects.create(user=self.secretario_user)
        self.bodega_token = Token.objects.create(user=self.bodega_user)
        
        # Crear datos de prueba
        self.role_cliente = Role.objects.create(name='Administrador')
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            email='cliente@test.com',
            telefono='123456789'
        )
        self.cliente.roles.add(self.role_cliente)
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio=100.00,
            stock=50
        )
    
    def test_ventas_can_read_clientes(self):
        """Test que personal de Ventas puede leer clientes"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        # GET /api/clientes/ - Debería funcionar
        response = self.client.get('/api/clientes/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Cliente Test')
        
        # GET /api/clientes/{id}/ - Debería funcionar
        response = self.client.get(f'/api/clientes/{self.cliente.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Cliente Test')
    
    def test_ventas_cannot_create_clientes(self):
        """Test que personal de Ventas NO puede crear clientes"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        data = {
            'nombre': 'Cliente Nuevo',
            'email': 'nuevo@test.com',
            'telefono': '987654321'
        }
        
        response = self.client.post('/api/clientes/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('solo puede consultar', str(response.data))
    
    def test_ventas_cannot_update_clientes(self):
        """Test que personal de Ventas NO puede actualizar clientes"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        data = {
            'nombre': 'Cliente Actualizado',
            'email': 'actualizado@test.com',
            'telefono': '111222333'
        }
        
        response = self.client.put(f'/api/clientes/{self.cliente.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('solo puede consultar', str(response.data))
    
    def test_ventas_cannot_delete_clientes(self):
        """Test que personal de Ventas NO puede eliminar clientes"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        response = self.client.delete(f'/api/clientes/{self.cliente.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('solo puede consultar', str(response.data))
    
    def test_ventas_can_read_productos(self):
        """Test que personal de Ventas puede leer productos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        # GET /api/productos/ - Debería funcionar
        response = self.client.get('/api/productos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nombre'], 'Producto Test')
        
        # GET /api/productos/{id}/ - Debería funcionar
        response = self.client.get(f'/api/productos/{self.producto.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Producto Test')
    
    def test_ventas_cannot_create_productos(self):
        """Test que personal de Ventas NO puede crear productos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        data = {
            'nombre': 'Producto Nuevo',
            'precio': 150.00,
            'stock': 25
        }
        
        response = self.client.post('/api/productos/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('solo puede consultar', str(response.data))
    
    def test_ventas_cannot_update_productos(self):
        """Test que personal de Ventas NO puede actualizar productos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        data = {
            'nombre': 'Producto Actualizado',
            'precio': 200.00,
            'stock': 75
        }
        
        response = self.client.put(f'/api/productos/{self.producto.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('solo puede consultar', str(response.data))
    
    def test_ventas_cannot_delete_productos(self):
        """Test que personal de Ventas NO puede eliminar productos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.ventas_token.key}')
        
        response = self.client.delete(f'/api/productos/{self.producto.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('solo puede consultar', str(response.data))
    
    def test_secretario_full_access_clientes(self):
        """Test que Secretario tiene acceso completo a clientes"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.secretario_token.key}')
        
        # Crear cliente
        data = {
            'nombre': 'Cliente Secretario',
            'email': 'secretario@test.com',
            'telefono': '555666777',
            'roles': [{'name': 'Administrador'}]
        }
        response = self.client.post('/api/clientes/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_bodega_full_access_productos(self):
        """Test que personal de Bodega tiene acceso completo a productos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.bodega_token.key}')
        
        # Crear producto
        data = {
            'nombre': 'Producto Bodega',
            'precio': 300.00,
            'stock': 100
        }
        response = self.client.post('/api/productos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_admin_full_access_all(self):
        """Test que Administrador tiene acceso completo a todo"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Crear cliente
        data_cliente = {
            'nombre': 'Cliente Admin',
            'email': 'admin@test.com',
            'telefono': '888999000',
            'roles': [{'name': 'Ventas'}]
        }
        response = self.client.post('/api/clientes/', data_cliente, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Crear producto
        data_producto = {
            'nombre': 'Producto Admin',
            'precio': 500.00,
            'stock': 200
        }
        response = self.client.post('/api/productos/', data_producto, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
