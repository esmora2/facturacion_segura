# 🔐 Actualización de Permisos - Personal de Ventas

## 📋 Resumen de Cambios

Se ha actualizado el sistema de permisos para permitir que el **personal de Ventas** tenga acceso de **solo lectura** a los módulos de **Clientes** y **Productos**, necesario para crear facturas.

## ✅ Cambios Implementados

### 1. Permisos Actualizados

#### 👨‍💼 Módulo de Clientes (`/api/clientes/`)
- **Administrador**: Acceso completo (CRUD)
- **Secretario**: Acceso completo (CRUD)
- **Ventas**: ✨ **Solo lectura** (GET) - ¡NUEVO!

#### 📦 Módulo de Productos (`/api/productos/`)
- **Administrador**: Acceso completo (CRUD)
- **Bodega**: Acceso completo (CRUD)
- **Ventas**: ✨ **Solo lectura** (GET) - ¡NUEVO!

#### 🧾 Módulo de Facturación (`/api/facturas/`)
- **Administrador**: Acceso completo
- **Ventas**: Acceso completo (como antes)

### 2. Archivos Modificados

```
apps/usuarios/permissions.py
├── ClientePermission (actualizada)
└── ProductoPermission (actualizada)

apps/clientes/views_api.py
└── ClienteViewSet (actualizada)

apps/productos/views_api.py
└── ProductoViewSet (actualizada)
```

## 🚀 Comportamiento del Personal de Ventas

### ✅ Lo que PUEDEN hacer:

```bash
# Listar todos los clientes
GET /api/clientes/
# Respuesta: 200 OK con lista de clientes

# Ver detalles de un cliente específico
GET /api/clientes/{id}/
# Respuesta: 200 OK con datos del cliente

# Listar todos los productos
GET /api/productos/
# Respuesta: 200 OK con lista de productos

# Ver detalles de un producto específico
GET /api/productos/{id}/
# Respuesta: 200 OK con datos del producto

# Crear, actualizar, eliminar facturas (sin cambios)
POST /api/facturas/
PUT /api/facturas/{id}/
DELETE /api/facturas/{id}/
```

### ❌ Lo que NO pueden hacer:

```bash
# Crear cliente
POST /api/clientes/
# Respuesta: 403 Forbidden - "El personal de Ventas solo puede consultar información de clientes (solo lectura)"

# Actualizar cliente
PUT /api/clientes/{id}/
PATCH /api/clientes/{id}/
# Respuesta: 403 Forbidden

# Eliminar cliente
DELETE /api/clientes/{id}/
# Respuesta: 403 Forbidden

# Crear producto
POST /api/productos/
# Respuesta: 403 Forbidden - "El personal de Ventas solo puede consultar información de productos (solo lectura)"

# Actualizar producto
PUT /api/productos/{id}/
PATCH /api/productos/{id}/
# Respuesta: 403 Forbidden

# Eliminar producto
DELETE /api/productos/{id}/
# Respuesta: 403 Forbidden
```

## 🧪 Tests Verificados

Los siguientes tests pasan exitosamente:

- ✅ `test_ventas_can_read_clientes` - Personal de Ventas puede leer clientes
- ✅ `test_ventas_can_read_productos` - Personal de Ventas puede leer productos
- ✅ `test_ventas_cannot_create_clientes` - Personal de Ventas NO puede crear clientes
- ✅ `test_ventas_cannot_create_productos` - Personal de Ventas NO puede crear productos
- ✅ `test_ventas_cannot_update_clientes` - Personal de Ventas NO puede actualizar clientes
- ✅ `test_ventas_cannot_update_productos` - Personal de Ventas NO puede actualizar productos
- ✅ `test_ventas_cannot_delete_clientes` - Personal de Ventas NO puede eliminar clientes
- ✅ `test_ventas_cannot_delete_productos` - Personal de Ventas NO puede eliminar productos

## 📱 Uso en Frontend

### JavaScript/TypeScript

```javascript
// Obtener lista de clientes (permitido para Ventas)
const response = await fetch('/api/clientes/', {
    headers: {
        'Authorization': `Token ${ventasUserToken}`
    }
});

if (response.ok) {
    const clientes = await response.json();
    // Mostrar lista de clientes para seleccionar en factura
} else if (response.status === 403) {
    console.log('Sin permisos de lectura');
}

// Obtener lista de productos (permitido para Ventas)
const productos = await fetch('/api/productos/', {
    headers: {
        'Authorization': `Token ${ventasUserToken}`
    }
});

// Crear factura (permitido para Ventas)
const nuevaFactura = await fetch('/api/facturas/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${ventasUserToken}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        cliente: clienteSeleccionado.id,
        items: [
            {
                producto: productoSeleccionado.id,
                cantidad: 2,
                precio_unitario: productoSeleccionado.precio
            }
        ]
    })
});
```

### Manejo de Errores

```javascript
async function handleVentasRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                'Authorization': `Token ${token}`,
                ...options.headers
            }
        });

        if (response.status === 403) {
            const error = await response.json();
            if (error.detail?.includes('solo puede consultar')) {
                showMessage('Solo puedes consultar esta información, no modificarla');
            }
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Error en request:', error);
        return null;
    }
}
```

## 🔧 Flujo de Trabajo Recomendado

### Para Personal de Ventas:

1. **Consultar clientes disponibles**
   ```bash
   GET /api/clientes/
   ```

2. **Consultar productos disponibles**
   ```bash
   GET /api/productos/
   ```

3. **Crear nueva factura con cliente y productos consultados**
   ```bash
   POST /api/facturas/
   {
     "cliente": cliente_id,
     "items": [
       {
         "producto": producto_id,
         "cantidad": 2,
         "precio_unitario": precio_producto
       }
     ]
   }
   ```

### Para Otros Roles:

- **Secretario**: Puede gestionar clientes + consultar todo lo demás
- **Bodega**: Puede gestionar productos + consultar todo lo demás  
- **Administrador**: Acceso completo a todo

## 🎯 Beneficios

1. **Seguridad**: Personal de Ventas no puede modificar datos críticos
2. **Funcionalidad**: Pueden acceder a la información necesaria para facturar
3. **Separación de responsabilidades**: Cada rol tiene permisos específicos
4. **Auditoría**: Todas las operaciones están registradas por rol

## 🔄 Compatibilidad

- ✅ **Totalmente compatible** con implementaciones anteriores
- ✅ **No requiere cambios** en el frontend existente
- ✅ **Amplia funcionalidad** sin comprometer seguridad
- ✅ **Tests completos** verifican el comportamiento

---

**🎉 El personal de Ventas ahora puede crear facturas con acceso de solo lectura a clientes y productos!**
