# Prueba Rápida - Ejemplo Específico

## 🎯 Tu Caso Específico Corregido

### Request Original (con error):
```json
POST http://localhost:8000/api/pagos/
{
  "factura": 30,
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030"
}
```

### Request Corregido (agregando pagado_por):
```json
POST http://localhost:8000/api/pagos/
Authorization: Token <admin_token>
Content-Type: application/json

{
  "factura": 30,
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
  "pagado_por": 1
}
```

## 🔧 Pasos para Completar la Prueba

### 1. Obtener token de admin:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Ver información del usuario logueado:
```bash
curl -X GET http://localhost:8000/api/me/ \
  -H "Authorization: Token <token_del_paso_1>"
```

### 3. Usar el ID del usuario en el campo pagado_por:
```bash
curl -X POST http://localhost:8000/api/pagos/ \
  -H "Authorization: Token <token_del_paso_1>" \
  -H "Content-Type: application/json" \
  -d '{
    "factura": 30,
    "tipo_pago": "transferencia",
    "monto": "23.00",
    "numero_transaccion": "TRF-2025-08-07-001",
    "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
    "pagado_por": <id_del_usuario>
  }'
```

## 💡 Alternativa Rápida

Si el usuario admin tiene ID 1 (como es común), puedes probar directamente:

```json
{
  "factura": 30,
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
  "pagado_por": 1
}
```

## ✅ Response Esperada

```json
{
  "id": <nuevo_id>,
  "factura": 30,
  "factura_numero": "FAC-000030",
  "factura_total": "1500.00",
  "tipo_pago": "transferencia",
  "monto": "23.00",
  "numero_transaccion": "TRF-2025-08-07-001",
  "observaciones": "Pago registrado por administrador para cliente ID 25 - Factura FAC-000030",
  "estado": "pendiente",
  "pagado_por": 1,
  "cliente_nombre": "Cliente Ejemplo",
  "fecha_pago": "2025-08-07T...",
  "fecha_validacion": null
}
```
