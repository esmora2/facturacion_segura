# Flujo Completo en Postman - Factura ID 30, Cliente ID 25

## Contexto
- **Factura ID**: 30 (estado BORRADOR)
- **Cliente ID**: 25
- **Objetivo**: Emitir factura y registrar pago

## Variables de Postman (Configurar en Environment)

```json
{
  "base_url": "http://localhost:8000",
  "admin_token": "{{admin_token}}",
  "cliente_token": "{{cliente_token}}"
}
```

---

## 🔐 PASO 1: Obtener Token de Administrador

**Request**: `POST {{base_url}}/api/token/`

**Headers**:
```
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response esperada**:
```json
{
  "token": "abc123def456..."
}
```

**Action**: Copiar el token y guardarlo en la variable `admin_token` del environment.

---

## 📄 PASO 2: Verificar Estado de la Factura

**Request**: `GET {{base_url}}/api/facturas/30/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Response esperada**:
```json
{
  "id": 30,
  "numero_factura": "FAC-000030",
  "cliente": 25,
  "estado": "BORRADOR",
  "total": "1500.00",
  "fecha": "2025-08-07T10:30:00Z",
  "cliente_info": {
    "id": 25,
    "nombre": "Cliente Ejemplo",
    "email": "cliente@ejemplo.com"
  }
}
```

---

## ✅ PASO 3: Cambiar Factura de BORRADOR a EMITIDA

**Request**: `PATCH {{base_url}}/api/facturas/30/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "estado": "EMITIDA"
}
```

**Response esperada**:
```json
{
  "id": 30,
  "numero_factura": "FAC-000030",
  "cliente": 25,
  "estado": "EMITIDA",
  "total": "1500.00",
  "fecha": "2025-08-07T10:30:00Z",
  "fecha_emision": "2025-08-07T11:00:00Z"
}
```

---

## � PASO 4: Admin Consulta Facturas del Cliente 25

**Request**: `GET {{base_url}}/api/facturas/?cliente=25&estado=EMITIDA`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Response esperada**:
```json
{
  "count": 1,
  "results": [
    {
      "id": 30,
      "numero_factura": "FAC-000030",
      "cliente": 25,
      "estado": "EMITIDA",
      "total": "1500.00",
      "fecha": "2025-08-07T10:30:00Z",
      "cliente_info": {
        "id": 25,
        "nombre": "Cliente Ejemplo",
        "email": "cliente@ejemplo.com"
      }
    }
  ]
}
```

**Nota**: En este sistema, los clientes de la tabla `Cliente` no tienen autenticación propia. Los pagos se registran a través del administrador especificando el cliente mediante su ID.

---

## 💳 PASO 5: Admin Registra Pago en Nombre del Cliente
```

**Request**: `POST {{base_url}}/api/pagos/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "factura": 30,
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
  "pagado_por": 25
}
```

**Nota**: El campo `pagado_por` debe ser el ID del usuario que registra el pago. En este caso se usa ID 25 (puede ser cliente o usuario según tu configuración).

**Response obtenida** (ejemplo real):
```json
{
  "id": 1,
  "factura": 30,
  "factura_numero": "FAC-000008",
  "factura_total": "23.00",
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
  "estado": "pendiente",
  "pagado_por": 25,
  "cliente_nombre": "Cliente Roles Vacíos",
  "validado_por": null,
  "fecha_pago": "2025-08-07T17:05:00.970247Z",
  "fecha_validacion": null
}
```

---

## 📊 PASO 6: Admin Consulta Pagos Pendientes

---

## 📊 PASO 6: Admin Consulta Pagos Pendientes

**Request**: `GET {{base_url}}/api/pagos/pendientes/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Response esperada**:
```json
{
  "count": 1,
  "results": [
    {
      "id": 15,
      "factura": 30,
      "factura_numero": "FAC-000030",
      "factura_total": "1500.00",
      "tipo_pago": "transferencia",
      "monto": "1500.00",
      "numero_transaccion": "TRF-2025-08-07-001",
      "cliente_nombre": "Cliente Ejemplo",
      "cliente_email": "cliente@ejemplo.com",
      "fecha_pago": "2025-08-07T11:15:00Z",
      "dias_pendiente": 0
    }
  ]
}
```

---

## ✅ PASO 7A: Admin Aprueba el Pago

**Request**: `POST {{base_url}}/api/pagos/15/validar/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "accion": "aprobar"
}
```

**Response esperada**:
```json
{
  "success": true,
  "message": "Pago #15 aprobado exitosamente",
  "pago_id": 15,
  "nuevo_estado": "aprobado",
  "fecha_validacion": "2025-08-07T11:30:00Z"
}
```

---

## ❌ PASO 7B: Admin Rechaza el Pago (Alternativo)

**Request**: `POST {{base_url}}/api/pagos/15/validar/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "accion": "rechazar",
  "motivo": "Número de transacción no coincide con registros bancarios"
}
```

**Response esperada**:
```json
{
  "success": true,
  "message": "Pago #15 rechazado",
  "pago_id": 15,
  "nuevo_estado": "rechazado",
  "fecha_validacion": "2025-08-07T11:30:00Z"
}
```

---

## 📖 PASO 8: Admin Consulta Historial de Pagos por Cliente

**Request**: `GET {{base_url}}/api/pagos/?factura__cliente=25`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Nota**: ✅ **Filtrado Corregido** - Ahora el endpoint respeta correctamente el filtro `factura__cliente` para mostrar solo pagos del cliente especificado.

**Response esperada** (si fue aprobado):
```json
{
  "count": 1,
  "results": [
    {
      "id": 15,
      "factura": 30,
      "factura_numero": "FAC-000030",
      "factura_total": "1500.00",
      "tipo_pago": "transferencia",
      "monto": "1500.00",
      "numero_transaccion": "TRF-2025-08-07-001",
      "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
      "estado": "aprobado",
      "pagado_por": 1,
      "cliente_nombre": "Cliente Ejemplo",
      "validado_por": 1,
      "validador_nombre": "admin",
      "fecha_pago": "2025-08-07T11:15:00Z",
      "fecha_validacion": "2025-08-07T11:30:00Z"
    }
  ]
}
```

---

## 🔍 PASO 9: Verificar Estado Final de la Factura

**Request**: `GET {{base_url}}/api/facturas/30/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Response esperada** (si pago fue aprobado):
```json
{
  "id": 30,
  "numero_factura": "FAC-000030",
  "cliente": 25,
  "estado": "PAGADA",
  "total": "1500.00",
  "fecha": "2025-08-07T10:30:00Z",
  "fecha_pago": "2025-08-07T11:30:00Z"
}
```

---

## 📈 PASO 10: Admin Consulta Estadísticas

**Request**: `GET {{base_url}}/api/pagos/estadisticas/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Response esperada**:
```json
{
  "total_pagos": 5,
  "pagos_pendientes": 0,
  "pagos_aprobados": 4,
  "pagos_rechazados": 1,
  "monto_total_aprobado": 6500.00,
  "pagos_ultimos_30_dias": 5,
  "distribucion_tipos_pago": [
    {
      "tipo_pago": "transferencia",
      "count": 3
    },
    {
      "tipo_pago": "efectivo",
      "count": 2
    }
  ]
}
```

---

## 🚨 Posibles Errores y Soluciones

### Error 400: "La factura debe estar en estado EMITIDA"
```json
{
  "error": "La factura debe estar en estado EMITIDA para poder registrar pagos"
}
```
**Solución**: Ejecutar PASO 3 para cambiar estado a EMITIDA.

### Error 404: "Factura no encontrada"
```json
{
  "error": "Factura con ID 30 no encontrada"
}
```
**Solución**: Verificar que la factura existe usando `GET /api/facturas/30/`.

### Error 400: "El monto no coincide con el total de la factura"
```json
{
  "error": "El monto debe coincidir exactamente con el total de la factura"
}
```
**Solución**: Ajustar el monto en el PASO 5 para que coincida con el total de la factura.

### Error 401: "Token inválido"
```json
{
  "detail": "Invalid token."
}
```
**Solución**: Ejecutar PASO 1 nuevamente para obtener un token válido.

---

## 📝 Notas Importantes

1. **Flujo Simplificado**: En este sistema, el administrador maneja todos los pagos directamente.
2. **No hay tokens de cliente**: Los clientes de la tabla `Cliente` no tienen autenticación propia.
3. **Estados**: La factura debe estar en estado EMITIDA para poder recibir pagos.
4. **Montos**: El monto del pago debe coincidir exactamente con el total de la factura.
5. **Identificación**: Los clientes se identifican por su ID en las consultas.
6. **Orden de ejecución**: Los pasos deben ejecutarse en orden secuencial.

## ✅ Resultado Final

- ✅ Factura cambia de BORRADOR → EMITIDA → PAGADA
- ✅ Pago registrado por administrador
- ✅ Pago validado por administrador
- ✅ Historial completo de auditoría
- ✅ Admin puede gestionar todo el flujo de pagos
- ✅ Seguimiento por cliente ID en lugar de autenticación de cliente
