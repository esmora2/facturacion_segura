#!/bin/bash
"""
Script de ejemplo para probar el endpoint /api/auth/validate-password/ usando curl
"""

echo "🔐 PRUEBA DEL ENDPOINT /api/auth/validate-password/"
echo "============================================================"

BASE_URL="http://localhost:8000"
TOKEN_URL="$BASE_URL/api/token/"
VALIDATE_URL="$BASE_URL/api/auth/validate-password/"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Nota: Asegúrate de que el servidor Django esté ejecutándose en el puerto 8000${NC}"
echo

# Ejemplo 1: Obtener token
echo "1. 📋 EJEMPLO: Obtener token de autenticación"
echo "curl -X POST $TOKEN_URL \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"username\": \"tu_usuario\", \"password\": \"tu_contraseña\"}'"
echo

# Ejemplo 2: Validar contraseña correcta
echo "2. ✅ EJEMPLO: Validar contraseña correcta"
echo "curl -X POST $VALIDATE_URL \\"
echo "  -H \"Authorization: Token tu_token_aqui\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"password\": \"tu_contraseña\"}'"
echo

# Ejemplo 3: Validar contraseña incorrecta
echo "3. ❌ EJEMPLO: Validar contraseña incorrecta"
echo "curl -X POST $VALIDATE_URL \\"
echo "  -H \"Authorization: Token tu_token_aqui\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"password\": \"contraseña_incorrecta\"}'"
echo

# Ejemplo 4: Sin contraseña
echo "4. ⚠️  EJEMPLO: Sin contraseña"
echo "curl -X POST $VALIDATE_URL \\"
echo "  -H \"Authorization: Token tu_token_aqui\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{}'"
echo

# Ejemplo 5: Sin autenticación
echo "5. 🚫 EJEMPLO: Sin autenticación"
echo "curl -X POST $VALIDATE_URL \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"password\": \"cualquier_contraseña\"}'"
echo

echo "============================================================"
echo -e "${GREEN}📊 RESPUESTAS ESPERADAS:${NC}"
echo
echo -e "${GREEN}✅ Contraseña válida (200 OK):${NC}"
echo '{
  "message": "Contraseña válida",
  "valid": true,
  "user": {
    "id": 1,
    "username": "usuario",
    "email": "usuario@email.com",
    "role": "Administrador"
  }
}'
echo

echo -e "${RED}❌ Contraseña incorrecta (400 Bad Request):${NC}"
echo '{
  "error": "Contraseña incorrecta",
  "valid": false
}'
echo

echo -e "${RED}❌ Sin contraseña (400 Bad Request):${NC}"
echo '{
  "error": "La contraseña es requerida",
  "valid": false
}'
echo

echo -e "${RED}❌ Sin autenticación (401 Unauthorized):${NC}"
echo '{
  "detail": "Authentication credentials were not provided."
}'
echo

echo "============================================================"
echo -e "${YELLOW}💡 CASOS DE USO:${NC}"
echo "• Confirmar identidad antes de eliminar registros importantes"
echo "• Validar usuario antes de operaciones críticas"
echo "• Doble verificación en transacciones sensibles"
echo "• Confirmar permisos administrativos"
