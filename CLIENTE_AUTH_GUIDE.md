# Sistema de Autenticación Estándar para Clientes

## 🎯 Resumen de Cambios Implementados

Hemos simplificado el sistema de autenticación de clientes para usar el **sistema estándar de Django REST Framework** en lugar de tokens personalizados.

## 📋 Endpoints Disponibles

### 1. Registro de Clientes
```
POST /api/cliente/register/
```
**Body:**
```json
{
    "username": "cliente_ejemplo",
    "email": "cliente@example.com", 
    "password": "password123",
    "nombre": "Nombre Cliente",
    "telefono": "1234567890"
}
```

### 2. Login de Clientes (Estándar)
```
POST /api/token/
```
**Body:**
```json
{
    "username": "cliente_ejemplo",
    "password": "password123"
}
```
**Respuesta:**
```json
{
    "token": "abc123def456..."
}
```

### 3. Datos del Cliente Autenticado
```
GET /api/cliente/me/
```
**Headers:**
```
Authorization: Token abc123def456...
```

### 4. Facturas del Cliente
```
GET /api/clientes/facturas/
```
**Headers:**
```
Authorization: Token abc123def456...
```

### 5. Pagos del Cliente
```
GET /api/pagos/mis-pagos/
```
**Headers:**
```
Authorization: Token abc123def456...
```

### 6. Registrar Pago
```
POST /api/pagos/registrar-cliente/
```
**Headers:**
```
Authorization: Token abc123def456...
```

## 🔧 Cambios Técnicos Realizados

### 1. Modelo Cliente
- ✅ Ahora hereda de `AbstractUser`
- ✅ Compatible con autenticación estándar de Django
- ✅ Eliminado modelo `ClienteToken` personalizado
- ✅ Campo `role = 'Cliente'` para diferenciación

### 2. Autenticación
- ✅ Usa `TokenAuthentication` estándar de DRF
- ✅ Tokens gestionados por Django (`authtoken_token` table)
- ✅ Endpoint `/api/token/` para login
- ✅ Headers estándar: `Authorization: Token <token>`

### 3. APIs de Cliente
- ✅ Validación automática de rol `Cliente`
- ✅ Acceso solo a recursos propios
- ✅ Compatible con frontend React/Next.js

## 💻 Ejemplo de Uso en Next.js

```javascript
// 1. Login del cliente
const loginResponse = await fetch('http://localhost:8000/api/token/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'cliente_ejemplo',
    password: 'password123'
  })
});

const { token } = await loginResponse.json();

// 2. Guardar token (localStorage, cookies, etc.)
localStorage.setItem('authToken', token);

// 3. Usar token en requests autenticados
const clienteResponse = await fetch('http://localhost:8000/api/cliente/me/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json',
  }
});

const clienteData = await clienteResponse.json();

// 4. Consultar facturas
const facturasResponse = await fetch('http://localhost:8000/api/clientes/facturas/', {
  headers: {
    'Authorization': `Token ${token}`,
  }
});

const facturas = await facturasResponse.json();
```

## 🛡️ Seguridad

- ✅ **Sin tokens en base de datos**: Usa tabla estándar `authtoken_token`
- ✅ **Validación de rol**: Solo clientes acceden a endpoints de cliente
- ✅ **Aislamiento**: Cada cliente solo ve sus propios datos
- ✅ **Autenticación robusta**: Sistema probado de Django

## 🔄 Flujo Completo

1. **Cliente se registra** → `POST /api/cliente/register/`
2. **Cliente hace login** → `POST /api/token/`
3. **Obtiene token** → Usa en header `Authorization`
4. **Accede a recursos** → Facturas, pagos, datos personales
5. **Registra pagos** → Con validación automática de pertenencia

## ✨ Ventajas del Nuevo Sistema

- 🎯 **Estándar**: Usa componentes nativos de Django/DRF
- 🔧 **Mantenible**: Menos código personalizado
- 🛡️ **Seguro**: Sistema probado y robusto
- 🔗 **Compatible**: Funciona con cualquier frontend
- 📱 **Escalable**: Fácil de extender y modificar

## 🧪 Pruebas

Ejecuta el script de prueba:
```bash
python test_cliente_auth.py
```

Este script valida todo el flujo: registro → login → consultas → pagos.
