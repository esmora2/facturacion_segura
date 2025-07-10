# 📋 DOCUMENTACIÓN COMPLETA DEL ENDPOINT DE EMISIÓN DE FACTURAS

## 🚀 POST /api/facturas/{id}/emitir/

### 📋 Descripción
Endpoint para emitir una factura (cambiar de estado BORRADOR a EMITIDA). Una vez emitida, la factura recibe un número único secuencial y no puede ser editada, solo marcada como pagada o anulada.

### 🔐 Permisos y Validaciones

#### **Validaciones de Usuario:**
- Solo el **creador** de la factura puede emitirla
- Los usuarios con rol **Administrador** pueden emitir cualquier factura
- Los **superusuarios** pueden emitir cualquier factura

#### **Validaciones de Estado:**
- La factura debe estar en estado **BORRADOR**
- La factura debe tener al menos **un item** agregado

### 📊 Request

#### Headers
```
Authorization: Token <tu_token_aqui>
Content-Type: application/json
```

#### Body
**No requiere cuerpo en la solicitud**

### 📋 Response

#### ✅ Éxito (200)
```json
{
    "status": "Factura emitida correctamente",
    "factura_id": 1,
    "numero_factura": "FAC-000001",
    "estado": "EMITIDA",
    "fecha_emision": "2025-01-20T10:30:00.123456Z"
}
```

#### ❌ Error 400 - Estado Inválido
```json
{
    "error": "Solo se pueden emitir facturas en estado borrador. Estado actual: Emitida"
}
```

#### ❌ Error 400 - Factura Sin Items
```json
{
    "error": "No se puede emitir una factura sin items"
}
```

#### ❌ Error 403 - Sin Permisos
```json
{
    "error": "Solo el creador de la factura o un Administrador pueden emitirla"
}
```

#### ❌ Error 404 - No Encontrada
```json
{
    "detail": "No encontrado."
}
```

### 🎯 Lógica de Negocio

#### **Qué sucede al emitir:**
1. Se verifica que el usuario tenga permisos
2. Se valida que la factura esté en estado BORRADOR
3. Se verifica que tenga al menos un item
4. Se genera un número de factura secuencial único (FAC-XXXXXX)
5. Se cambia el estado a EMITIDA
6. Se guarda la factura con los nuevos datos

#### **Número de Factura:**
- Formato: `FAC-XXXXXX` (ejemplo: FAC-000001, FAC-000002, etc.)
- Secuencial basado en la cantidad total de facturas emitidas
- Una vez asignado, no se puede cambiar

### 💡 Recomendaciones para el Frontend

#### **Validaciones en UI:**
```javascript
// Verificar antes de mostrar el botón "Emitir"
const puedeEmitir = (factura, currentUser) => {
    // Solo mostrar si está en borrador
    if (factura.estado !== 'BORRADOR') return false;
    
    // Solo mostrar si tiene items
    if (!factura.items || factura.items.length === 0) return false;
    
    // Solo mostrar si es el creador o admin
    if (currentUser.role === 'Administrador') return true;
    if (factura.creador === currentUser.id) return true;
    
    return false;
};
```

#### **Confirmación de Emisión:**
```javascript
const confirmarEmision = async (facturaId) => {
    const confirmacion = confirm(
        "¿Está seguro de emitir esta factura?\n\n" +
        "Una vez emitida:\n" +
        "• No se podrá editar\n" +
        "• Recibirá un número oficial\n" +
        "• Solo se podrá marcar como pagada o anular"
    );
    
    if (confirmacion) {
        try {
            const response = await fetch(`/api/facturas/${facturaId}/emitir/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                alert(`Factura emitida exitosamente!\nNúmero: ${data.numero_factura}`);
                // Recargar datos o redirigir
                location.reload();
            } else {
                const error = await response.json();
                alert(`Error: ${error.error || 'No se pudo emitir la factura'}`);
            }
        } catch (error) {
            alert('Error de conexión. Intente nuevamente.');
        }
    }
};
```

#### **Estados de Botón:**
```javascript
const getButtonState = (factura, currentUser) => {
    if (factura.estado !== 'BORRADOR') {
        return {
            disabled: true,
            text: `Factura ${factura.estado.toLowerCase()}`,
            class: 'btn-secondary'
        };
    }
    
    if (!factura.items || factura.items.length === 0) {
        return {
            disabled: true,
            text: 'Agregar items primero',
            class: 'btn-warning'
        };
    }
    
    if (!puedeEmitir(factura, currentUser)) {
        return {
            disabled: true,
            text: 'Sin permisos',
            class: 'btn-secondary'
        };
    }
    
    return {
        disabled: false,
        text: 'Emitir Factura',
        class: 'btn-success'
    };
};
```

### 🔄 Flujo Completo de Estados

```
BORRADOR → [emitir] → EMITIDA → [marcar_pagada] → PAGADA
    ↓                     ↓                         ↓
[editar/eliminar]     [anular]                [anular]
    ↓                     ↓                         ↓
 BORRADOR            ANULADA                   ANULADA
```

### 🧪 Casos de Prueba Recomendados

1. **Emisión exitosa por creador**
2. **Emisión exitosa por administrador**
3. **Error: Usuario sin permisos**
4. **Error: Factura ya emitida**
5. **Error: Factura sin items**
6. **Error: Factura no encontrada**
7. **Verificar número secuencial único**
8. **Verificar cambio de estado correcto**
