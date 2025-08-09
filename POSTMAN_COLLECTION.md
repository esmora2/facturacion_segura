# Ejemplo Postman con Datos Reales del Sistema

## 🎯 Colección Postman para Sistema de Pagos

### Variables de Environment
```json
{
  "base_url": "http://localhost:8000",
  "admin_token": "",
  "cliente_token": ""
}
```

---

## 📋 COLLECTION: Sistema Pagos - Flujo Completo

### 🔐 1. LOGIN ADMIN
**Name**: `Login Admin`  
**Method**: `POST`  
**URL**: `{{base_url}}/api/token/`

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

**Tests** (JavaScript):
```javascript
pm.test("Login successful", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.environment.set("admin_token", jsonData.token);
});
```

---

### 📄 2. LISTAR FACTURAS BORRADOR
**Name**: `Listar Facturas Borrador`  
**Method**: `GET`  
**URL**: `{{base_url}}/api/facturas/?estado=BORRADOR`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Tests**:
```javascript
pm.test("Facturas retrieved", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    if (jsonData.results && jsonData.results.length > 0) {
        // Guardar ID de la primera factura borrador
        pm.environment.set("factura_id", jsonData.results[0].id);
        pm.environment.set("cliente_id", jsonData.results[0].cliente);
        pm.environment.set("factura_total", jsonData.results[0].total);
    }
});
```

---

### ✅ 3. EMITIR FACTURA
**Name**: `Emitir Factura (BORRADOR → EMITIDA)`  
**Method**: `PATCH`  
**URL**: `{{base_url}}/api/facturas/{{factura_id}}/`

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

**Tests**:
```javascript
pm.test("Factura emitida", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.estado).to.eql("EMITIDA");
});
```

---

### 🔑 4. GENERAR TOKEN CLIENTE
**Name**: `Generar Token Cliente`  
**Method**: `POST`  
**URL**: `{{base_url}}/api/clientes/{{cliente_id}}/generar-token/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Tests**:
```javascript
pm.test("Token generado", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.environment.set("cliente_token", jsonData.token);
});
```

---

### 📋 5. CONSULTAR FACTURAS PENDIENTES (CLIENTE)
**Name**: `Cliente - Facturas Pendientes`  
**Method**: `GET`  
**URL**: `{{base_url}}/api/cliente/facturas-pendientes/`

**Headers**:
```
Authorization: Token {{cliente_token}}
Content-Type: application/json
```

**Tests**:
```javascript
pm.test("Facturas pendientes obtenidas", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.count).to.be.greaterThan(0);
});
```

---

### 💳 6. REGISTRAR PAGO (CLIENTE)
**Name**: `Cliente - Registrar Pago`  
**Method**: `POST`  
**URL**: `{{base_url}}/api/cliente/registrar-pago/`

**Headers**:
```
Authorization: Token {{cliente_token}}
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "factura": {{factura_id}},
  "tipo_pago": "transferencia",
  "monto": "{{factura_total}}",
  "numero_transaccion": "TRF-{{$timestamp}}",
  "observaciones": "Pago mediante transferencia bancaria - Postman Test"
}
```

**Tests**:
```javascript
pm.test("Pago registrado", function () {
    pm.response.to.have.status(201);
    var jsonData = pm.response.json();
    pm.environment.set("pago_id", jsonData.pago.id);
    pm.expect(jsonData.success).to.be.true;
});
```

---

### 📊 7. CONSULTAR PAGOS PENDIENTES (ADMIN)
**Name**: `Admin - Pagos Pendientes`  
**Method**: `GET`  
**URL**: `{{base_url}}/api/pagos/pendientes/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Tests**:
```javascript
pm.test("Pagos pendientes consultados", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    console.log("Pagos pendientes:", jsonData.count);
});
```

---

### ✅ 8A. APROBAR PAGO (ADMIN)
**Name**: `Admin - Aprobar Pago`  
**Method**: `POST`  
**URL**: `{{base_url}}/api/pagos/{{pago_id}}/validar/`

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

**Tests**:
```javascript
pm.test("Pago aprobado", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.be.true;
    pm.expect(jsonData.nuevo_estado).to.eql("aprobado");
});
```

---

### ❌ 8B. RECHAZAR PAGO (ADMIN) - ALTERNATIVO
**Name**: `Admin - Rechazar Pago`  
**Method**: `POST`  
**URL**: `{{base_url}}/api/pagos/{{pago_id}}/validar/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Body** (raw JSON):
```json
{
  "accion": "rechazar",
  "motivo": "Número de transacción no válido o comprobante insuficiente"
}
```

**Tests**:
```javascript
pm.test("Pago rechazado", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    pm.expect(jsonData.success).to.be.true;
    pm.expect(jsonData.nuevo_estado).to.eql("rechazado");
});
```

---

### 📖 9. CONSULTAR MIS PAGOS (CLIENTE)
**Name**: `Cliente - Mis Pagos`  
**Method**: `GET`  
**URL**: `{{base_url}}/api/cliente/mis-pagos/`

**Headers**:
```
Authorization: Token {{cliente_token}}
Content-Type: application/json
```

**Tests**:
```javascript
pm.test("Historial de pagos obtenido", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    console.log("Total pagos del cliente:", jsonData.count);
});
```

---

### 📈 10. ESTADÍSTICAS (ADMIN)
**Name**: `Admin - Estadísticas`  
**Method**: `GET`  
**URL**: `{{base_url}}/api/pagos/estadisticas/`

**Headers**:
```
Authorization: Token {{admin_token}}
Content-Type: application/json
```

**Tests**:
```javascript
pm.test("Estadísticas obtenidas", function () {
    pm.response.to.have.status(200);
    var jsonData = pm.response.json();
    console.log("Total pagos sistema:", jsonData.total_pagos);
    console.log("Pendientes:", jsonData.pagos_pendientes);
    console.log("Aprobados:", jsonData.pagos_aprobados);
});
```

---

## 🚀 Cómo Usar esta Colección

### Paso 1: Importar en Postman
1. Crear nueva colección llamada "Sistema Pagos"
2. Agregar las 10 requests anteriores
3. Crear environment con las variables base

### Paso 2: Configurar Environment
```json
{
  "base_url": "http://localhost:8000",
  "admin_token": "",
  "cliente_token": "",
  "factura_id": "",
  "cliente_id": "",
  "factura_total": "",
  "pago_id": ""
}
```

### Paso 3: Ejecutar en Orden
1. **Login Admin** (guarda token automáticamente)
2. **Listar Facturas Borrador** (guarda IDs automáticamente)
3. **Emitir Factura** (cambia estado a EMITIDA)
4. **Generar Token Cliente** (guarda token cliente)
5. **Cliente - Facturas Pendientes** (verifica facturas)
6. **Cliente - Registrar Pago** (registra pago)
7. **Admin - Pagos Pendientes** (verifica pago registrado)
8. **Admin - Aprobar Pago** (aprueba el pago)
9. **Cliente - Mis Pagos** (verifica estado final)
10. **Admin - Estadísticas** (dashboard general)

### Paso 4: Automatización (Runner)
- Usar Collection Runner de Postman
- Ejecutar toda la colección secuencialmente
- Las variables se pasarán automáticamente entre requests

---

## 🎯 Ejemplo con Datos Específicos

Si quieres probar con datos específicos (suponiendo que existen):

### Variables Manuales:
```json
{
  "base_url": "http://localhost:8000",
  "factura_id": "30",
  "cliente_id": "25",
  "factura_total": "1500.00"
}
```

### Request Directo - Registrar Pago:
```json
POST {{base_url}}/api/cliente/registrar-pago/
Authorization: Token {{cliente_token}}

{
  "factura": 30,
  "tipo_pago": "transferencia", 
  "monto": "1500.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago factura FAC-000030"
}
```

---

## 🔧 Troubleshooting

### Error 401 - Token inválido
- Ejecutar Login Admin nuevamente
- Verificar que el token se guardó en environment

### Error 404 - Factura/Cliente no encontrado
- Verificar IDs en la base de datos
- Usar Listar Facturas para obtener IDs válidos

### Error 400 - Factura no en estado EMITIDA
- Ejecutar "Emitir Factura" antes de registrar pago

### Error 403 - Sin permisos
- Verificar que el token del cliente corresponde al propietario de la factura

---

## 📝 Notas

1. **Orden importante**: Los requests deben ejecutarse en orden para que las variables se propaguen correctamente
2. **Tokens dinámicos**: Los tokens se generan automáticamente y se guardan en variables
3. **IDs automáticos**: Los IDs de factura, cliente y pago se capturan automáticamente
4. **Tests incluidos**: Cada request tiene tests para validar respuestas
5. **Reutilizable**: Una vez configurado, se puede ejecutar múltiples veces
