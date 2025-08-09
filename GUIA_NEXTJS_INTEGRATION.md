# API de Pagos - Sistema de Facturación

## Configuración del Proyecto

El sistema de pagos está completamente implementado y listo para usar con tu proyecto Next.js. Los endpoints están disponibles en `http://localhost:8000`.

## Credenciales de Prueba

### Usuarios del Sistema
```bash
# Para obtener tokens de usuarios
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Respuesta esperada:
# {"token": "abc123..."}
```

### Clientes
Los clientes usan tokens generados automáticamente. Para obtener el token de un cliente específico, usa el endpoint de administración.

## Ejemplos de Uso en Next.js

### 1. Cliente: Consultar Facturas Pendientes

```typescript
// lib/api.ts
const API_BASE = 'http://localhost:8000';

export async function getFacturasPendientes(clienteToken: string) {
  const response = await fetch(`${API_BASE}/api/cliente/facturas-pendientes/`, {
    headers: {
      'Authorization': `Token ${clienteToken}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Error al obtener facturas pendientes');
  }
  
  return response.json();
}
```

### 2. Cliente: Registrar Pago

```typescript
export interface RegistrarPagoData {
  factura: number;
  tipo_pago: 'efectivo' | 'tarjeta' | 'transferencia' | 'cheque';
  monto: string;
  numero_transaccion: string;
  observaciones?: string;
}

export async function registrarPago(clienteToken: string, data: RegistrarPagoData) {
  const response = await fetch(`${API_BASE}/api/cliente/registrar-pago/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${clienteToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Error al registrar pago');
  }
  
  return response.json();
}
```

### 3. Cliente: Consultar Mis Pagos

```typescript
export async function getMisPagos(clienteToken: string) {
  const response = await fetch(`${API_BASE}/api/cliente/mis-pagos/`, {
    headers: {
      'Authorization': `Token ${clienteToken}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Error al obtener pagos');
  }
  
  return response.json();
}
```

### 4. Administrador: Listar Pagos Pendientes

```typescript
export async function getPagosPendientes(adminToken: string) {
  const response = await fetch(`${API_BASE}/api/pagos/pendientes/`, {
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Error al obtener pagos pendientes');
  }
  
  return response.json();
}
```

### 5. Administrador: Validar Pago

```typescript
export interface ValidarPagoData {
  accion: 'aprobar' | 'rechazar';
  motivo?: string; // requerido para rechazar
}

export async function validarPago(adminToken: string, pagoId: number, data: ValidarPagoData) {
  const response = await fetch(`${API_BASE}/api/pagos/${pagoId}/validar/`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Error al validar pago');
  }
  
  return response.json();
}
```

### 6. Administrador: Obtener Estadísticas

```typescript
export async function getEstadisticasPagos(adminToken: string) {
  const response = await fetch(`${API_BASE}/api/pagos/estadisticas/`, {
    headers: {
      'Authorization': `Token ${adminToken}`,
      'Content-Type': 'application/json',
    },
  });
  
  if (!response.ok) {
    throw new Error('Error al obtener estadísticas');
  }
  
  return response.json();
}
```

## Componentes React de Ejemplo

### Formulario de Registro de Pago

```tsx
// components/RegistrarPago.tsx
import { useState } from 'react';
import { registrarPago, type RegistrarPagoData } from '@/lib/api';

interface Props {
  facturaId: number;
  facturaTotal: string;
  clienteToken: string;
  onSuccess: () => void;
}

export default function RegistrarPago({ facturaId, facturaTotal, clienteToken, onSuccess }: Props) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<RegistrarPagoData>({
    factura: facturaId,
    tipo_pago: 'transferencia',
    monto: facturaTotal,
    numero_transaccion: '',
    observaciones: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await registrarPago(clienteToken, formData);
      alert('Pago registrado exitosamente');
      onSuccess();
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Error al registrar pago');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium">Tipo de Pago</label>
        <select
          value={formData.tipo_pago}
          onChange={(e) => setFormData(prev => ({ ...prev, tipo_pago: e.target.value as any }))}
          className="mt-1 block w-full border rounded-md px-3 py-2"
        >
          <option value="efectivo">Efectivo</option>
          <option value="tarjeta">Tarjeta</option>
          <option value="transferencia">Transferencia</option>
          <option value="cheque">Cheque</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium">Monto</label>
        <input
          type="number"
          step="0.01"
          value={formData.monto}
          onChange={(e) => setFormData(prev => ({ ...prev, monto: e.target.value }))}
          className="mt-1 block w-full border rounded-md px-3 py-2"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Número de Transacción</label>
        <input
          type="text"
          value={formData.numero_transaccion}
          onChange={(e) => setFormData(prev => ({ ...prev, numero_transaccion: e.target.value }))}
          className="mt-1 block w-full border rounded-md px-3 py-2"
          placeholder="Código del comprobante"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium">Observaciones</label>
        <textarea
          value={formData.observaciones}
          onChange={(e) => setFormData(prev => ({ ...prev, observaciones: e.target.value }))}
          className="mt-1 block w-full border rounded-md px-3 py-2"
          rows={3}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Registrando...' : 'Registrar Pago'}
      </button>
    </form>
  );
}
```

### Panel de Administración de Pagos

```tsx
// components/AdminPagos.tsx
import { useState, useEffect } from 'react';
import { getPagosPendientes, validarPago } from '@/lib/api';

interface Props {
  adminToken: string;
}

export default function AdminPagos({ adminToken }: Props) {
  const [pagos, setPagos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPagos();
  }, []);

  const loadPagos = async () => {
    try {
      const data = await getPagosPendientes(adminToken);
      setPagos(data.results);
    } catch (error) {
      console.error('Error loading pagos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleValidar = async (pagoId: number, accion: 'aprobar' | 'rechazar') => {
    let motivo = '';
    if (accion === 'rechazar') {
      motivo = prompt('Motivo del rechazo:') || '';
      if (!motivo) return;
    }

    try {
      await validarPago(adminToken, pagoId, { accion, motivo });
      alert(`Pago ${accion === 'aprobar' ? 'aprobado' : 'rechazado'} exitosamente`);
      loadPagos(); // Recargar lista
    } catch (error) {
      alert(error instanceof Error ? error.message : 'Error al validar pago');
    }
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Pagos Pendientes de Validación</h2>
      
      {pagos.length === 0 ? (
        <p>No hay pagos pendientes</p>
      ) : (
        <div className="grid gap-4">
          {pagos.map((pago: any) => (
            <div key={pago.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">Factura {pago.factura_numero}</h3>
                  <p>Cliente: {pago.cliente_nombre}</p>
                  <p>Tipo: {pago.tipo_pago}</p>
                  <p>Monto: ${pago.monto}</p>
                  <p>Transacción: {pago.numero_transaccion}</p>
                  <p>Fecha: {new Date(pago.fecha_pago).toLocaleString()}</p>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => handleValidar(pago.id, 'aprobar')}
                    className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
                  >
                    Aprobar
                  </button>
                  <button
                    onClick={() => handleValidar(pago.id, 'rechazar')}
                    className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
                  >
                    Rechazar
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## Configuración de CORS (si es necesario)

Si tienes problemas de CORS con tu aplicación Next.js, verifica que en `settings.py` esté configurado:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Tu app de Next.js
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

## Estados de Pago

- **pendiente**: Pago registrado por el cliente, esperando validación
- **aprobado**: Pago validado y aprobado, factura marcada como pagada
- **rechazado**: Pago rechazado, factura mantiene estado anterior

## Próximos Pasos

1. Obtén los tokens de autenticación ejecutando el servidor Django
2. Prueba los endpoints con Postman o curl
3. Integra las funciones en tu aplicación Next.js
4. Personaliza los componentes según tu diseño

El sistema está completamente funcional y listo para producción.
