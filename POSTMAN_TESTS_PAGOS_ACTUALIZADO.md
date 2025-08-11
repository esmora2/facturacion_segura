# Pruebas de Pagos - Sistema de Cliente Token

## Configuración Actualizada

### ✅ Cambios Realizados

1. **Creación de permisos personalizados** (`apps/facturacion/permissions.py`):
   - `AllowClientTokenAuth`: Permite acceso sin autenticación Django 
   - `PagosRolePermission`: Requiere rol 'pagos' o 'Administrador'

2. **Actualización de vistas** (`apps/facturacion/views_pagos.py`):
   - `registrar_pago_cliente`: Usa `AllowClientTokenAuth` - **SIN autenticación Django**
   - `facturas_cliente`: Usa `AllowClientTokenAuth` - **SIN autenticación Django**
   - `pagos_pendientes`: Usa `PagosRolePermission` - **CON autenticación Django**
   - `PagoViewSet`: Usa `PagosRolePermission` - **CON autenticación Django**

## 🧪 Pruebas en Postman

### 1. Generar Token de Cliente

```http
GET http://localhost:8000/clientes/1/generar-token/
```

**Headers:** NINGUNO requerido para este endpoint

**Respuesta esperada:**
```json
{
    "cliente": "Nombre del Cliente",
    "token": "abc123def456...",
    "message": "Token generado exitosamente"
}
```

### 2. Registrar Pago de Cliente (SIN autenticación Django)

```http
POST http://localhost:8000/api/cliente/pagar/
```

**Headers:**
```
X-Client-Token: [TOKEN_OBTENIDO_DEL_PASO_1]
Content-Type: application/json
```

**NO incluir:** Authorization header

**Body:**
```json
{
    "factura": 1,
    "monto": 1500.00,
    "metodo_pago": "transferencia",
    "referencia_transaccion": "TXN789012",
    "notas": "Pago realizado por transferencia bancaria"
}
```

**Respuesta esperada:**
```json
{
    "mensaje": "Pago registrado exitosamente. Será validado por el equipo de pagos.",
    "pago": {
        "id": 1,
        "factura": 1,
        "monto": "1500.00",
        "estado": "pendiente",
        "metodo_pago": "transferencia",
        "referencia_transaccion": "TXN789012",
        "pagado_por": "Nombre del Cliente",
        "created_at": "2025-08-07T12:30:00Z"
    }
}
```

### 3. Ver Facturas de Cliente (SIN autenticación Django)

```http
GET http://localhost:8000/api/cliente/facturas/
```

**Headers:**
```
X-Client-Token: [TOKEN_OBTENIDO_DEL_PASO_1]
```

**NO incluir:** Authorization header

### 4. Ver Pagos Pendientes (CON autenticación Django)

```http
GET http://localhost:8000/api/pagos/pendientes/
```

**Headers:**
```
Authorization: Token [DJANGO_USER_TOKEN]
Content-Type: application/json
```

## 🔧 Diagnóstico de Problemas

### Error: "Authentication credentials were not provided"

**Solución:** Este error NO debería aparecer más para los endpoints de cliente porque ahora usan `AllowClientTokenAuth`.

Si sigue apareciendo:

1. **Verificar que el header es correcto:**
   ```
   X-Client-Token: tu_token_aqui
   ```

2. **NO incluir Authorization header** en endpoints de cliente

3. **Verificar que el token existe:**
   ```sql
   SELECT * FROM clientes_clientetoken WHERE key = 'tu_token';
   ```

### Error: "Token de cliente inválido"

**Causas posibles:**
1. Token no generado o expirado
2. Copia incorrecta del token
3. Cliente no existe

**Solución:**
1. Generar nuevo token via `/clientes/1/generar-token/`
2. Copiar token completo sin espacios
3. Verificar que el cliente existe

## 📋 Checklist de Pruebas

- [ ] ✅ Generar token de cliente
- [ ] ✅ Registrar pago SIN Authorization header
- [ ] ✅ Ver facturas del cliente SIN Authorization header  
- [ ] ✅ Ver pagos pendientes CON Authorization header
- [ ] ✅ Validar pago CON Authorization header

## 🎯 Endpoints Actualizados

| Endpoint | Autenticación | Header Requerido |
|----------|---------------|------------------|
| `/clientes/1/generar-token/` | ❌ Ninguna | Ninguno |
| `/api/cliente/pagar/` | ❌ Django Token | `X-Client-Token` |
| `/api/cliente/facturas/` | ❌ Django Token | `X-Client-Token` |
| `/api/pagos/pendientes/` | ✅ Django Token | `Authorization: Token xxx` |
| `/api/pagos/{id}/validar/` | ✅ Django Token | `Authorization: Token xxx` |

Los endpoints marcados con ❌ ya NO requieren autenticación Django, solo su propio sistema de tokens.
