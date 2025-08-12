# 📋 Documentación Técnica del API REST - Sistema de Facturación Segura

## 📝 Información General

**Versión:** 1.0  
**Framework:** Django REST Framework  
**Autenticación:** Token-based Authentication  
**Base URL:** `http://localhost:8000`  
**Fecha:** Agosto 2025

---

## 🔐 Sistema de Autenticación

### Tipos de Tokens
- **Token Estándar DRF:** Para empleados (Admin, Ventas, Secretario, Bodega, Pagos)
- **Token de Cliente:** Para usuarios con rol='Cliente'

### Roles del Sistema
- **Administrador:** Acceso completo al sistema
- **Ventas:** Gestión de productos y facturas
- **Secretario:** Gestión de clientes y facturas
- **Bodega:** Gestión de productos e inventario
- **Pagos:** Validación y gestión de pagos
- **Cliente:** Acceso limitado a sus propios datos

---

## 🔗 Endpoints de Autenticación

### 1. POST `/api/token/`
**Descripción:** Obtener token de autenticación estándar de Django REST Framework

**Flujo:**
1. Cliente envía credenciales (username, password)
2. Django valida credenciales contra modelo User
3. Si válido, retorna token de autenticación
4. Token se usa en header: `Authorization: Token <token>`

**Request:**
```json
{
    "username": "admin",
    "password": "password123"
}
```

**Response Exitoso (200):**
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Códigos de Error:**
- `400`: Credenciales inválidas

---

### 2. GET `/api/me/`
**Descripción:** Obtener información del usuario autenticado

**Flujo:**
1. Valida token en header Authorization
2. Obtiene usuario asociado al token
3. Serializa datos del usuario con UserSerializer
4. Retorna información del perfil

**Headers Requeridos:**
```
Authorization: Token <token>
```

**Response Exitoso (200):**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "Administrador",
    "is_active": true,
    "date_joined": "2025-01-01T10:00:00Z"
}
```

**Códigos de Error:**
- `401`: Token inválido o ausente

---

### 3. POST `/api/auth/validate-password/`
**Descripción:** Validar contraseña del usuario autenticado para operaciones críticas

**Flujo:**
1. Valida token de autenticación
2. Verifica que la contraseña proporcionada coincida con la del usuario
3. Utilizado para confirmar identidad en operaciones sensibles

**Headers Requeridos:**
```
Authorization: Token <token>
Content-Type: application/json
```

**Request:**
```json
{
    "password": "current_password"
}
```

**Response Exitoso (200):**
```json
{
    "valid": true,
    "message": "Contraseña válida"
}
```

**Códigos de Error:**
- `400`: Contraseña incorrecta
- `401`: No autenticado

---

## 👥 Gestión de Usuarios (Solo Administradores)

### 4. GET `/api/usuarios/`
**Descripción:** Listar todos los usuarios del sistema

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica que usuario tenga rol 'Administrador'
2. Obtiene todos los usuarios de la base de datos
3. Aplica paginación si está configurada
4. Serializa con UserSerializer

**Headers Requeridos:**
```
Authorization: Token <admin_token>
```

**Response Exitoso (200):**
```json
{
    "count": 25,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": "Administrador",
            "is_active": true,
            "date_joined": "2025-01-01T10:00:00Z"
        }
    ]
}
```

**Códigos de Error:**
- `403`: Sin permisos de administrador

---

### 5. POST `/api/usuarios/`
**Descripción:** Crear nuevo usuario en el sistema

**Permisos:** Solo Administradores

**Flujo:**
1. Valida permisos de administrador
2. Valida datos con UserCreateSerializer
3. Verifica que username sea único
4. Confirma que password y confirm_password coincidan
5. Hashea la contraseña con make_password()
6. Crea usuario en base de datos
7. Registra acción en auditoría

**Request:**
```json
{
    "username": "nuevo_usuario",
    "email": "usuario@email.com",
    "password": "password123",
    "confirm_password": "password123",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "role": "Ventas"
}
```

**Response Exitoso (201):**
```json
{
    "id": 26,
    "username": "nuevo_usuario",
    "email": "usuario@email.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "role": "Ventas",
    "is_active": true,
    "date_joined": "2025-08-11T15:30:00Z"
}
```

**Códigos de Error:**
- `400`: Datos inválidos o username duplicado
- `403`: Sin permisos

---

### 6. GET `/api/usuarios/{id}/`
**Descripción:** Obtener detalles de un usuario específico

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Busca usuario por ID
3. Serializa con UserSerializer

**Response Exitoso (200):**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "Administrador",
    "is_active": true,
    "date_joined": "2025-01-01T10:00:00Z"
}
```

**Códigos de Error:**
- `404`: Usuario no encontrado
- `403`: Sin permisos

---

### 7. PUT `/api/usuarios/{id}/`
**Descripción:** Actualizar usuario completo

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Valida todos los campos requeridos
3. Actualiza usuario en base de datos
4. Registra cambios en auditoría

**Request:**
```json
{
    "username": "usuario_actualizado",
    "email": "nuevo@email.com",
    "first_name": "Nuevo Nombre",
    "last_name": "Nuevo Apellido",
    "role": "Secretario"
}
```

**Códigos de Error:**
- `400`: Datos inválidos
- `403`: Sin permisos
- `404`: Usuario no encontrado

---

### 8. PATCH `/api/usuarios/{id}/`
**Descripción:** Actualizar campos específicos del usuario

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Valida solo campos proporcionados
3. Actualiza parcialmente el usuario
4. Registra cambios en auditoría

**Request:**
```json
{
    "role": "Bodega"
}
```

---

### 9. DELETE `/api/usuarios/{id}/`
**Descripción:** Eliminar usuario del sistema

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Verifica que no sea el último administrador
3. Elimina usuario de base de datos
4. Registra eliminación en auditoría

**Response Exitoso (204):** Sin contenido

**Códigos de Error:**
- `403`: Sin permisos o último admin
- `404`: Usuario no encontrado

---

### 10. POST `/api/usuarios/{id}/toggle_active/`
**Descripción:** Alternar estado activo/inactivo del usuario

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Obtiene usuario por ID
3. Invierte el valor de is_active
4. Guarda cambio en base de datos
5. Registra acción en auditoría

**Response Exitoso (200):**
```json
{
    "message": "Estado del usuario actualizado",
    "is_active": false
}
```

---

### 11. POST `/api/usuarios/{id}/change_role/`
**Descripción:** Cambiar el rol de un usuario

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Valida que el nuevo rol sea válido
3. Actualiza campo role del usuario
4. Registra cambio en auditoría

**Request:**
```json
{
    "role": "Administrador"
}
```

**Response Exitoso (200):**
```json
{
    "message": "Rol actualizado exitosamente",
    "role": "Administrador"
}
```

---

### 12. GET `/api/usuarios/roles/`
**Descripción:** Obtener lista de roles disponibles en el sistema

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Retorna lista estática de roles del sistema

**Response Exitoso (200):**
```json
{
    "roles": [
        {"value": "Administrador", "label": "Administrador"},
        {"value": "Ventas", "label": "Ventas"},
        {"value": "Secretario", "label": "Secretario"},
        {"value": "Bodega", "label": "Bodega"},
        {"value": "Pagos", "label": "Pagos"},
        {"value": "Cliente", "label": "Cliente"}
    ]
}
```

---

### 13. POST `/api/usuarios/{id}/eliminar-con-motivo/`
**Descripción:** Eliminar usuario registrando motivo en auditoría

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Registra motivo de eliminación en LogAuditoria
3. Elimina usuario de base de datos
4. Retorna confirmación

**Request:**
```json
{
    "motivo": "Usuario inactivo por más de 6 meses"
}
```

**Response Exitoso (200):**
```json
{
    "message": "Usuario eliminado exitosamente",
    "motivo": "Usuario inactivo por más de 6 meses"
}
```

---

### 14. POST `/api/usuarios/{id}/generar-token-permiso/`
**Descripción:** Generar token temporal para acciones que requieren autorización especial

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Genera token temporal con expiración
3. Asocia token con acción específica
4. Registra generación en auditoría

**Request:**
```json
{
    "accion": "eliminar_producto",
    "motivo": "Autorización especial para limpieza de inventario"
}
```

**Response Exitoso (200):**
```json
{
    "token": "temp_abc123def456",
    "expires_at": "2025-08-11T16:30:00Z",
    "accion": "eliminar_producto"
}
```

---

## 👨‍💼 Gestión de Clientes

### 15. GET `/api/clientes/`
**Descripción:** Listar todos los clientes

**Permisos:** Admin, Secretario, Ventas

**Flujo:**
1. Verifica permisos apropiados
2. Filtra usuarios con role='Cliente'
3. Aplica paginación
4. Serializa con ClienteSerializer

**Response Exitoso (200):**
```json
{
    "count": 11,
    "results": [
        {
            "id": 64,
            "username": "cliente1",
            "email": "cliente1@email.com",
            "nombre": "Cliente Uno",
            "telefono": "+1234567890",
            "is_active": true,
            "date_joined": "2025-01-01T10:00:00Z"
        }
    ]
}
```

---

### 16. POST `/api/clientes/`
**Descripción:** Crear nuevo cliente

**Permisos:** Solo Admin, Secretario

**Flujo:**
1. Verifica permisos apropiados
2. Valida datos con ClienteCreateSerializer
3. Establece role='Cliente' automáticamente
4. Crea usuario en base de datos
5. Registra creación en auditoría

**Request:**
```json
{
    "username": "cliente_nuevo",
    "email": "cliente@email.com",
    "nombre": "Juan Pérez",
    "telefono": "+1234567890"
}
```

**Response Exitoso (201):**
```json
{
    "id": 75,
    "username": "cliente_nuevo",
    "email": "cliente@email.com",
    "nombre": "Juan Pérez",
    "telefono": "+1234567890",
    "is_active": true,
    "date_joined": "2025-08-11T15:30:00Z"
}
```

---

### 17. GET `/api/clientes/{id}/`
**Descripción:** Obtener detalles de un cliente específico

**Permisos:** Admin, Secretario, Ventas

**Flujo:**
1. Verifica permisos apropiados
2. Busca cliente por ID
3. Verifica que sea role='Cliente'
4. Serializa con ClienteSerializer

---

### 18. PUT `/api/clientes/{id}/`
**Descripción:** Actualizar cliente completo

**Permisos:** Solo Admin, Secretario

**Flujo:**
1. Verifica permisos de edición
2. Valida todos los campos
3. Actualiza datos del cliente
4. Registra cambios en auditoría

---

### 19. PATCH `/api/clientes/{id}/`
**Descripción:** Actualizar campos específicos del cliente

**Permisos:** Solo Admin, Secretario

**Flujo:**
1. Verifica permisos de edición
2. Valida solo campos proporcionados
3. Actualiza parcialmente
4. Registra cambios en auditoría

---

### 20. DELETE `/api/clientes/{id}/`
**Descripción:** Eliminar cliente del sistema

**Permisos:** Solo Admin, Secretario

**Flujo:**
1. Verifica permisos de eliminación
2. Verifica que no tenga facturas pendientes
3. Elimina cliente de base de datos
4. Registra eliminación en auditoría

---

### 21. POST `/api/clientes/{id}/eliminar-con-motivo/`
**Descripción:** Eliminar cliente registrando motivo en auditoría

**Permisos:** Solo Admin, Secretario

**Flujo:**
1. Verifica permisos de eliminación
2. Registra motivo detallado en auditoría
3. Elimina cliente de base de datos

**Request:**
```json
{
    "motivo": "Cliente solicitó eliminación de datos personales"
}
```

---

### 22. POST `/api/cliente/register/`
**Descripción:** Registro público para nuevos clientes

**Permisos:** Público (sin autenticación)

**Flujo:**
1. No requiere autenticación
2. Valida datos de registro
3. Verifica que username sea único
4. Hashea contraseña
5. Establece role='Cliente'
6. Crea usuario en base de datos
7. Genera token automáticamente

**Request:**
```json
{
    "username": "cliente_autoregistro",
    "email": "autoregistro@email.com",
    "password": "password123",
    "nombre": "Cliente Autoregistro",
    "telefono": "+1234567890"
}
```

**Response Exitoso (201):**
```json
{
    "id": 76,
    "username": "cliente_autoregistro",
    "email": "autoregistro@email.com",
    "nombre": "Cliente Autoregistro",
    "telefono": "+1234567890",
    "token": "abc123def456ghi789"
}
```

---

### 23. GET `/api/cliente/me/`
**Descripción:** Obtener perfil del cliente autenticado

**Permisos:** Solo clientes autenticados

**Flujo:**
1. Valida token del cliente
2. Verifica que sea role='Cliente'
3. Serializa datos del perfil
4. Retorna información personal

**Headers Requeridos:**
```
Authorization: Token <cliente_token>
```

**Response Exitoso (200):**
```json
{
    "id": 64,
    "username": "cliente1",
    "email": "cliente1@email.com",
    "nombre": "Cliente Uno",
    "telefono": "+1234567890",
    "facturas_count": 3,
    "facturas_pendientes": 1
}
```

---

## 📦 Gestión de Productos

### 24. GET `/api/productos/`
**Descripción:** Listar todos los productos

**Permisos:** Admin, Bodega, Ventas

**Flujo:**
1. Verifica permisos apropiados
2. Obtiene todos los productos
3. Aplica filtros si se proporcionan
4. Serializa con ProductoSerializer

**Response Exitoso (200):**
```json
{
    "count": 50,
    "results": [
        {
            "id": 1,
            "nombre": "Producto Ejemplo",
            "descripcion": "Descripción del producto",
            "precio": 25.99,
            "stock": 100,
            "categoria": "Electrónicos",
            "fecha_creacion": "2025-01-01T10:00:00Z",
            "is_active": true
        }
    ]
}
```

---

### 25. POST `/api/productos/`
**Descripción:** Crear nuevo producto

**Permisos:** Solo Admin, Bodega

**Flujo:**
1. Verifica permisos de creación
2. Valida datos con ProductoSerializer
3. Verifica que nombre sea único
4. Crea producto en base de datos
5. Registra creación en auditoría

**Request:**
```json
{
    "nombre": "Producto Nuevo",
    "descripcion": "Descripción del producto",
    "precio": 25.99,
    "stock": 100,
    "categoria": "Electrónicos"
}
```

---

### 26. GET `/api/productos/{id}/`
**Descripción:** Obtener detalles de un producto específico

**Permisos:** Admin, Bodega, Ventas

**Flujo:**
1. Verifica permisos de lectura
2. Busca producto por ID
3. Serializa con ProductoSerializer

---

### 27. PUT `/api/productos/{id}/`
**Descripción:** Actualizar producto completo

**Permisos:** Solo Admin, Bodega

**Flujo:**
1. Verifica permisos de edición
2. Valida todos los campos
3. Actualiza producto en base de datos
4. Registra cambios en auditoría

---

### 28. PATCH `/api/productos/{id}/`
**Descripción:** Actualizar campos específicos del producto

**Permisos:** Solo Admin, Bodega

**Flujo:**
1. Verifica permisos de edición
2. Valida solo campos proporcionados
3. Actualiza parcialmente
4. Registra cambios en auditoría

---

### 29. DELETE `/api/productos/{id}/`
**Descripción:** Eliminar producto del sistema

**Permisos:** Solo Admin, Bodega

**Flujo:**
1. Verifica permisos de eliminación
2. Verifica que no esté en facturas activas
3. Elimina producto de base de datos
4. Registra eliminación en auditoría

---

### 30. POST `/api/productos/{id}/eliminar-con-motivo/`
**Descripción:** Eliminar producto registrando motivo en auditoría

**Permisos:** Solo Admin, Bodega

**Flujo:**
1. Verifica permisos de eliminación
2. Registra motivo detallado en auditoría
3. Elimina producto de base de datos

**Request:**
```json
{
    "motivo": "Producto descontinuado por el fabricante"
}
```

---

## 🧾 Gestión de Facturas

### 31. GET `/api/facturas/`
**Descripción:** Listar todas las facturas

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos de lectura
2. Obtiene todas las facturas
3. Aplica filtros por estado, fecha, cliente
4. Serializa con FacturaSerializer

**Response Exitoso (200):**
```json
{
    "count": 22,
    "results": [
        {
            "id": 27,
            "numero": "FAC-000027",
            "cliente": {
                "id": 64,
                "nombre": "Cliente Uno"
            },
            "fecha_emision": "2025-08-11T10:00:00Z",
            "estado": "EMITIDA",
            "total": 150.00,
            "items": [
                {
                    "producto": {
                        "id": 1,
                        "nombre": "Producto Ejemplo"
                    },
                    "cantidad": 2,
                    "precio_unitario": 75.00,
                    "subtotal": 150.00
                }
            ]
        }
    ]
}
```

---

### 32. POST `/api/facturas/`
**Descripción:** Crear nueva factura

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos de creación
2. Valida datos con FacturaCreateSerializer
3. Verifica existencia de cliente y productos
4. Calcula totales automáticamente
5. Establece estado='BORRADOR'
6. Crea factura e items en base de datos
7. Registra creación en auditoría

**Request:**
```json
{
    "cliente": 64,
    "items": [
        {
            "producto": 1,
            "cantidad": 2
        }
    ],
    "estado": "BORRADOR"
}
```

**Response Exitoso (201):**
```json
{
    "id": 28,
    "numero": "FAC-000028",
    "cliente": {
        "id": 64,
        "nombre": "Cliente Uno"
    },
    "fecha_emision": "2025-08-11T15:30:00Z",
    "estado": "BORRADOR",
    "total": 150.00,
    "items": [...]
}
```

---

### 33. GET `/api/facturas/{id}/`
**Descripción:** Obtener detalles de una factura específica

**Permisos:** Admin, Ventas, Cliente (solo propias)

**Flujo:**
1. Verifica permisos de lectura
2. Si es cliente, verifica que la factura le pertenezca
3. Busca factura por ID
4. Serializa con FacturaDetailSerializer

---

### 34. PUT `/api/facturas/{id}/`
**Descripción:** Actualizar factura completa

**Permisos:** Admin, Ventas (solo BORRADOR)

**Flujo:**
1. Verifica permisos de edición
2. Verifica que estado sea 'BORRADOR'
3. Valida todos los campos
4. Actualiza factura e items
5. Recalcula totales
6. Registra cambios en auditoría

---

### 35. PATCH `/api/facturas/{id}/`
**Descripción:** Actualizar campos específicos de la factura

**Permisos:** Admin, Ventas (solo BORRADOR)

**Flujo:**
1. Verifica permisos de edición
2. Verifica que estado sea 'BORRADOR'
3. Valida solo campos proporcionados
4. Actualiza parcialmente
5. Registra cambios en auditoría

---

### 36. DELETE `/api/facturas/{id}/`
**Descripción:** Eliminar factura

**Permisos:** Solo Admin, Ventas (solo BORRADOR, solo creador/admin)

**Flujo:**
1. Verifica permisos de eliminación
2. Verifica que estado sea 'BORRADOR'
3. Verifica que usuario sea creador o admin
4. Elimina factura e items de base de datos
5. Registra eliminación en auditoría

---

### 37. POST `/api/facturas/{id}/emitir/`
**Descripción:** Emitir factura (BORRADOR → EMITIDA)

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos de emisión
2. Verifica que estado sea 'BORRADOR'
3. Valida que hay stock suficiente para todos los productos
4. Descuenta stock de productos automáticamente
5. Cambia estado a 'EMITIDA'
6. Establece fecha_emision
7. Registra emisión en auditoría

**Response Exitoso (200):**
```json
{
    "message": "Factura emitida exitosamente",
    "numero": "FAC-000027",
    "estado": "EMITIDA",
    "fecha_emision": "2025-08-11T15:30:00Z"
}
```

**Códigos de Error:**
- `400`: Stock insuficiente o estado inválido

---

### 38. POST `/api/facturas/{id}/marcar_pagada/`
**Descripción:** Marcar factura como pagada (EMITIDA → PAGADA)

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos apropiados
2. Verifica que estado sea 'EMITIDA'
3. Cambia estado a 'PAGADA'
4. Establece fecha_pago
5. Registra pago en auditoría

**Response Exitoso (200):**
```json
{
    "message": "Factura marcada como pagada",
    "estado": "PAGADA",
    "fecha_pago": "2025-08-11T15:30:00Z"
}
```

---

### 39. POST `/api/facturas/{id}/anular/`
**Descripción:** Anular factura (restituir stock automáticamente)

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos de anulación
2. Verifica que estado sea 'EMITIDA' o 'PAGADA'
3. Restituye stock de productos automáticamente
4. Cambia estado a 'ANULADA'
5. Establece fecha_anulacion
6. Registra anulación en auditoría

**Response Exitoso (200):**
```json
{
    "message": "Factura anulada exitosamente",
    "estado": "ANULADA",
    "fecha_anulacion": "2025-08-11T15:30:00Z",
    "stock_restituido": true
}
```

---

### 40. POST `/api/facturas/{id}/send_pdf/`
**Descripción:** Enviar PDF de la factura por correo electrónico al cliente

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos de envío
2. Verifica que factura esté EMITIDA o PAGADA
3. Genera PDF de la factura
4. Envía email al cliente con PDF adjunto
5. Registra envío en auditoría

**Response Exitoso (200):**
```json
{
    "message": "PDF enviado exitosamente",
    "email": "cliente1@email.com",
    "fecha_envio": "2025-08-11T15:30:00Z"
}
```

---

### 41. GET `/api/facturas/{id}/view-pdf/`
**Descripción:** Visualizar PDF de la factura en el navegador

**Permisos:** Admin/Ventas (todas), Clientes (solo propias)

**Flujo:**
1. Verifica permisos de visualización
2. Si es cliente, verifica que la factura le pertenezca
3. Genera PDF con ReportLab
4. Retorna PDF con Content-Type: application/pdf
5. Header Content-Disposition: inline (mostrar en navegador)

**Headers de Respuesta:**
```
Content-Type: application/pdf
Content-Disposition: inline; filename="Factura_FAC-000027.pdf"
```

**Códigos de Error:**
- `403`: Sin permisos para ver esta factura
- `404`: Factura no encontrada

---

### 42. GET `/api/facturas/{id}/download-pdf/`
**Descripción:** Descargar PDF de la factura

**Permisos:** Admin/Ventas (todas), Clientes (solo propias)

**Flujo:**
1. Verifica permisos de descarga
2. Si es cliente, verifica que la factura le pertenezca
3. Genera PDF con ReportLab
4. Retorna PDF con Content-Disposition: attachment
5. Fuerza descarga del archivo

**Headers de Respuesta:**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="Factura_FAC-000027.pdf"
```

---

### 43. GET `/api/facturas/metrics/`
**Descripción:** Obtener métricas y estadísticas de facturas

**Permisos:** Admin, Ventas

**Flujo:**
1. Verifica permisos de métricas
2. Calcula estadísticas de los últimos 7 días
3. Agrupa por estado, fecha, cliente
4. Retorna métricas consolidadas

**Response Exitoso (200):**
```json
{
    "periodo": "últimos_7_días",
    "total_facturas": 22,
    "por_estado": {
        "BORRADOR": 3,
        "EMITIDA": 8,
        "PAGADA": 10,
        "ANULADA": 1
    },
    "ventas_totales": 15750.00,
    "promedio_por_factura": 715.91,
    "cliente_mas_activo": {
        "id": 64,
        "nombre": "Cliente Uno",
        "facturas": 5
    }
}
```

---

### 44. POST `/api/facturas/{id}/eliminar-con-motivo/`
**Descripción:** Eliminar factura registrando motivo en auditoría

**Permisos:** Solo Admin

**Flujo:**
1. Verifica permisos de administrador
2. Verifica que estado sea 'BORRADOR'
3. Registra motivo detallado en auditoría
4. Elimina factura e items de base de datos

**Request:**
```json
{
    "motivo": "Factura creada por error"
}
```

---

### 45. GET `/api/facturas/cliente/`
**Descripción:** Obtener facturas del cliente autenticado

**Permisos:** Solo clientes autenticados

**Flujo:**
1. Valida token del cliente
2. Verifica que sea role='Cliente'
3. Filtra facturas donde cliente = usuario_autenticado
4. Aplica filtros por estado si se proporcionan
5. Serializa con FacturaClienteSerializer

**Headers Requeridos:**
```
Authorization: Token <cliente_token>
```

**Response Exitoso (200):**
```json
{
    "count": 3,
    "results": [
        {
            "id": 27,
            "numero": "FAC-000027",
            "fecha_emision": "2025-08-11T10:00:00Z",
            "estado": "EMITIDA",
            "total": 150.00,
            "puede_descargar_pdf": true
        }
    ]
}
```

---

## 💳 Gestión de Pagos

### 46. GET `/api/pagos/`
**Descripción:** Listar todos los pagos

**Permisos:** Admin, Pagos

**Flujo:**
1. Verifica permisos apropiados
2. Obtiene todos los pagos del sistema
3. Aplica filtros por estado, fecha, factura
4. Serializa con PagoSerializer

**Response Exitoso (200):**
```json
{
    "count": 15,
    "results": [
        {
            "id": 1,
            "factura": {
                "id": 27,
                "numero": "FAC-000027"
            },
            "monto": 150.00,
            "tipo_pago": "transferencia",
            "comprobante": "TRANS123456",
            "estado": "PENDIENTE",
            "fecha_pago": "2025-08-11T10:00:00Z",
            "observaciones": "Pago por transferencia bancaria"
        }
    ]
}
```

---

### 47. POST `/api/pagos/`
**Descripción:** Crear nuevo pago

**Permisos:** Admin, Pagos

**Flujo:**
1. Verifica permisos de creación
2. Valida datos con PagoCreateSerializer
3. Verifica que factura exista y esté EMITIDA
4. Establece estado='PENDIENTE'
5. Crea pago en base de datos
6. Registra creación en auditoría

**Request:**
```json
{
    "factura": 27,
    "monto": 150.00,
    "tipo_pago": "transferencia",
    "comprobante": "TRANS123456",
    "observaciones": "Pago por transferencia bancaria"
}
```

**Response Exitoso (201):**
```json
{
    "id": 16,
    "factura": {
        "id": 27,
        "numero": "FAC-000027"
    },
    "monto": 150.00,
    "tipo_pago": "transferencia",
    "comprobante": "TRANS123456",
    "estado": "PENDIENTE",
    "fecha_pago": "2025-08-11T15:30:00Z"
}
```

---

### 48. GET `/api/pagos/{id}/`
**Descripción:** Obtener detalles de un pago específico

**Permisos:** Admin, Pagos

**Flujo:**
1. Verifica permisos de lectura
2. Busca pago por ID
3. Serializa con PagoDetailSerializer

---

### 49. PUT `/api/pagos/{id}/`
**Descripción:** Actualizar pago completo

**Permisos:** Admin, Pagos (solo PENDIENTE)

**Flujo:**
1. Verifica permisos de edición
2. Verifica que estado sea 'PENDIENTE'
3. Valida todos los campos
4. Actualiza pago en base de datos
5. Registra cambios en auditoría

---

### 50. DELETE `/api/pagos/{id}/`
**Descripción:** Eliminar pago del sistema

**Permisos:** Admin, Pagos (solo PENDIENTE)

**Flujo:**
1. Verifica permisos de eliminación
2. Verifica que estado sea 'PENDIENTE'
3. Elimina pago de base de datos
4. Registra eliminación en auditoría

---

### 51. GET `/api/pagos/pendientes/`
**Descripción:** Listar solo pagos pendientes de validación

**Permisos:** Admin, Pagos

**Flujo:**
1. Verifica permisos de lectura
2. Filtra pagos con estado='PENDIENTE'
3. Ordena por fecha_pago descendente
4. Serializa con PagoPendienteSerializer

**Response Exitoso (200):**
```json
{
    "count": 5,
    "results": [
        {
            "id": 16,
            "factura": {
                "id": 27,
                "numero": "FAC-000027",
                "cliente": "Cliente Uno"
            },
            "monto": 150.00,
            "tipo_pago": "transferencia",
            "comprobante": "TRANS123456",
            "fecha_pago": "2025-08-11T15:30:00Z",
            "dias_pendiente": 1
        }
    ]
}
```

---

### 52. POST `/api/pagos/{id}/validar/`
**Descripción:** Validar pago (aprobar o rechazar)

**Permisos:** Solo Admin, Pagos

**Flujo:**
1. Verifica permisos de validación
2. Verifica que estado sea 'PENDIENTE'
3. Valida acción ('aprobar' o 'rechazar')
4. Si aprobar:
   - Cambia estado a 'APROBADO'
   - Marca factura como PAGADA automáticamente
5. Si rechazar:
   - Cambia estado a 'RECHAZADO'
   - Mantiene factura como EMITIDA
6. Registra validación en auditoría

**Request:**
```json
{
    "accion": "aprobar",
    "motivo": "Comprobante verificado correctamente"
}
```

**Response Exitoso (200):**
```json
{
    "message": "Pago aprobado exitosamente",
    "estado": "APROBADO",
    "factura_actualizada": true,
    "motivo": "Comprobante verificado correctamente"
}
```

**Códigos de Error:**
- `400`: Acción inválida o estado incorrecto

---

### 53. GET `/api/pagos/estadisticas/`
**Descripción:** Obtener estadísticas generales de pagos

**Permisos:** Admin, Pagos

**Flujo:**
1. Verifica permisos de estadísticas
2. Calcula métricas de pagos por período
3. Agrupa por estado, tipo_pago, mes
4. Retorna estadísticas consolidadas

**Response Exitoso (200):**
```json
{
    "total_pagos": 15,
    "por_estado": {
        "PENDIENTE": 5,
        "APROBADO": 8,
        "RECHAZADO": 2
    },
    "por_tipo": {
        "efectivo": 6,
        "transferencia": 7,
        "tarjeta": 2
    },
    "monto_total_aprobado": 12500.00,
    "promedio_por_pago": 833.33,
    "tiempo_promedio_validacion": "2.3 días"
}
```

---

### 54. POST `/api/cliente/registrar-pago/`
**Descripción:** Registrar nuevo pago como cliente autenticado

**Permisos:** Solo clientes autenticados

**Flujo:**
1. Valida token del cliente
2. Verifica que sea role='Cliente'
3. Valida que factura pertenezca al cliente
4. Verifica que factura esté EMITIDA
5. Crea pago con estado='PENDIENTE'
6. Registra en auditoría

**Headers Requeridos:**
```
Authorization: Token <cliente_token>
```

**Request:**
```json
{
    "factura": 27,
    "monto": 150.00,
    "tipo_pago": "efectivo",
    "comprobante": "EF123456",
    "observaciones": "Pago en efectivo"
}
```

**Response Exitoso (201):**
```json
{
    "id": 17,
    "factura": {
        "id": 27,
        "numero": "FAC-000027"
    },
    "monto": 150.00,
    "tipo_pago": "efectivo",
    "estado": "PENDIENTE",
    "mensaje": "Pago registrado. Pendiente de validación."
}
```

---

### 55. GET `/api/cliente/mis-pagos/`
**Descripción:** Ver mis propios pagos como cliente autenticado

**Permisos:** Solo clientes autenticados

**Flujo:**
1. Valida token del cliente
2. Verifica que sea role='Cliente'
3. Filtra pagos donde factura.cliente = usuario_autenticado
4. Serializa con PagoClienteSerializer

**Response Exitoso (200):**
```json
{
    "count": 3,
    "results": [
        {
            "id": 17,
            "factura": {
                "id": 27,
                "numero": "FAC-000027"
            },
            "monto": 150.00,
            "tipo_pago": "efectivo",
            "estado": "PENDIENTE",
            "fecha_pago": "2025-08-11T15:30:00Z"
        }
    ]
}
```

---

### 56. GET `/api/cliente/facturas-pendientes/`
**Descripción:** Ver facturas pendientes de pago como cliente autenticado

**Permisos:** Solo clientes autenticados

**Flujo:**
1. Valida token del cliente
2. Verifica que sea role='Cliente'
3. Filtra facturas donde:
   - cliente = usuario_autenticado
   - estado = 'EMITIDA'
   - sin pagos aprobados
4. Serializa con FacturaPendienteSerializer

**Response Exitoso (200):**
```json
{
    "count": 2,
    "results": [
        {
            "id": 28,
            "numero": "FAC-000028",
            "fecha_emision": "2025-08-11T15:30:00Z",
            "total": 200.00,
            "dias_vencida": 5,
            "puede_pagar": true
        }
    ]
}
```

---

## 📋 Auditorías y Logs

### 57. GET `/api/logs/`
**Descripción:** Listar todos los registros de auditoría

**Permisos:** Admin, Solo lectura

**Flujo:**
1. Verifica permisos de administrador
2. Obtiene todos los logs de auditoría
3. Aplica filtros por fecha, usuario, acción
4. Ordena por fecha descendente
5. Serializa con LogAuditoriaSerializer

**Response Exitoso (200):**
```json
{
    "count": 150,
    "results": [
        {
            "id": 1,
            "usuario": {
                "id": 1,
                "username": "admin"
            },
            "accion": "CREAR_FACTURA",
            "modelo": "Factura",
            "objeto_id": 27,
            "descripcion": "Factura FAC-000027 creada",
            "ip_address": "127.0.0.1",
            "timestamp": "2025-08-11T15:30:00Z",
            "detalles": {
                "cliente_id": 64,
                "total": 150.00
            }
        }
    ]
}
```

---

### 58. GET `/api/logs/{id}/`
**Descripción:** Obtener detalles de un registro de auditoría específico

**Permisos:** Solo Administradores

**Flujo:**
1. Verifica permisos de administrador
2. Busca log por ID
3. Serializa con LogAuditoriaDetailSerializer

**Response Exitoso (200):**
```json
{
    "id": 1,
    "usuario": {
        "id": 1,
        "username": "admin",
        "full_name": "Admin User"
    },
    "accion": "CREAR_FACTURA",
    "modelo": "Factura",
    "objeto_id": 27,
    "descripcion": "Factura FAC-000027 creada",
    "ip_address": "127.0.0.1",
    "user_agent": "PostmanRuntime/7.28.4",
    "timestamp": "2025-08-11T15:30:00Z",
    "detalles": {
        "cliente_id": 64,
        "total": 150.00,
        "items_count": 2
    }
}
```

---

## 📖 Documentación

### 59. GET `/api/docs/`
**Descripción:** Obtener documentación completa de todos los endpoints

**Permisos:** Usuarios autenticados

**Flujo:**
1. Valida autenticación del usuario
2. Genera documentación dinámica de todos los endpoints
3. Incluye ejemplos de request/response
4. Agrupa por módulos

**Response Exitoso (200):**
```json
{
    "version": "1.0",
    "base_url": "http://localhost:8000",
    "authentication": "Token-based",
    "modules": {
        "usuarios": {
            "endpoints": [...],
            "permissions": ["Administrador"]
        },
        "clientes": {
            "endpoints": [...],
            "permissions": ["Admin", "Secretario", "Ventas"]
        },
        "productos": {
            "endpoints": [...],
            "permissions": ["Admin", "Bodega", "Ventas"]
        },
        "facturas": {
            "endpoints": [...],
            "permissions": ["Admin", "Ventas", "Cliente"]
        },
        "pagos": {
            "endpoints": [...],
            "permissions": ["Admin", "Pagos", "Cliente"]
        }
    }
}
```

---

### 60. GET `/api/pagos/docs/`
**Descripción:** Obtener documentación específica del módulo de pagos

**Permisos:** Admin, Pagos

**Flujo:**
1. Verifica permisos apropiados
2. Genera documentación detallada del flujo de pagos
3. Incluye diagramas de estado
4. Explica proceso de validación

**Response Exitoso (200):**
```json
{
    "module": "pagos",
    "description": "Módulo de gestión y validación de pagos",
    "workflow": {
        "cliente_registra": "Cliente registra pago → PENDIENTE",
        "admin_valida": "Admin/Pagos valida → APROBADO/RECHAZADO",
        "factura_actualiza": "Si aprobado → Factura PAGADA"
    },
    "estados": [
        {"value": "PENDIENTE", "description": "Pago registrado, pendiente validación"},
        {"value": "APROBADO", "description": "Pago validado y aprobado"},
        {"value": "RECHAZADO", "description": "Pago rechazado por invalidez"}
    ],
    "endpoints": [...],
    "business_rules": [
        "Solo se pueden aprobar pagos PENDIENTES",
        "Pago aprobado marca factura como PAGADA automáticamente",
        "Clientes solo ven sus propios pagos"
    ]
}
```

---

## 🔒 Notas de Seguridad

### Control de Acceso
- **Autenticación:** Todos los endpoints requieren token válido (excepto registro público)
- **Autorización:** Verificación de roles en cada endpoint
- **Ownership:** Clientes solo acceden a sus propios recursos

### Auditoría
- **Logs Automáticos:** Todas las acciones se registran en LogAuditoria
- **Trazabilidad:** IP, user agent, timestamp de cada operación
- **Integridad:** Logs son solo de lectura después de creación

### Validaciones de Negocio
- **Stock:** Verificación automática antes de emitir facturas
- **Estados:** Transiciones de estado controladas y validadas
- **Permisos:** Verificación multinivel (autenticación + autorización + ownership)

### PDF Security
- **Access Control:** Clientes solo ven PDFs de sus facturas
- **Content-Type:** Configuración correcta para evitar ataques XSS
- **File Handling:** Generación dinámica sin almacenamiento permanente

---

## 📊 Códigos de Estado HTTP

### Exitosos
- **200:** OK - Operación exitosa
- **201:** Created - Recurso creado exitosamente
- **204:** No Content - Eliminación exitosa

### Errores del Cliente
- **400:** Bad Request - Datos inválidos
- **401:** Unauthorized - Token inválido o ausente
- **403:** Forbidden - Sin permisos para la operación
- **404:** Not Found - Recurso no encontrado

### Errores del Servidor
- **500:** Internal Server Error - Error interno del servidor

---

## 🚀 Optimizaciones Implementadas

### Performance
- **Paginación:** Todos los listados paginados automáticamente
- **Select Related:** Optimización de consultas con relaciones
- **Prefetch Related:** Carga eficiente de relaciones múltiples

### Caching
- **QuerySet Caching:** Cache de consultas frecuentes
- **Static Files:** Configuración para archivos estáticos

### Database
- **Indexes:** Índices en campos de búsqueda frecuente
- **Transactions:** Operaciones atómicas para consistencia

---

*Documento generado el 11 de agosto de 2025*  
*Sistema de Facturación Segura v1.0*
