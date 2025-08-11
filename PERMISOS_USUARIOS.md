# 🔐 RESUMEN COMPLETO DE PERMISOS POR TIPO DE USUARIO

## 👥 TIPOS DE USUARIOS EN EL SISTEMA

### 1. **SUPERUSUARIO (Django)**
- ✅ **Acceso total sin restricciones**
- ✅ Puede hacer todo en todos los módulos
- ✅ Bypass de todos los permisos personalizados

### 2. **ADMINISTRADOR**
- ✅ **Acceso completo a todos los módulos**
- ✅ Gestión de usuarios (CRUD)
- ✅ Gestión de clientes (CRUD)
- ✅ Gestión de productos (CRUD)
- ✅ Gestión de facturas (CRUD)
- ✅ Gestión de pagos (CRUD)
- ✅ Validación y aprobación de pagos
- ✅ Acceso a logs de auditoría
- ✅ Generación de tokens para clientes

### 3. **SECRETARIO**
- ✅ Gestión de clientes (CRUD)
- ❌ No acceso a productos
- ❌ No acceso a facturas
- ❌ No acceso a pagos
- ❌ No acceso a usuarios

### 4. **BODEGA**
- ✅ Gestión de productos (CRUD)
- ❌ No acceso a clientes
- ❌ No acceso a facturas
- ❌ No acceso a pagos
- ❌ No acceso a usuarios

### 5. **VENTAS**
- ✅ Consulta de clientes (solo lectura)
- ✅ Consulta de productos (solo lectura)
- ✅ Gestión de facturas (CRUD)
- ❌ No acceso a pagos
- ❌ No acceso a usuarios
- ❌ No puede modificar clientes o productos

### 6. **PAGOS**
- ✅ Gestión de pagos (CRUD)
- ✅ Validación y aprobación de pagos
- ✅ Consulta de pagos pendientes
- ❌ No acceso a clientes
- ❌ No acceso a productos
- ❌ No acceso a facturas
- ❌ No acceso a usuarios

### 7. **CLIENTE** (Nuevos usuarios clientes)
- ✅ Consulta de sus propios datos
- ✅ Consulta de sus propias facturas
- ✅ Registro de pagos propios
- ✅ Consulta de sus propios pagos
- ❌ No acceso a datos de otros clientes
- ❌ No acceso a funciones administrativas

---

## 📋 PERMISOS DETALLADOS POR MÓDULO

### 🏢 **MÓDULO CLIENTES** (`/api/clientes/`)

| Rol | GET (Consulta) | POST (Crear) | PUT (Editar) | DELETE (Eliminar) |
|-----|---------------|--------------|--------------|-------------------|
| **Administrador** | ✅ | ✅ | ✅ | ✅ |
| **Secretario** | ✅ | ✅ | ✅ | ✅ |
| **Ventas** | ✅ (solo lectura) | ❌ | ❌ | ❌ |
| **Bodega** | ❌ | ❌ | ❌ | ❌ |
| **Pagos** | ❌ | ❌ | ❌ | ❌ |
| **Cliente** | ❌* | ❌ | ❌ | ❌ |

*Los clientes solo pueden acceder a `/api/cliente/me/` para sus propios datos.

### 📦 **MÓDULO PRODUCTOS** (`/api/productos/`)

| Rol | GET (Consulta) | POST (Crear) | PUT (Editar) | DELETE (Eliminar) |
|-----|---------------|--------------|--------------|-------------------|
| **Administrador** | ✅ | ✅ | ✅ | ✅ |
| **Bodega** | ✅ | ✅ | ✅ | ✅ |
| **Ventas** | ✅ (solo lectura) | ❌ | ❌ | ❌ |
| **Secretario** | ❌ | ❌ | ❌ | ❌ |
| **Pagos** | ❌ | ❌ | ❌ | ❌ |
| **Cliente** | ❌ | ❌ | ❌ | ❌ |

### 🧾 **MÓDULO FACTURAS** (`/api/facturas/`)

| Rol | GET (Consulta) | POST (Crear) | PUT (Editar) | DELETE (Eliminar) |
|-----|---------------|--------------|--------------|-------------------|
| **Administrador** | ✅ | ✅ | ✅ | ✅ |
| **Ventas** | ✅ | ✅ | ✅ | ✅ |
| **Secretario** | ❌ | ❌ | ❌ | ❌ |
| **Bodega** | ❌ | ❌ | ❌ | ❌ |
| **Pagos** | ❌ | ❌ | ❌ | ❌ |
| **Cliente** | ✅* | ❌ | ❌ | ❌ |

*Los clientes solo pueden ver sus propias facturas mediante `/api/clientes/facturas/`.

### 💰 **MÓDULO PAGOS** (`/api/pagos/`)

| Rol | GET (Consulta) | POST (Crear) | PUT (Editar) | DELETE (Eliminar) | Validar |
|-----|---------------|--------------|--------------|-------------------|---------|
| **Administrador** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Pagos** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Ventas** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Secretario** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Bodega** | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Cliente** | ✅* | ✅* | ❌ | ❌ | ❌ |

*Los clientes solo pueden:
- Consultar sus propios pagos: `/api/pagos/mis-pagos/`
- Registrar pagos para sus facturas: `/api/pagos/registrar-cliente/`

### 👤 **MÓDULO USUARIOS** (`/api/usuarios/`)

| Rol | GET (Consulta) | POST (Crear) | PUT (Editar) | DELETE (Eliminar) |
|-----|---------------|--------------|--------------|-------------------|
| **Administrador** | ✅ | ✅ | ✅ | ✅ |
| **Secretario** | ❌ | ❌ | ❌ | ❌ |
| **Ventas** | ❌ | ❌ | ❌ | ❌ |
| **Bodega** | ❌ | ❌ | ❌ | ❌ |
| **Pagos** | ❌ | ❌ | ❌ | ❌ |
| **Cliente** | ❌ | ❌ | ❌ | ❌ |

### 📊 **MÓDULO AUDITORÍAS** (`/api/logs/`)

| Rol | GET (Consulta) | POST (Crear) | PUT (Editar) | DELETE (Eliminar) |
|-----|---------------|--------------|--------------|-------------------|
| **Todos los usuarios autenticados** | ✅ | ❌ | ❌ | ❌ |

---

## 🔑 **ENDPOINTS DE AUTENTICACIÓN**

### Para **USUARIOS DEL SISTEMA**:
- `POST /api/token/` - Login estándar (username/password)
- `GET /api/me/` - Datos del usuario autenticado
- `POST /api/auth/login/` - Login mejorado con más información
- `POST /api/auth/validate-password/` - Validar contraseña

### Para **CLIENTES**:
- `POST /api/cliente/register/` - Registro de nuevos clientes
- `POST /api/token/` - Login estándar (mismo endpoint que usuarios)
- `GET /api/cliente/me/` - Datos del cliente autenticado

---

## 🛡️ **FUNCIONES ESPECIALES POR ROL**

### **ADMINISTRADOR ESPECÍFICO**:
- ✅ Generar tokens para clientes: `POST /clientes/<id>/generar-token/`
- ✅ Acceso al panel de administración Django
- ✅ Validar y aprobar/rechazar pagos
- ✅ Gestión completa de usuarios

### **PAGOS ESPECÍFICO**:
- ✅ Validar pagos pendientes
- ✅ Aprobar/rechazar pagos con notificaciones por email
- ✅ Consultar estadísticas de pagos
- ✅ Acceso a dashboard de pagos

### **VENTAS ESPECÍFICO**:
- ✅ Crear facturas para clientes
- ✅ Consultar información de productos para ventas
- ✅ Consultar información de clientes para ventas
- ❌ No puede modificar productos ni clientes

### **CLIENTE ESPECÍFICO**:
- ✅ Registrar pagos con comprobantes
- ✅ Recibir notificaciones por email sobre estado de pagos
- ✅ Consultar historial de facturas y pagos propios
- 🔒 Acceso completamente aislado (solo sus datos)

---

## 🔒 **VALIDACIONES DE SEGURIDAD**

### **Validación de Rol**:
```python
# Cada endpoint valida el rol del usuario
if not hasattr(user, 'role') or user.role != 'ExpectedRole':
    return 403 Forbidden
```

### **Aislamiento de Datos**:
```python
# Los clientes solo ven sus propios datos
facturas = Factura.objects.filter(cliente=request.user)
pagos = Pago.objects.filter(pagado_por=request.user)
```

### **Autenticación Estándar**:
```python
# Sistema unificado para usuarios y clientes
Authorization: Token <token_from_api_token_endpoint>
```

---

## 📱 **COMPATIBILIDAD CON FRONTEND**

### **Headers Requeridos**:
```javascript
headers: {
  'Authorization': `Token ${token}`,
  'Content-Type': 'application/json'
}
```

### **Flujo de Autenticación**:
1. **Login** → `POST /api/token/`
2. **Obtener token** → Guardar en localStorage/cookies
3. **Requests autenticados** → Incluir header Authorization
4. **Validar permisos** → Backend valida rol automáticamente

Este sistema garantiza que cada tipo de usuario tenga acceso únicamente a las funcionalidades que corresponden a su rol, manteniendo la seguridad y separación de responsabilidades.
