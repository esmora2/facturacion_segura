#!/bin/bash

# Script para probar el endpoint /api/auth/validate-password/
# Sistema de Facturación Segura

# Configuración
API_BASE_URL="http://localhost:8000"
USERNAME="your_username"
PASSWORD="your_password"

echo "🔐 Probando endpoint de validación de contraseña"
echo "================================================"

# Paso 1: Obtener token de autenticación
echo "1️⃣ Obteniendo token de autenticación..."
TOKEN_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" \
  "$API_BASE_URL/api/token/")

# Extraer token de la respuesta
TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ Error al obtener token. Respuesta:"
    echo "$TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Token obtenido: ${TOKEN:0:20}..."

# Paso 2: Probar validación con contraseña correcta
echo ""
echo "2️⃣ Probando validación con contraseña correcta..."
VALID_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d "{\"password\":\"$PASSWORD\"}" \
  "$API_BASE_URL/api/auth/validate-password/")

echo "✅ Respuesta con contraseña correcta:"
echo "$VALID_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$VALID_RESPONSE"

# Paso 3: Probar validación con contraseña incorrecta
echo ""
echo "3️⃣ Probando validación con contraseña incorrecta..."
INVALID_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d "{\"password\":\"wrong_password\"}" \
  "$API_BASE_URL/api/auth/validate-password/")

echo "❌ Respuesta con contraseña incorrecta:"
echo "$INVALID_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$INVALID_RESPONSE"

# Paso 4: Probar validación sin contraseña
echo ""
echo "4️⃣ Probando validación sin contraseña..."
EMPTY_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Token $TOKEN" \
  -d "{}" \
  "$API_BASE_URL/api/auth/validate-password/")

echo "❌ Respuesta sin contraseña:"
echo "$EMPTY_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$EMPTY_RESPONSE"

# Paso 5: Probar sin autenticación
echo ""
echo "5️⃣ Probando sin token de autenticación..."
NO_AUTH_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"$PASSWORD\"}" \
  "$API_BASE_URL/api/auth/validate-password/")

echo "❌ Respuesta sin autenticación:"
echo "$NO_AUTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$NO_AUTH_RESPONSE"

# Paso 6: Probar método GET (no permitido)
echo ""
echo "6️⃣ Probando método GET (debería fallar)..."
GET_RESPONSE=$(curl -s -X GET \
  -H "Authorization: Token $TOKEN" \
  "$API_BASE_URL/api/auth/validate-password/")

echo "❌ Respuesta con método GET:"
echo "$GET_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$GET_RESPONSE"

echo ""
echo "🎉 Pruebas completadas!"
echo ""
echo "💡 Uso recomendado en aplicaciones:"
echo "   - Validar contraseña antes de eliminaciones permanentes"
echo "   - Confirmar cambios críticos de configuración"
echo "   - Verificar identidad para operaciones sensibles"
