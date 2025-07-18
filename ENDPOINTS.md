# 📋 LISTA COMPLETA DE ENDPOINTS - Sistema de Facturación Segura

## 🔐 AUTENTICACIÓN Y AUTORIZACIÓN

### Obtener Token de Autenticación
```
POST /api/token/
Content-Type: application/json
{
    "username": "usuario",
    "password": "contraseña"
}
```

### Información del Usuario Autenticado
```
GET /api/me/
Authorization: Token <token>
```

### Validar Contraseña para Operaciones Críticas ⚠️
```
POST /api/auth/validate-password/
Authorization: Token <token>
Content-Type: application/json
{
    "password": "contraseña_del_usuario"
}

Response (Éxito):
{
    "message": "Contraseña válida",
    "valid": true,
    "user": {
        "id": 1,
        "username": "usuario",
        "email": "usuario@example.com",
        "role": "Administrador"
    }
}

Response (Error):
{
    "error": "Contraseña incorrecta",
    "valid": false
}
```

---

## 👥 GESTIÓN DE USUARIOS (Solo Administradores)

### Operaciones CRUD Básicas
```
GET    /api/usuarios/           # Listar usuarios
POST   /api/usuarios/           # Crear usuario
GET    /api/usuarios/{id}/      # Obtener usuario específico
PUT    /api/usuarios/{id}/      # Actualizar usuario completo
PATCH  /api/usuarios/{id}/      # Actualizar usuario parcial
DELETE /api/usuarios/{id}/      # Eliminar usuario
```

### Actions Personalizadas
```
POST /api/usuarios/{id}/toggle_active/    # Activar/desactivar usuario
POST /api/usuarios/{id}/change_role/      # Cambiar rol de usuario
GET  /api/usuarios/roles/                 # Obtener lista de roles disponibles
```

---

## 👨‍💼 GESTIÓN DE CLIENTES

### Permisos de Acceso:
- **Administrador**: ✅ Acceso completo (CRUD)
- **Secretario**: ✅ Acceso completo (CRUD)  
- **Ventas**: ✅ Solo lectura (GET) - ¡NUEVO!

### Operaciones CRUD Básicas
```
GET    /api/clientes/           # Listar clientes (Admin, Secretario, Ventas)
POST   /api/clientes/           # Crear cliente (Solo Admin, Secretario)
GET    /api/clientes/{id}/      # Obtener cliente específico (Admin, Secretario, Ventas)
PUT    /api/clientes/{id}/      # Actualizar cliente completo (Solo Admin, Secretario)
PATCH  /api/clientes/{id}/      # Actualizar cliente parcial (Solo Admin, Secretario)
DELETE /api/clientes/{id}/      # Eliminar cliente (Solo Admin, Secretario)
```
PUT    /api/clientes/{id}/      # Actualizar cliente completo
PATCH  /api/clientes/{id}/      # Actualizar cliente parcial
DELETE /api/clientes/{id}/      # Eliminar cliente
```

---

## 📦 GESTIÓN DE PRODUCTOS

### Permisos de Acceso:
- **Administrador**: ✅ Acceso completo (CRUD)
- **Bodega**: ✅ Acceso completo (CRUD)
- **Ventas**: ✅ Solo lectura (GET) - ¡NUEVO!

### Operaciones CRUD Básicas
```
GET    /api/productos/          # Listar productos (Admin, Bodega, Ventas)
POST   /api/productos/          # Crear producto (Solo Admin, Bodega)
GET    /api/productos/{id}/     # Obtener producto específico (Admin, Bodega, Ventas)
PUT    /api/productos/{id}/     # Actualizar producto completo (Solo Admin, Bodega)
PATCH  /api/productos/{id}/     # Actualizar producto parcial (Solo Admin, Bodega)
DELETE /api/productos/{id}/     # Eliminar producto (Solo Admin, Bodega)
```

---

## 🧾 GESTIÓN DE FACTURAS (Administrador + Ventas)

### Operaciones CRUD Básicas
```
GET    /api/facturas/           # Listar facturas
POST   /api/facturas/           # Crear factura
GET    /api/facturas/{id}/      # Obtener factura específica
PUT    /api/facturas/{id}/      # Actualizar factura (solo BORRADOR)
PATCH  /api/facturas/{id}/      # Actualizar factura parcial (solo BORRADOR)
DELETE /api/facturas/{id}/      # Eliminar factura (solo creador/admin, solo BORRADOR)
```

### Actions Personalizadas
```
POST /api/facturas/{id}/send_pdf/         # Enviar PDF por email al cliente
POST /api/facturas/{id}/emitir/           # Emitir factura (BORRADOR → EMITIDA)
POST /api/facturas/{id}/marcar_pagada/    # Marcar como pagada (EMITIDA → PAGADA)
POST /api/facturas/{id}/anular_factura/   # Anular factura (restituir stock)
GET  /api/facturas/metrics/               # Obtener métricas de facturas
```

---

## 🌐 VISTAS WEB (HTML)

### Autenticación
```
GET  /accounts/login/         # Página de login
POST /accounts/login/         # Procesar login
GET  /accounts/logout/        # Cerrar sesión
```

### Páginas Principales
```
GET /                         # Página principal (home)
GET /clientes/                # Lista de clientes (Secretario + Admin)
GET /productos/               # Lista de productos (Bodega + Admin)
GET /facturacion/             # Lista de facturas (Ventas + Admin)
```

### Acciones Específicas
```
POST /facturacion/eliminar/{id}/   # Eliminar factura (vista web)
```

### Panel de Administración
```
GET /admin/                   # Panel de administración Django
```

---

## 📊 FORMATOS DE RESPUESTA

### Ejemplo de Cliente
```json
{
    "id": 1,
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "telefono": "+1234567890",
    "activo": true,
    "roles": [
        {"name": "Cliente"}
    ]
}
```

### Ejemplo de Producto
```json
{
    "id": 1,
    "nombre": "Laptop HP",
    "descripcion": "Laptop HP Core i5",
    "stock": 10,
    "precio": "999.99"
}
```

### Ejemplo de Factura
```json
{
    "id": 1,
    "creador": 1,
    "cliente": 1,
    "fecha": "2025-07-09T10:30:00Z",
    "estado": "EMITIDA",
    "numero_factura": "FAC-000001",
    "anulada": false,
    "items": [
        {
            "id": 1,
            "producto": 1,
            "cantidad": 2
        }
    ]
}
```

### Ejemplo de Usuario
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@sistema.com",
    "first_name": "Administrador",
    "last_name": "Sistema",
    "role": "Administrador",
    "is_active": true,
    "date_joined": "2025-01-01T00:00:00Z"
}
```

---

## 🔒 CONTROL DE ACCESO POR ENDPOINT

### Públicos (Sin autenticación)
- `POST /api/token/` - Obtener token
- `GET /accounts/login/` - Página de login

### Autenticación Requerida
- `GET /api/me/` - Cualquier usuario autenticado

### Solo Administradores
- `/api/usuarios/*` - Gestión completa de usuarios
- `/admin/*` - Panel de administración

### Administrador + Secretario
- `/api/clientes/*` - Gestión de clientes
- `/clientes/` - Vista web de clientes

### Administrador + Bodega
- `/api/productos/*` - Gestión de productos
- `/productos/` - Vista web de productos

### Administrador + Ventas
- `/api/facturas/*` - Gestión de facturas
- `/facturacion/*` - Vista web de facturas

---

## ⚙️ CARACTERÍSTICAS ESPECIALES

### Transacciones Atómicas
- Todas las operaciones CRUD usan transacciones atómicas
- Stock se maneja automáticamente en creación/eliminación/anulación

### Estados de Factura
- **BORRADOR**: Editable y eliminable
- **EMITIDA**: Solo puede marcarse como pagada o anularse
- **PAGADA**: Solo puede anularse
- **ANULADA**: Inmutable

### Validaciones Automáticas
- Stock insuficiente al crear facturas
- Permisos de eliminación (solo creador o admin)
- Estados válidos para cada operación

### Middleware Personalizado
- Verificación de usuario activo
- Control de acceso por rol
- Cierre automático de sesión si usuario es eliminado/desactivado

---

## 📈 MÉTRICAS DISPONIBLES

### Facturas por Día
```
GET /api/facturas/metrics/
Response:
{
    "facturas_por_dia": {
        "labels": ["2025-07-03", "2025-07-04", "2025-07-05"],
        "data": [5, 8, 12]
    }
}
```

---

## 🔄 ESTADOS HTTP COMUNES

- **200**: OK - Operación exitosa
- **201**: Created - Recurso creado exitosamente
- **400**: Bad Request - Datos inválidos
- **401**: Unauthorized - Token inválido o faltante
- **403**: Forbidden - Sin permisos para la operación
- **404**: Not Found - Recurso no encontrado
- **500**: Internal Server Error - Error del servidor

---

# 📋 DOCUMENTACIÓN DEL ENDPOINT DE EMISIÓN DE FACTURAS

## Emitir Factura

### Descripción
Este endpoint permite emitir una factura que ha sido previamente creada y guardada como borrador. Una vez emitida, la factura cambiará su estado a "EMITIDA" y no podrá ser modificada excepto para marcarla como pagada o anularla.

### Endpoint
```
POST /api/facturas/{id}/emitir/
```

### Parámetros

| Nombre | Tipo   | Descripción |
|--------|--------|-------------|
| id     | entero | ID de la factura a emitir |

### Headers

| Nombre          | Tipo    | Descripción                        |
|-----------------|---------|------------------------------------|
| Authorization   | string  | Token de autenticación del usuario |
| Content-Type    | string  | Debe ser siempre `application/json`|

### Request Body
No se requiere cuerpo en la solicitud.

### Respuestas

#### Éxito (200 OK)
```json
{
    "id": 1,
    "estado": "EMITIDA",
    "numero_factura": "FAC-000001",
    "fecha_emision": "2025-07-09T10:30:00Z",
    "mensaje": "Factura emitida exitosamente."
}
```

#### Error - Factura No Encontrada (404 Not Found)
```json
{
    "error": "Factura no encontrada."
}
```

#### Error - Estado Inválido (400 Bad Request)
```json
{
    "error": "La factura solo puede ser emitida si está en estado BORRADOR."
}
```

#### Error - Sin Permisos (403 Forbidden)
```json
{
    "error": "No tiene permisos para emitir esta factura."
}
```

---

## Ejemplo de Uso

### Solicitud
```
POST /api/facturas/1/emitir/
Authorization: Token <token>
Content-Type: application/json
```

### Respuesta Exitosa
```json
{
    "id": 1,
    "estado": "EMITIDA",
    "numero_factura": "FAC-000001",
    "fecha_emision": "2025-07-09T10:30:00Z",
    "mensaje": "Factura emitida exitosamente."
}
```

### Respuesta de Error - Factura No Encontrada
```json
{
    "error": "Factura no encontrada."
}
```

### Respuesta de Error - Estado Inválido
```json
{
    "error": "La factura solo puede ser emitida si está en estado BORRADOR."
}
```

### Respuesta de Error - Sin Permisos
```json
{
    "error": "No tiene permisos para emitir esta factura."
}
```
