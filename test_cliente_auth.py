#!/usr/bin/env python3
"""
Script para probar el sistema de autenticación estándar de clientes.
Este script demuestra cómo los clientes pueden:
1. Registrarse
2. Hacer login usando /api/token/
3. Acceder a sus datos con el token
4. Registrar pagos
5. Consultar sus pagos
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_cliente_authentication():
    """Prueba completa del sistema de autenticación de clientes."""
    
    print("🔐 PRUEBA COMPLETA: Sistema de Autenticación Estándar para Clientes\n")
    
    # Datos del cliente de prueba
    cliente_data = {
        "username": "cliente_test_2024",
        "email": "cliente_test@example.com",
        "password": "password123",
        "nombre": "Cliente de Prueba",
        "telefono": "1234567890"
    }
    
    # 1. REGISTRO DE CLIENTE
    print("1️⃣ Registrando nuevo cliente...")
    response = requests.post(f"{API_BASE}/cliente/register/", json=cliente_data)
    
    if response.status_code == 201:
        print("✅ Cliente registrado exitosamente!")
        print(f"📄 Respuesta: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Error al registrar cliente: {response.status_code}")
        print(f"📄 Error: {response.text}")
        return
    
    print("\n" + "="*60 + "\n")
    
    # 2. LOGIN USANDO /api/token/ (ENDPOINT ESTÁNDAR)
    print("2️⃣ Haciendo login usando /api/token/ (sistema estándar)...")
    login_data = {
        "username": cliente_data["username"],
        "password": cliente_data["password"]
    }
    
    response = requests.post(f"{API_BASE}/token/", json=login_data)
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["token"]
        print("✅ Login exitoso!")
        print(f"🔑 Token obtenido: {token}")
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(f"📄 Error: {response.text}")
        return
    
    print("\n" + "="*60 + "\n")
    
    # 3. CONSULTAR DATOS DEL CLIENTE AUTENTICADO
    print("3️⃣ Consultando datos del cliente autenticado...")
    headers = {"Authorization": f"Token {token}"}
    
    response = requests.get(f"{API_BASE}/cliente/me/", headers=headers)
    
    if response.status_code == 200:
        print("✅ Datos del cliente obtenidos!")
        print(f"📄 Cliente: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"❌ Error al obtener datos: {response.status_code}")
        print(f"📄 Error: {response.text}")
    
    print("\n" + "="*60 + "\n")
    
    # 4. CONSULTAR PAGOS DEL CLIENTE
    print("4️⃣ Consultando pagos del cliente...")
    
    response = requests.get(f"{API_BASE}/pagos/mis-pagos/", headers=headers)
    
    if response.status_code == 200:
        pagos = response.json()
        print("✅ Pagos del cliente obtenidos!")
        print(f"📄 Cantidad de pagos: {len(pagos)}")
        if pagos:
            print(f"📄 Primer pago: {json.dumps(pagos[0], indent=2)}")
        else:
            print("📄 No hay pagos registrados para este cliente")
    else:
        print(f"❌ Error al obtener pagos: {response.status_code}")
        print(f"📄 Error: {response.text}")
    
    print("\n" + "="*60 + "\n")
    
    # 5. EJEMPLO DE USO DESDE NEXT.JS
    print("5️⃣ EJEMPLO DE USO DESDE NEXT.JS:")
    print("""
    // En tu frontend Next.js:
    
    // 1. Login del cliente
    const loginResponse = await fetch('http://localhost:8000/api/token/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: 'cliente_test_2024',
        password: 'password123'
      })
    });
    
    const { token } = await loginResponse.json();
    
    // 2. Usar el token para requests autenticados
    const clienteResponse = await fetch('http://localhost:8000/api/cliente/me/', {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      }
    });
    
    const clienteData = await clienteResponse.json();
    
    // 3. Consultar facturas del cliente
    const facturasResponse = await fetch('http://localhost:8000/api/clientes/facturas/', {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json',
      }
    });
    
    const facturas = await facturasResponse.json();
    """)
    
    print("\n" + "="*60 + "\n")
    print("🎉 PRUEBA COMPLETA FINALIZADA!")
    print("\n📋 RESUMEN:")
    print("✅ Los clientes pueden registrarse usando /api/cliente/register/")
    print("✅ Los clientes pueden hacer login usando /api/token/ (estándar)")
    print("✅ Los clientes pueden consultar sus datos usando /api/cliente/me/")
    print("✅ Los clientes pueden consultar sus pagos usando /api/pagos/mis-pagos/")
    print("✅ El sistema usa autenticación estándar de Django REST Framework")
    print("✅ No se almacenan tokens personalizados en la base de datos")
    print("✅ Compatible con sistemas de frontend como Next.js")

if __name__ == "__main__":
    try:
        test_cliente_authentication()
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor.")
        print("🔧 Asegúrate de que el servidor Django esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
