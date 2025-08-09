# Ejemplo Corregido - Registro de Pago

## 🚨 Error Detectado y Solucionado

**Error encontrado**:
```json
{
    "pagado_por": [
        "This field is required."
    ]
}
```

## ✅ Request Corregido

### POST http://localhost:8000/api/pagos/

**Headers**:
```
Authorization: Token <admin_token>
Content-Type: application/json
```

**Body corregido**:
```json
{
  "factura": 30,
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
  "pagado_por": 1
}
```

## 📋 Campos Requeridos para Registro de Pago

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `factura` | int | ID de la factura | 30 |
| `tipo_pago` | string | efectivo/tarjeta/transferencia/cheque | "transferencia" |
| `monto` | decimal | Monto del pago | "23.00" |
| `numero_transaccion` | string | Código del comprobante | "TRF-2025-08-07-001" |
| `pagado_por` | int | ID del usuario que registra | 1 |
| `observaciones` | string | Comentarios (opcional) | "Descripción del pago" |

## 🔍 Cómo Obtener el ID del Usuario

### Opción 1: Consultar usuarios disponibles
```bash
GET http://localhost:8000/api/usuarios/
Authorization: Token <admin_token>
```

### Opción 2: Ver información del usuario logueado
```bash
GET http://localhost:8000/api/me/
Authorization: Token <admin_token>
```

## 🚀 Ejemplo Completo de Prueba

```bash
# 1. Login
POST http://localhost:8000/api/token/
{
  "username": "admin",
  "password": "admin123"
}

# 2. Obtener info del usuario
GET http://localhost:8000/api/me/
Authorization: Token <token_obtenido>

# 3. Registrar pago (usando el ID del usuario del paso 2)
POST http://localhost:8000/api/pagos/
Authorization: Token <token_obtenido>
{
  "factura": 30,
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago de prueba",
  "pagado_por": <user_id_del_paso_2>
}
```

## 📝 Notas Importantes

1. **Campo obligatorio**: `pagado_por` es requerido y debe ser un ID válido de usuario
2. **Validación**: El usuario debe existir en la tabla de usuarios
3. **Permisos**: Solo usuarios con permisos pueden registrar pagos
4. **Auditoría**: Este campo permite rastrear quién registró cada pago
