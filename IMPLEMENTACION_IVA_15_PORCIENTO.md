# Implementación de Cálculo de IVA del 15%

## Descripción General

Se ha implementado un sistema completo para el cálculo automático del IVA del 15% en las facturas del sistema de facturación segura.

## Cambios Realizados

### 1. Modelo de Factura (`apps/facturacion/models.py`)

**Nuevos campos agregados:**
- `subtotal`: Suma de todos los items sin IVA
- `iva`: Cálculo del 15% sobre el subtotal
- `total`: Subtotal + IVA

**Constante agregada:**
- `IVA_PORCENTAJE = Decimal('0.15')`: Porcentaje del IVA (15%)

**Métodos agregados:**
- `calcular_totales()`: Calcula subtotal, IVA y total basado en los items
- `save()`: Sobrescrito para recalcular totales automáticamente

### 2. Modelo de FacturaItem (`apps/facturacion/models.py`)

**Cambios en métodos:**
- `save()`: Ahora recalcula totales de la factura después de agregar un item
- `delete()`: Ahora recalcula totales de la factura después de eliminar un item

### 3. Serializer de Factura (`apps/facturacion/serializers.py`)

**Campos agregados:**
- `subtotal`, `iva`, `total`: Como campos de solo lectura
- Los campos se calculan automáticamente y se incluyen en la respuesta del API

**Métodos modificados:**
- `create()`: Recalcula totales después de crear todos los items

### 4. Generación de PDFs (`apps/facturacion/views_api.py`)

**Mejoras en el PDF:**
- Muestra subtotal, IVA (15%) y total por separado
- Formato profesional con filas diferenciadas para cada total
- Estilos mejorados para mejor visualización

### 5. Migración de Base de Datos

**Migración creada:**
- `0005_factura_iva_factura_subtotal_factura_total.py`
- Agrega los nuevos campos a la tabla de facturas

### 6. Script de Actualización

**Archivo:** `actualizar_facturas_iva.py`
- Actualiza todas las facturas existentes con los nuevos cálculos
- Calcula subtotal, IVA y total para facturas preexistentes

## Funcionamiento

### Cálculo Automático
1. Al agregar un item a una factura, se recalculan automáticamente los totales
2. Al eliminar un item de una factura, se recalculan automáticamente los totales
3. Los cálculos se realizan en tiempo real

### Fórmulas Utilizadas
```python
subtotal = sum(item.cantidad * item.producto.precio for item in factura.items.all())
iva = subtotal * 0.15
total = subtotal + iva
```

### Ejemplo de Cálculo
```
Producto A: 2 unidades × $50.00 = $100.00
Producto B: 1 unidad × $30.00 = $30.00
--------------------------------------
Subtotal: $130.00
IVA (15%): $19.50
--------------------------------------
Total: $149.50
```

## API Response

### Antes (sin IVA)
```json
{
    "id": 1,
    "cliente": 1,
    "fecha": "2025-01-14T10:30:00Z",
    "estado": "BORRADOR",
    "items": [...]
}
```

### Después (con IVA)
```json
{
    "id": 1,
    "cliente": 1,
    "fecha": "2025-01-14T10:30:00Z",
    "estado": "BORRADOR",
    "subtotal": "130.00",
    "iva": "19.50",
    "total": "149.50",
    "items": [...]
}
```

## Formato PDF

### Antes
```
Descripción    Cantidad    Precio Unit.    Subtotal
Producto A     2           $50.00          $100.00
Producto B     1           $30.00          $30.00
                           Total           $130.00
```

### Después
```
Descripción    Cantidad    Precio Unit.    Subtotal
Producto A     2           $50.00          $100.00
Producto B     1           $30.00          $30.00
                           Subtotal        $130.00
                           IVA (15%)       $19.50
                           Total           $149.50
```

## Testing

### Tests Implementados
1. **test_calcular_totales_factura_simple**: Verifica cálculo con un producto
2. **test_calcular_totales_factura_multiple_productos**: Verifica cálculo con múltiples productos
3. **test_factura_sin_items**: Verifica manejo de facturas vacías
4. **test_actualizar_totales_al_agregar_item**: Verifica actualización automática al agregar
5. **test_actualizar_totales_al_eliminar_item**: Verifica actualización automática al eliminar
6. **test_porcentaje_iva_correcto**: Verifica que el IVA sea exactamente 15%
7. **test_precision_decimal**: Verifica manejo correcto de decimales

### Ejecutar Tests
```bash
python manage.py test test_calculos_iva.TestCalculosIVA
python manage.py test test_factura_pdf_endpoints.TestFacturaPDFEndpoints
```

## Migración y Actualización

### Pasos para aplicar en producción:

1. **Crear y aplicar migración:**
```bash
python manage.py makemigrations facturacion
python manage.py migrate
```

2. **Actualizar facturas existentes:**
```bash
python actualizar_facturas_iva.py
```

3. **Verificar con tests:**
```bash
python manage.py test test_calculos_iva
```

## Características Técnicas

### Precisión Decimal
- Todos los cálculos usan `Decimal` para precisión exacta
- Campos configurados con `max_digits=10, decimal_places=2`
- Evita problemas de redondeo de punto flotante

### Transacciones Atómicas
- Los cálculos se realizan dentro de transacciones
- Garantiza consistencia de datos
- Rollback automático en caso de error

### Rendimiento
- Cálculos se realizan solo cuando es necesario
- Uso eficiente de consultas a la base de datos
- Caché automático en los campos del modelo

## Compatibilidad

### Backward Compatibility
- Las facturas existentes funcionan sin problemas
- Los endpoints existentes siguen funcionando
- Se mantiene compatibilidad con el frontend actual

### Frontend Integration
- Los nuevos campos están disponibles en el API
- Fácil integración con cualquier frontend
- Formato JSON estándar

## Próximas Mejoras

1. **IVA configurable**: Hacer el porcentaje configurable desde settings
2. **Múltiples tipos de IVA**: Soporte para diferentes tipos de IVA por producto
3. **Descuentos**: Implementar descuentos antes del cálculo del IVA
4. **Reportes**: Generar reportes de IVA por período
5. **Validaciones**: Validaciones adicionales para casos especiales

## Conclusión

La implementación del cálculo de IVA del 15% está completa y funcional. El sistema:
- ✅ Calcula automáticamente subtotal, IVA y total
- ✅ Actualiza en tiempo real al modificar items
- ✅ Genera PDFs con formato profesional
- ✅ Mantiene compatibilidad con código existente
- ✅ Incluye tests comprehensivos
- ✅ Maneja correctamente la precisión decimal
