from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.urls import reverse

User = get_user_model()

class ValidatePasswordTestCase(TestCase):
    """
    Test cases para el endpoint de validación de contraseña
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            role='Ventas'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.url = '/api/auth/validate-password/'
    
    def test_validate_password_success(self):
        """Test validación exitosa de contraseña"""
        data = {'password': 'testpassword123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['message'], 'Contraseña válida')
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['role'], 'Ventas')
    
    def test_validate_password_incorrect(self):
        """Test validación con contraseña incorrecta"""
        data = {'password': 'wrongpassword'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])
        self.assertEqual(response.data['error'], 'Contraseña incorrecta')
    
    def test_validate_password_empty(self):
        """Test validación con contraseña vacía"""
        data = {'password': ''}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])
        self.assertEqual(response.data['error'], 'La contraseña es requerida')
    
    def test_validate_password_missing(self):
        """Test validación sin enviar contraseña"""
        data = {}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['valid'])
        self.assertEqual(response.data['error'], 'La contraseña es requerida')
    
    def test_validate_password_no_auth(self):
        """Test validación sin autenticación"""
        self.client.credentials()  # Remover token
        data = {'password': 'testpassword123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_validate_password_invalid_token(self):
        """Test validación con token inválido"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token')
        data = {'password': 'testpassword123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_validate_password_get_method_not_allowed(self):
        """Test que solo se permita método POST"""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_validate_password_with_admin_user(self):
        """Test validación con usuario administrador"""
        admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpassword123',
            role='Administrador'
        )
        admin_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {admin_token.key}')
        
        data = {'password': 'adminpassword123'}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valid'])
        self.assertEqual(response.data['user']['role'], 'Administrador')
