# 🧪 **Pruebas API REST de Pagos - Guía Postman**

## 📋 **Variables de Postman**

Primero, configura estas variables en Postman:

```
BASE_URL = http://127.0.0.1:8000
ADMIN_TOKEN = [se obtiene del login]
CLIENT_TOKEN = [se genera para cada cliente]
```

---

## 🔧 **Colección de Requests para Postman**

### **1. Login como Administrador**

```http
POST {{BASE_URL}}/api/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Respuesta esperada:**
```json
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "Administrador"
  }
}
```

**Script Post-request:**
```javascript
// Guardar token en variable
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.globals.set("ADMIN_TOKEN", response.token);
}
```

---

### **2. Obtener Lista de Clientes**

```http
GET {{BASE_URL}}/api/clientes/
Authorization: Token {{ADMIN_TOKEN}}
```

**Script Post-request:**
```javascript
// Guardar ID del primer cliente
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.length > 0) {
        pm.globals.set("CLIENT_ID", response[0].id);
    }
}
```

---

### **3. Generar Token para Cliente**

```http
POST {{BASE_URL}}/api/clientes/{{CLIENT_ID}}/generar-token/
Authorization: Token {{ADMIN_TOKEN}}
```

**Script Post-request:**
```javascript
// Guardar token del cliente
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.globals.set("CLIENT_TOKEN", response.token);
}
```

---

### **3.5. Cambiar Estado de Factura (si está en BORRADOR)**

Si al consultar las facturas del cliente encuentras que están en estado `BORRADOR`, debes cambiarlas a `PENDIENTE` o `EMITIDA`:

```http
PATCH {{BASE_URL}}/api/facturas/{{FACTURA_ID}}/
Authorization: Token {{ADMIN_TOKEN}}
Content-Type: application/json

{
  "estado": "PENDIENTE"
}
```

**Script Post-request:**
```javascript
// Confirmar cambio de estado
if (pm.response.code === 200) {
    const response = pm.response.json();
    console.log("Estado actualizado:", response.estado);
}
```

---

### **4. Ver Facturas del Cliente (usando token de cliente)**

```http
GET {{BASE_URL}}/api/cliente/facturas/
X-Client-Token: {{CLIENT_TOKEN}}
```

**⚠️ Nota:** 
- Solo se muestran facturas en estado `PENDIENTE` o `EMITIDA`. Las facturas en `BORRADOR` no aparecen.
- **IMPORTANTE**: Usa el header `X-Client-Token` en lugar de `Authorization` para evitar conflictos con el sistema de autenticación de Django.

**Script Post-request:**
```javascript
// Guardar ID de factura pendiente para pruebas
if (pm.response.code === 200) {
    const response = pm.response.json();
    const facturas = response.facturas;
    
    for (let factura of facturas) {
        if ((factura.estado === 'PENDIENTE' || factura.estado === 'EMITIDA') && !factura.tiene_pagos_pendientes) {
            pm.globals.set("FACTURA_ID", factura.id);
            pm.globals.set("FACTURA_TOTAL", factura.total);
            console.log("Factura encontrada - ID:", factura.id, "Estado:", factura.estado, "Total:", factura.total);
            break;
        }
    }
}
```

---

### **5. Registrar Pago (cliente paga su factura)**

```http
POST {{BASE_URL}}/api/cliente/pagar/
X-Client-Token: {{CLIENT_TOKEN}}
Content-Type: application/json

{
  "factura": {{FACTURA_ID}},
  "tipo_pago": "transferencia",
  "monto": {{FACTURA_TOTAL}},
  "numero_transaccion": "TXN-POSTMAN-{{$timestamp}}",
  "observacion": "Pago realizado desde Postman"
}
```

**⚠️ IMPORTANTE**: Usa el header `X-Client-Token` en lugar de `Authorization`

**Script Post-request:**
```javascript
// Guardar ID del pago para validación
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.globals.set("PAGO_ID", response.pago.id);
}
```

---

### **6. Ver Pagos Pendientes (como admin/validador)**

```http
GET {{BASE_URL}}/api/pagos/pendientes/
Authorization: Token {{ADMIN_TOKEN}}
```

---

### **7. Aprobar Pago**

```http
POST {{BASE_URL}}/api/pagos/{{PAGO_ID}}/validar/
Authorization: Token {{ADMIN_TOKEN}}
Content-Type: application/json

{
  "accion": "aprobar"
}
```

---

### **8. Rechazar Pago (alternativo)**

```http
POST {{BASE_URL}}/api/pagos/{{PAGO_ID}}/validar/
Authorization: Token {{ADMIN_TOKEN}}
Content-Type: application/json

{
  "accion": "rechazar",
  "motivo": "Número de transacción inválido"
}
```

---

### **9. Verificar Estado de Factura Actualizada**

```http
GET {{BASE_URL}}/api/cliente/facturas/
X-Client-Token: {{CLIENT_TOKEN}}
```

---

## 🎯 **Flujo Completo de Prueba**

### **Paso a Paso:**

1. **Login Admin** → Obtener `ADMIN_TOKEN`
2. **Listar Clientes** → Obtener `CLIENT_ID`
3. **Generar Token Cliente** → Obtener `CLIENT_TOKEN`
4. **Ver Facturas Cliente** → Obtener `FACTURA_ID` pendiente
5. **Cliente Registra Pago** → Obtener `PAGO_ID`
6. **Admin Ve Pagos Pendientes** → Confirmar pago en lista
7. **Admin Aprueba Pago** → Validar pago
8. **Verificar Factura Pagada** → Confirmar estado actualizado

---

## 🧪 **Test Scripts Automatizados**

### **Test para Login:**
```javascript
pm.test("Login exitoso", function () {
    pm.response.to.have.status(200);
    pm.expect(pm.response.json()).to.have.property('token');
});
```

### **Test para Registro de Pago:**
```javascript
pm.test("Pago registrado correctamente", function () {
    pm.response.to.have.status(201);
    const response = pm.response.json();
    pm.expect(response).to.have.property('mensaje');
    pm.expect(response.pago.estado).to.eql('pendiente');
});
```

### **Test para Validación de Pago:**
```javascript
pm.test("Pago aprobado correctamente", function () {
    pm.response.to.have.status(200);
    const response = pm.response.json();
    pm.expect(response.mensaje).to.include('aprobado');
    pm.expect(response.factura_estado).to.eql('PAGADA');
});
```

---

## 🚨 **Casos de Error Comunes**

### **Error 401 - Token inválido:**
```json
{
  "error": "Token de autorización requerido"
}
```

### **Error 403 - Sin permisos:**
```json
{
  "error": "La factura no existe o no pertenece al cliente"
}
```

### **Error 400 - Validación fallida:**
```json
{
  "monto": ["El monto debe coincidir con el total de la factura (23.00)"]
}
```

### **Error 400 - Estado inválido:**
```json
{
  "factura": ["La factura debe estar en estado PENDIENTE o EMITIDA para poder recibir pagos"]
}
```

### **⚠️ Importante - Formato del Monto:**
- Usa formato decimal: `23.00` en lugar de `23`
- El monto debe coincidir EXACTAMENTE con el total de la factura
- Si la factura tiene total `"23.00"`, envía `23.00` en el JSON
```

---

## 📊 **Variables Esperadas al Final**

Después de ejecutar todos los requests, deberías tener:

- `ADMIN_TOKEN`: Token de administrador
- `CLIENT_TOKEN`: Token específico del cliente
- `CLIENT_ID`: ID del cliente de prueba
- `FACTURA_ID`: ID de la factura a pagar
- `FACTURA_TOTAL`: Monto total de la factura
- `PAGO_ID`: ID del pago registrado

---

## 🎉 **Importar Colección**

Puedes importar esta colección en Postman copiando este JSON:

```json
{
  "info": {
    "name": "Sistema de Pagos - Facturación Segura",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "BASE_URL",
      "value": "http://127.0.0.1:8000"
    }
  ],
  "item": [
    {
      "name": "1. Login Admin",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"username\": \"admin\", \"password\": \"admin123\"}"
        },
        "url": "{{BASE_URL}}/api/auth/login/"
      }
    },
    {
      "name": "2. Listar Clientes",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Token {{ADMIN_TOKEN}}"
          }
        ],
        "url": "{{BASE_URL}}/api/clientes/"
      }
    },
    {
      "name": "3. Generar Token Cliente",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Token {{ADMIN_TOKEN}}"
          }
        ],
        "url": "{{BASE_URL}}/api/clientes/{{CLIENT_ID}}/generar-token/"
      }
    },
    {
      "name": "4. Ver Facturas Cliente",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Token {{CLIENT_TOKEN}}"
          }
        ],
        "url": "{{BASE_URL}}/api/cliente/facturas/"
      }
    },
    {
      "name": "5. Cliente Registra Pago",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Token {{CLIENT_TOKEN}}"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"factura\": {{FACTURA_ID}}, \"tipo_pago\": \"transferencia\", \"monto\": {{FACTURA_TOTAL}}, \"numero_transaccion\": \"TXN-POSTMAN-{{$timestamp}}\", \"observacion\": \"Pago desde Postman\"}"
        },
        "url": "{{BASE_URL}}/api/cliente/pagar/"
      }
    },
    {
      "name": "6. Ver Pagos Pendientes",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Token {{ADMIN_TOKEN}}"
          }
        ],
        "url": "{{BASE_URL}}/api/pagos/pendientes/"
      }
    },
    {
      "name": "7. Aprobar Pago",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Token {{ADMIN_TOKEN}}"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\"accion\": \"aprobar\"}"
        },
        "url": "{{BASE_URL}}/api/pagos/{{PAGO_ID}}/validar/"
      }
    }
  ]
}
```

¡Con esta guía puedes probar completamente el sistema de pagos usando Postman! 🚀
