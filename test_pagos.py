#!/usr/bin/env python3
"""
Script de pruebas para el sistema de pagos
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_sistema_pagos():
    """Prueba completa del sistema de pagos"""
    
    print("🔧 === SISTEMA DE PAGOS - PRUEBAS ===")
    
    # 1. Login como admin para obtener token
    print("\n1. 🔐 Obteniendo token de administrador...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
    if response.status_code == 200:
        admin_token = response.json()["token"]
        print(f"✅ Token admin obtenido: {admin_token[:20]}...")
    else:
        print(f"❌ Error al obtener token admin: {response.status_code}")
        return
    
    # 2. Obtener lista de clientes
    print("\n2. 👥 Obteniendo lista de clientes...")
    
    headers = {"Authorization": f"Token {admin_token}"}
    response = requests.get(f"{BASE_URL}/api/clientes/", headers=headers)
    
    if response.status_code == 200:
        clientes = response.json()
        if clientes:
            cliente_id = clientes[0]["id"]
            print(f"✅ Cliente encontrado: ID {cliente_id} - {clientes[0]['nombre']}")
        else:
            print("❌ No hay clientes en el sistema")
            return
    else:
        print(f"❌ Error al obtener clientes: {response.status_code}")
        return
    
    # 3. Generar token para el cliente
    print("\n3. 🔑 Generando token para cliente...")
    
    response = requests.post(f"{BASE_URL}/api/clientes/{cliente_id}/generar-token/", headers=headers)
    
    if response.status_code == 200:
        cliente_token = response.json()["token"]
        print(f"✅ Token cliente generado: {cliente_token[:20]}...")
    else:
        print(f"❌ Error al generar token cliente: {response.status_code}")
        return
    
    # 4. Obtener facturas del cliente
    print("\n4. 📄 Obteniendo facturas del cliente...")
    
    client_headers = {"Authorization": f"Token {cliente_token}"}
    response = requests.get(f"{BASE_URL}/api/cliente/facturas/", headers=client_headers)
    
    if response.status_code == 200:
        facturas_data = response.json()
        facturas = facturas_data["facturas"]
        print(f"✅ Cliente: {facturas_data['cliente']}")
        print(f"✅ Facturas encontradas: {len(facturas)}")
        
        if facturas:
            factura_pendiente = None
            for factura in facturas:
                print(f"   - Factura {factura['numero_factura']} - Estado: {factura['estado']} - Total: ${factura['total']}")
                if factura['estado'] == 'PENDIENTE' and not factura['tiene_pagos_pendientes']:
                    factura_pendiente = factura
            
            if factura_pendiente:
                print(f"✅ Factura pendiente disponible para pago: {factura_pendiente['numero_factura']}")
                
                # 5. Registrar pago
                print("\n5. 💳 Registrando pago...")
                
                pago_data = {
                    "factura": factura_pendiente["id"],
                    "tipo_pago": "transferencia",
                    "monto": factura_pendiente["total"],
                    "numero_transaccion": "TEST-TXN-12345",
                    "observacion": "Pago de prueba del sistema"
                }
                
                response = requests.post(f"{BASE_URL}/api/cliente/pagar/", 
                                       json=pago_data, headers=client_headers)
                
                if response.status_code == 201:
                    pago_respuesta = response.json()
                    pago_id = pago_respuesta["pago"]["id"]
                    print(f"✅ Pago registrado exitosamente!")
                    print(f"   - ID del pago: {pago_id}")
                    print(f"   - Estado: {pago_respuesta['pago']['estado']}")
                    print(f"   - Mensaje: {pago_respuesta['mensaje']}")
                    
                    # 6. Ver pagos pendientes como admin
                    print("\n6. 👀 Viendo pagos pendientes (como admin)...")
                    
                    response = requests.get(f"{BASE_URL}/api/pagos/pendientes/", headers=headers)
                    
                    if response.status_code == 200:
                        pagos_data = response.json()
                        print(f"✅ Total pagos pendientes: {pagos_data['total_pendientes']}")
                        
                        if pagos_data["pagos"]:
                            pago_pendiente = pagos_data["pagos"][0]
                            print(f"   - Pago ID: {pago_pendiente['id']}")
                            print(f"   - Cliente: {pago_pendiente['cliente_nombre']}")
                            print(f"   - Monto: ${pago_pendiente['monto']}")
                            print(f"   - Tipo: {pago_pendiente['tipo_pago']}")
                            
                            # 7. Aprobar el pago
                            print("\n7. ✅ Aprobando pago...")
                            
                            aprobacion_data = {"accion": "aprobar"}
                            response = requests.post(f"{BASE_URL}/api/pagos/{pago_id}/validar/", 
                                                   json=aprobacion_data, headers=headers)
                            
                            if response.status_code == 200:
                                resultado = response.json()
                                print(f"✅ {resultado['mensaje']}")
                                print(f"   - Estado de factura: {resultado['factura_estado']}")
                                
                                # 8. Verificar facturas actualizadas
                                print("\n8. 🔄 Verificando facturas actualizadas...")
                                
                                response = requests.get(f"{BASE_URL}/api/cliente/facturas/", headers=client_headers)
                                
                                if response.status_code == 200:
                                    facturas_actualizadas = response.json()["facturas"]
                                    for factura in facturas_actualizadas:
                                        if factura["id"] == factura_pendiente["id"]:
                                            print(f"✅ Factura {factura['numero_factura']} actualizada:")
                                            print(f"   - Estado: {factura['estado']}")
                                            print(f"   - Pagos: {factura['pagos_count']}")
                                            break
                                else:
                                    print(f"❌ Error al verificar facturas: {response.status_code}")
                            else:
                                print(f"❌ Error al aprobar pago: {response.status_code}")
                        else:
                            print("❌ No se encontró el pago pendiente")
                    else:
                        print(f"❌ Error al obtener pagos pendientes: {response.status_code}")
                else:
                    print(f"❌ Error al registrar pago: {response.status_code}")
                    print(f"Respuesta: {response.text}")
            else:
                print("⚠️ No hay facturas pendientes para hacer pruebas de pago")
        else:
            print("⚠️ El cliente no tiene facturas")
    else:
        print(f"❌ Error al obtener facturas del cliente: {response.status_code}")
        print(f"Respuesta: {response.text}")
    
    print("\n🎉 === PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    test_sistema_pagos()
