# Endpoints de PDF para Facturas

## Descripción General

Este documento describe los endpoints implementados para visualizar, descargar y generar PDFs de facturas en el sistema de facturación segura.

## Endpoints Disponibles

### 1. Visualizar PDF de Factura

**Endpoint:** `GET /api/facturas/{id}/view_pdf/`

**Descripción:** Permite visualizar un PDF de una factura directamente en el navegador.

**Parámetros:**
- `id`: ID de la factura a visualizar

**Respuesta:**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `inline; filename="factura_[numero|id].pdf"`

**Ejemplo de uso:**
```javascript
// Visualizar factura en una nueva ventana
window.open('/api/facturas/123/view_pdf/', '_blank');

// O en un iframe
document.getElementById('pdf-iframe').src = '/api/facturas/123/view_pdf/';
```

### 2. Descargar PDF de Factura

**Endpoint:** `GET /api/facturas/{id}/download_pdf/`

**Descripción:** Permite descargar un PDF de una factura como archivo.

**Parámetros:**
- `id`: ID de la factura a descargar

**Respuesta:**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="factura_[numero|id].pdf"`

**Ejemplo de uso:**
```javascript
// Descargar factura
const downloadLink = document.createElement('a');
downloadLink.href = '/api/facturas/123/download_pdf/';
downloadLink.download = 'factura_123.pdf';
downloadLink.click();

// O simplemente redirigir
window.location = '/api/facturas/123/download_pdf/';
```

### 3. Enviar PDF por Email (Existente - Mejorado)

**Endpoint:** `POST /api/facturas/{id}/send_pdf/`

**Descripción:** Envía un PDF de una factura por email. Ahora usa la función helper común para generar el PDF.

**Parámetros:**
- `id`: ID de la factura a enviar

**Body:**
```json
{
    "destinatario": "cliente@example.com",
    "asunto": "Factura #123",
    "mensaje": "Adjunto encontrará su factura."
}
```

**Respuesta:**
```json
{
    "mensaje": "PDF enviado exitosamente",
    "destinatario": "cliente@example.com"
}
```

## Autenticación y Permisos

Todos los endpoints requieren:
- **Autenticación:** Token de autenticación válido
- **Permisos:** Usuario debe tener permisos para ver facturas

```javascript
// Ejemplo con token de autenticación
fetch('/api/facturas/123/view_pdf/', {
    method: 'GET',
    headers: {
        'Authorization': 'Token your-token-here'
    }
})
.then(response => response.blob())
.then(blob => {
    const url = window.URL.createObjectURL(blob);
    window.open(url);
});
```

## Estructura del PDF Generado

El PDF incluye:
- **Encabezado:** Título "FACTURA" y número de factura
- **Información de la empresa:** Nombre, dirección, teléfono
- **Información del cliente:** Nombre, email, teléfono
- **Detalles de la factura:** Fecha, estado, total
- **Tabla de items:** Productos/servicios con cantidades y precios
- **Totales:** Subtotal, impuestos, total final

## Naming Convention para Archivos

Los nombres de archivos PDF siguen esta lógica:
- Si la factura tiene `numero_factura`: `factura_[numero_factura].pdf`
- Si no tiene número (estado borrador): `factura_[id].pdf`

## Códigos de Error

| Código | Descripción |
|--------|-------------|
| 404 | Factura no encontrada |
| 401 | No autenticado |
| 403 | Sin permisos para acceder |
| 500 | Error interno del servidor |

## Integración Frontend

### Botón para Visualizar PDF

```html
<button onclick="verPDF(123)">Ver PDF</button>

<script>
function verPDF(facturaId) {
    const token = localStorage.getItem('authToken');
    
    fetch(`/api/facturas/${facturaId}/view_pdf/`, {
        headers: {
            'Authorization': `Token ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Error al cargar PDF');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al cargar el PDF');
    });
}
</script>
```

### Botón para Descargar PDF

```html
<button onclick="descargarPDF(123)">Descargar PDF</button>

<script>
function descargarPDF(facturaId) {
    const token = localStorage.getItem('authToken');
    
    fetch(`/api/facturas/${facturaId}/download_pdf/`, {
        headers: {
            'Authorization': `Token ${token}`
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Error al descargar PDF');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `factura_${facturaId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al descargar el PDF');
    });
}
</script>
```

### Visor de PDF Integrado

```html
<div id="pdf-viewer" style="width: 100%; height: 600px;">
    <iframe id="pdf-iframe" style="width: 100%; height: 100%; border: none;"></iframe>
</div>

<script>
function mostrarPDFEnViewer(facturaId) {
    const token = localStorage.getItem('authToken');
    const iframe = document.getElementById('pdf-iframe');
    
    // Configurar headers para la autenticación
    iframe.src = `/api/facturas/${facturaId}/view_pdf/?token=${token}`;
}
</script>
```

## Consideraciones Técnicas

### Optimización
- Los PDFs se generan en memoria usando `BytesIO`
- No se almacenan archivos temporales en el sistema
- La generación es eficiente y escalable

### Seguridad
- Todos los endpoints requieren autenticación
- Se verifican permisos antes de generar PDFs
- Los tokens de autenticación son validados

### Mantenimiento
- El código para generar PDFs está centralizado en `_generar_pdf_factura()`
- Es fácil modificar el formato del PDF desde un solo lugar
- Los tests cubren todos los casos de uso principales

## Tests Disponibles

El archivo `test_factura_pdf_endpoints.py` incluye:
- Test de visualización de PDF
- Test de descarga de PDF
- Test de headers correctos
- Test de permisos de usuario
- Test de nombres de archivo
- Test de facturas sin ítems
- Test de facturas emitidas vs. borradores
- Test de manejo de errores

Para ejecutar los tests:
```bash
python manage.py test test_factura_pdf_endpoints.TestFacturaPDFEndpoints
```

## Próximas Mejoras

1. **Plantillas personalizables:** Permitir diferentes formatos de PDF
2. **Watermarks:** Agregar marcas de agua para borradores
3. **Firmas digitales:** Implementar firma digital para facturas oficiales
4. **Compresión:** Optimizar el tamaño de los archivos PDF
5. **Caché:** Implementar caché para PDFs frecuentemente solicitados
