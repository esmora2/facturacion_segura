# 📧 SISTEMA DE ENVÍO DE FACTURAS POR CORREO

## 🔍 CÓMO FUNCIONA EL SISTEMA

### 📋 **Endpoint Principal**
```
POST /api/facturas/{id}/send_pdf/
```

### 🔄 **Proceso Completo**

#### **1. Validación Inicial**
```python
# Verificar que la factura tenga un cliente asignado
if not factura.cliente:
    return Response({"error": "No se ha asignado un cliente a esta factura"}, status=400)
```

#### **2. Generación del PDF**
El sistema utiliza **ReportLab** para generar un PDF profesional:

```python
# Librerías utilizadas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
```

**Estructura del PDF generado:**
- ✅ **Encabezado empresarial** con logo y datos de la empresa
- ✅ **Información de la factura** (número, fecha, cliente)
- ✅ **Tabla detallada** con productos, cantidades, precios y subtotales
- ✅ **Total general** calculado automáticamente
- ✅ **Pie de página** con mensaje de agradecimiento

#### **3. Envío por Email**
```python
# Configuración del email
email = EmailMessage(
    subject=f"Factura #{factura.id}",
    body="Adjunto encontrarás tu factura.",
    from_email=settings.EMAIL_HOST_USER,
    to=[cliente.email],
)
email.attach(f"factura_{factura.id}.pdf", pdf, "application/pdf")
email.send()
```

## ⚙️ CONFIGURACIÓN NECESARIA

### **1. Variables de Entorno (.env)**
```env
# Configuración SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_app
```

### **2. Settings de Django**
```python
# En settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
```

### **3. Dependencias Requeridas**
```bash
# Instalar ReportLab para generación de PDF
pip install reportlab

# Ya incluido en requirements.txt
```

## 📊 EJEMPLO DE USO

### **Request**
```http
POST /api/facturas/123/send_pdf/
Authorization: Token <tu_token>
Content-Type: application/json
```

### **Response Exitoso**
```json
{
    "status": "Factura enviada al correo"
}
```

### **Response Error**
```json
{
    "error": "No se ha asignado un cliente a esta factura"
}
```

## 🎨 CONTENIDO DEL PDF GENERADO

### **Encabezado**
```
Sistema de Facturación Segura
RUC: 123456789 | Dirección: Av. Ejemplo 123, Ciudad
Teléfono: (123) 456-7890 | Email: contacto@facturasegura.com
```

### **Información de Factura**
```
Factura #123
Fecha: 2025-07-14 10:30
Cliente: Juan Pérez
Email: juan@email.com
```

### **Tabla de Productos**
```
┌─────────────────┬──────────┬────────────────┬───────────┐
│ Descripción     │ Cantidad │ Precio Unitario│ Subtotal  │
├─────────────────┼──────────┼────────────────┼───────────┤
│ Producto A      │ 2        │ $50.00         │ $100.00   │
│ Producto B      │ 1        │ $30.00         │ $30.00    │
├─────────────────┼──────────┼────────────────┼───────────┤
│                 │          │ Total          │ $130.00   │
└─────────────────┴──────────┴────────────────┴───────────┘
```

### **Pie de Página**
```
Gracias por su compra. Contáctenos para cualquier consulta.
```

## 🔧 CONFIGURACIÓN PARA DIFERENTES PROVEEDORES

### **Gmail**
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_app  # Contraseña de aplicación
```

### **Outlook/Hotmail**
```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@outlook.com
EMAIL_HOST_PASSWORD=tu_contraseña
```

### **Yahoo**
```env
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_correo@yahoo.com
EMAIL_HOST_PASSWORD=tu_contraseña_app
```

### **SMTP Local/Personalizado**
```env
EMAIL_HOST=mail.tu-empresa.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=facturacion@tu-empresa.com
EMAIL_HOST_PASSWORD=tu_contraseña
```

## 🚨 CONFIGURACIÓN PARA DESARROLLO

### **Opción 1: Console Backend (Solo para pruebas)**
```python
# En settings.py para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### **Opción 2: File Backend (Guardar en archivo)**
```python
# En settings.py para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = BASE_DIR / 'emails'
```

### **Opción 3: Dummy Backend (No enviar)**
```python
# En settings.py para desarrollo
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
```

## 📱 INTEGRACIÓN CON FRONTEND

### **JavaScript/React**
```javascript
const enviarFacturaPorCorreo = async (facturaId) => {
    try {
        const response = await fetch(`/api/facturas/${facturaId}/send_pdf/`, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${localStorage.getItem('token')}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            alert('✅ Factura enviada al correo del cliente');
        } else {
            const error = await response.json();
            alert(`❌ Error: ${error.error}`);
        }
    } catch (error) {
        alert('❌ Error de conexión');
    }
};

// Uso en componente
<button onClick={() => enviarFacturaPorCorreo(factura.id)}>
    📧 Enviar por Correo
</button>
```

### **jQuery**
```javascript
function enviarFacturaPorCorreo(facturaId) {
    $.ajax({
        url: `/api/facturas/${facturaId}/send_pdf/`,
        method: 'POST',
        headers: {
            'Authorization': 'Token ' + localStorage.getItem('token')
        },
        success: function(response) {
            alert('✅ Factura enviada al correo del cliente');
        },
        error: function(xhr) {
            const error = JSON.parse(xhr.responseText);
            alert('❌ Error: ' + error.error);
        }
    });
}
```

## 🛠️ MEJORAS SUGERIDAS

### **1. Validaciones Adicionales**
```python
# Validar que el cliente tenga email válido
if not cliente.email:
    return Response({"error": "El cliente no tiene email asignado"}, status=400)

# Validar que la factura esté emitida
if factura.estado != 'EMITIDA':
    return Response({"error": "Solo se pueden enviar facturas emitidas"}, status=400)
```

### **2. Personalización del PDF**
```python
# Agregar logo de la empresa
from reportlab.lib.utils import ImageReader
logo = ImageReader('static/images/logo.png')
elements.append(Image(logo, width=100, height=50))

# Agregar número de factura oficial
elements.append(Paragraph(f"Factura #{factura.numero_factura}", styles['Heading2']))
```

### **3. Plantillas de Email**
```python
# Usar plantillas HTML para emails más profesionales
from django.template.loader import render_to_string

html_body = render_to_string('emails/factura_template.html', {
    'factura': factura,
    'cliente': cliente,
    'empresa': {
        'nombre': 'Sistema de Facturación Segura',
        'ruc': '123456789'
    }
})

email = EmailMessage(
    subject=f"Factura #{factura.numero_factura}",
    body=html_body,
    from_email=settings.EMAIL_HOST_USER,
    to=[cliente.email],
)
email.content_subtype = "html"  # Habilitar HTML
```

### **4. Logging y Auditoría**
```python
import logging

logger = logging.getLogger(__name__)

try:
    email.send()
    logger.info(f"Factura #{factura.id} enviada a {cliente.email}")
    return Response({"status": "Factura enviada al correo"})
except Exception as e:
    logger.error(f"Error enviando factura #{factura.id}: {str(e)}")
    return Response({"error": "Error al enviar el correo"}, status=500)
```

## 📋 ESTADO ACTUAL

### ✅ **Funcionalities Implementadas**
- ✅ Generación automática de PDF
- ✅ Envío por correo electrónico
- ✅ Validación de cliente asignado
- ✅ Formato profesional del PDF
- ✅ Cálculo automático de totales
- ✅ Configuración SMTP flexible

### 🔄 **Pendientes/Mejoras**
- ⏳ Validación de email del cliente
- ⏳ Plantillas HTML para emails
- ⏳ Logo de empresa en PDF
- ⏳ Logging y auditoría
- ⏳ Manejo de errores SMTP
- ⏳ Confirmación de entrega

El sistema está **funcional** y **listo para usar** con la configuración SMTP adecuada en las variables de entorno. 🚀
