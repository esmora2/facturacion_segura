#!/usr/bin/env python3
"""
Script de ejemplo para probar el endpoint /api/auth/validate-password/
"""

import urllib.request
import urllib.parse
import json
import sys

# Configuración
BASE_URL = "http://localhost:8000"
VALIDATE_PASSWORD_URL = f"{BASE_URL}/api/auth/validate-password/"
TOKEN_URL = f"{BASE_URL}/api/token/"

def make_request(url, data=None, headers=None, method='GET'):
    """Función auxiliar para hacer requests HTTP"""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    if data:
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            data = data.encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return {
                'status_code': response.status,
                'data': json.loads(response.read().decode('utf-8'))
            }
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode('utf-8'))
        except:
            error_data = {'error': str(e)}
        return {
            'status_code': e.code,
            'data': error_data
        }
    except Exception as e:
        return {
            'status_code': 500,
            'data': {'error': str(e)}
        }

def get_token(username, password):
    """Obtener token de autenticación"""
    response = make_request(TOKEN_URL, {
        'username': username,
        'password': password
    }, method='POST')
    
    if response['status_code'] == 200:
        token = response['data']['token']
        print(f"✅ Token obtenido: {token[:20]}...")
        return token
    else:
        print(f"Error obteniendo token: {response['status_code']}")
        print(response['data'])
        return None

def validate_password(token, password):
    """Validar contraseña del usuario autenticado"""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'password': password
    }
    
    response = make_request(VALIDATE_PASSWORD_URL, data, headers, method='POST')
    
    return response

def main():
    print("🔐 PRUEBA DEL ENDPOINT /api/auth/validate-password/")
    print("=" * 60)
    
    # Solicitar credenciales
    username = input("Username: ")
    password = input("Password: ")
    
    # Obtener token
    print("\n1. Obteniendo token de autenticación...")
    token = get_token(username, password)
    
    if not token:
        print("❌ No se pudo obtener el token")
        return
    
    # Validar contraseña correcta
    print("\n2. Validando contraseña correcta...")
    response = validate_password(token, password)
    
    print(f"Status Code: {response['status_code']}")
    print(f"Response: {json.dumps(response['data'], indent=2)}")
    
    if response['status_code'] == 200 and response['data'].get('valid'):
        print("✅ Contraseña válida")
    else:
        print("❌ Error en validación")
    
    # Validar contraseña incorrecta
    print("\n3. Validando contraseña incorrecta...")
    response = validate_password(token, "contraseña_incorrecta")
    
    print(f"Status Code: {response['status_code']}")
    print(f"Response: {json.dumps(response['data'], indent=2)}")
    
    if response['status_code'] == 400 and not response['data'].get('valid'):
        print("✅ Contraseña incorrecta detectada correctamente")
    else:
        print("❌ Error en validación de contraseña incorrecta")
    
    # Validar sin contraseña
    print("\n4. Validando sin contraseña...")
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    response = make_request(VALIDATE_PASSWORD_URL, {}, headers, method='POST')
    
    print(f"Status Code: {response['status_code']}")
    print(f"Response: {json.dumps(response['data'], indent=2)}")
    
    if response['status_code'] == 400:
        print("✅ Error de contraseña faltante detectado correctamente")
    else:
        print("❌ Error en validación sin contraseña")

if __name__ == "__main__":
    main()
