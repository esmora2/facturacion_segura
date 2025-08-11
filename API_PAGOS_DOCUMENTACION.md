# 📋 **API de Pagos - Documentación Completa**

## 🌟 **Resumen del Sistema**

El sistema de pagos permite a los clientes registrar pagos para sus facturas mediante tokens de autenticación, mientras que los usuarios con rol "pagos" pueden validar (aprobar/rechazar) estos pagos.

---

## 🔐 **Autenticación**

### **Para Clientes (Token de Cliente)**
```
Authorization: Token <cliente_token>
```

### **Para Usuarios del Sistema (Token de Usuario)**
```
Authorization: Token <user_token>
```

---

## 📍 **Endpoints Disponibles**

### **1. Obtener Facturas del Cliente**
```http
GET /api/cliente/facturas/
```

**Headers:**
```
Authorization: Token <cliente_token>
Content-Type: application/json
```

**Respuesta exitosa (200):**
```json
{
  "cliente": "Juan Pérez",
  "facturas": [
    {
      "id": 1,
      "numero_factura": "FAC-000001",
      "fecha": "2025-01-15T10:30:00Z",
      "estado": "PENDIENTE",
      "subtotal": 100.00,
      "iva": 15.00,
      "total": 115.00,
      "pagos_count": 0,
      "tiene_pagos_pendientes": false
    }
  ]
}
```

---

### **2. Registrar Pago (Cliente)**
```http
POST /api/cliente/pagar/
```

**Headers:**
```
Authorization: Token <cliente_token>
Content-Type: application/json
```

**Body:**
```json
{
  "factura": 1,
  "tipo_pago": "transferencia",
  "monto": 115.00,
  "numero_transaccion": "TXN-123456789",
  "observacion": "Pago mediante transferencia bancaria"
}
```

**Respuesta exitosa (201):**
```json
{
  "mensaje": "Pago registrado exitosamente. Será validado por el equipo de pagos.",
  "pago": {
    "id": 1,
    "factura": 1,
    "factura_numero": "FAC-000001",
    "tipo_pago": "transferencia",
    "monto": "115.00",
    "numero_transaccion": "TXN-123456789",
    "observacion": "Pago mediante transferencia bancaria",
    "estado": "pendiente",
    "pagado_por": 1,
    "cliente_nombre": "Juan Pérez",
    "validado_por": null,
    "validador_nombre": null,
    "created_at": "2025-01-15T15:30:00Z",
    "validated_at": null
  }
}
```

---

### **3. Ver Pagos Pendientes (Rol Pagos/Admin)**
```http
GET /api/pagos/pendientes/
```

**Headers:**
```
Authorization: Token <user_token>
Content-Type: application/json
```

**Respuesta exitosa (200):**
```json
{
  "total_pendientes": 2,
  "pagos": [
    {
      "id": 1,
      "factura": 1,
      "factura_numero": "FAC-000001",
      "tipo_pago": "transferencia",
      "monto": "115.00",
      "numero_transaccion": "TXN-123456789",
      "observacion": "Pago mediante transferencia bancaria",
      "estado": "pendiente",
      "pagado_por": 1,
      "cliente_nombre": "Juan Pérez",
      "validado_por": null,
      "validador_nombre": null,
      "created_at": "2025-01-15T15:30:00Z",
      "validated_at": null
    }
  ]
}
```

---

### **4. Validar Pago (Aprobar/Rechazar)**
```http
POST /api/pagos/{pago_id}/validar/
```

**Headers:**
```
Authorization: Token <user_token>
Content-Type: application/json
```

**Body para Aprobar:**
```json
{
  "accion": "aprobar"
}
```

**Body para Rechazar:**
```json
{
  "accion": "rechazar",
  "motivo": "Número de transacción inválido"
}
```

**Respuesta exitosa (200) - Aprobación:**
```json
{
  "mensaje": "Pago aprobado exitosamente",
  "factura_estado": "PAGADA"
}
```

**Respuesta exitosa (200) - Rechazo:**
```json
{
  "mensaje": "Pago rechazado exitosamente"
}
```

---

### **5. CRUD Completo de Pagos (Admin)**
```http
GET /api/pagos/                 # Listar todos los pagos
GET /api/pagos/{id}/           # Ver pago específico
PUT /api/pagos/{id}/           # Actualizar pago (solo admin)
DELETE /api/pagos/{id}/        # Eliminar pago (solo admin)
```

---

## 🔍 **Tipos de Pago Disponibles**

- `efectivo` - Efectivo
- `tarjeta` - Tarjeta de crédito/débito
- `transferencia` - Transferencia bancaria
- `cheque` - Cheque

---

## 📊 **Estados de Pago**

- `pendiente` - Pago registrado, esperando validación
- `aprobado` - Pago aprobado por validador
- `rechazado` - Pago rechazado por validador

---

## 📋 **Estados de Factura**

- `BORRADOR` - Factura en edición
- `PENDIENTE` - Factura emitida, esperando pago (estado por defecto)
- `PAGADA` - Factura pagada y aprobada
- `ANULADA` - Factura cancelada

---

## ⚠️ **Validaciones y Restricciones**

### **Validaciones de Pago:**
- El monto debe coincidir exactamente con el total de la factura
- Solo el cliente dueño de la factura puede registrar el pago
- No se pueden registrar pagos para facturas ya pagadas o anuladas
- El número de transacción es obligatorio

### **Validaciones de Factura:**
- Una factura solo puede tener un pago aprobado
- Al aprobar un pago, la factura cambia automáticamente a "PAGADA"
- Al rechazar un pago, la factura permanece "PENDIENTE"

### **Permisos:**
- **Clientes:** Solo pueden ver sus facturas y registrar pagos
- **Rol "pagos":** Pueden ver y validar pagos pendientes
- **Administradores:** Acceso completo a todos los pagos

---

## 🚨 **Códigos de Error Comunes**

### **401 - Token Inválido**
```json
{
  "error": "Token de autorización requerido"
}
```

### **403 - Sin Permisos**
```json
{
  "error": "No tienes permiso para validar pagos"
}
```

### **400 - Validación Fallida**
```json
{
  "monto": ["El monto debe coincidir con el total de la factura (115.00)"]
}
```

### **404 - Recurso No Encontrado**
```json
{
  "error": "La factura no existe o no pertenece al cliente"
}
```

---

## 🔧 **Ejemplos de Uso con cURL**

### **Cliente registra pago:**
```bash
curl -X POST "http://localhost:8000/api/cliente/pagar/" \
  -H "Authorization: Token abc123clientetoken" \
  -H "Content-Type: application/json" \
  -d '{
    "factura": 1,
    "tipo_pago": "transferencia", 
    "monto": 115.00,
    "numero_transaccion": "TXN-987654321",
    "observacion": "Pago completo"
  }'
```

### **Validador aprueba pago:**
```bash
curl -X POST "http://localhost:8000/api/pagos/1/validar/" \
  -H "Authorization: Token def456usertoken" \
  -H "Content-Type: application/json" \
  -d '{
    "accion": "aprobar"
  }'
```

---

## 🎯 **Flujo Completo del Sistema**

1. **Cliente ve sus facturas:** `GET /api/cliente/facturas/`
2. **Cliente registra pago:** `POST /api/cliente/pagar/`
3. **Validador ve pagos pendientes:** `GET /api/pagos/pendientes/`
4. **Validador aprueba/rechaza:** `POST /api/pagos/{id}/validar/`
5. **Sistema actualiza automáticamente el estado de la factura**

---

Este sistema garantiza un flujo seguro y auditado para el manejo de pagos en el sistema de facturación. 🎉
