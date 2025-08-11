#!/bin/bash

# Script para probar el sistema de autenticación de clientes
BASE_URL="http://127.0.0.1:8000"

echo "=== PRUEBAS DEL SISTEMA DE AUTENTICACIÓN DE CLIENTES ==="
echo ""

# Función para hacer peticiones POST
post_request() {
    local url=$1
    local data=$2
    local token=$3
    
    if [ -z "$token" ]; then
        curl -s -X POST "${BASE_URL}${url}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X POST "${BASE_URL}${url}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Token $token" \
            -d "$data"
    fi
}

# Función para hacer peticiones GET
get_request() {
    local url=$1
    local token=$2
    
    if [ -z "$token" ]; then
        curl -s "${BASE_URL}${url}"
    else
        curl -s "${BASE_URL}${url}" \
            -H "Authorization: Token $token"
    fi
}

echo "1. Registrando un nuevo cliente..."
REGISTRO_RESPONSE=$(post_request "/api/cliente/register/" '{
    "username": "cliente_test",
    "email": "cliente.test@email.com", 
    "password": "password123",
    "nombre": "Cliente de Prueba",
    "telefono": "555-1234"
}')

echo "Respuesta del registro:"
echo "$REGISTRO_RESPONSE" | python3 -m json.tool
echo ""

# Extraer el token del registro
CLIENT_TOKEN=$(echo "$REGISTRO_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)

if [ -z "$CLIENT_TOKEN" ]; then
    echo "⚠️  No se pudo obtener el token del registro. Probando login..."
    echo ""
    
    echo "2. Intentando login con el cliente..."
    LOGIN_RESPONSE=$(post_request "/api/cliente/login/" '{
        "email": "cliente.test@email.com",
        "password": "password123"
    }')
    
    echo "Respuesta del login:"
    echo "$LOGIN_RESPONSE" | python3 -m json.tool
    echo ""
    
    CLIENT_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
else
    echo "✅ Cliente registrado exitosamente!"
    echo "Token obtenido: $CLIENT_TOKEN"
    echo ""
fi

if [ -n "$CLIENT_TOKEN" ]; then
    echo "3. Probando endpoint /api/cliente/me/ con el token..."
    ME_RESPONSE=$(get_request "/api/cliente/me/" "$CLIENT_TOKEN")
    echo "Respuesta de /api/cliente/me/:"
    echo "$ME_RESPONSE" | python3 -m json.tool
    echo ""
    
    echo "4. Probando endpoint /api/facturas/cliente/ (facturas del cliente)..."
    FACTURAS_RESPONSE=$(get_request "/api/facturas/cliente/" "$CLIENT_TOKEN")
    echo "Respuesta de facturas del cliente:"
    echo "$FACTURAS_RESPONSE" | python3 -m json.tool
    echo ""
    
    echo "5. Probando endpoint /api/cliente/mis-pagos/ ..."
    PAGOS_RESPONSE=$(get_request "/api/cliente/mis-pagos/" "$CLIENT_TOKEN")
    echo "Respuesta de mis pagos:"
    echo "$PAGOS_RESPONSE" | python3 -m json.tool
    echo ""
    
else
    echo "❌ No se pudo obtener el token. Verifica la configuración."
fi

echo "=== FIN DE LAS PRUEBAS ==="
