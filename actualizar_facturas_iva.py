#!/usr/bin/env python
"""
Script para actualizar las facturas existentes con los nuevos campos de IVA.
Ejecutar después de aplicar la migración.
"""

import os
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from apps.facturacion.models import Factura

def actualizar_facturas_existentes():
    """
    Actualiza todas las facturas existentes para calcular subtotal, IVA y total.
    """
    facturas = Factura.objects.all()
    actualizadas = 0
    
    print(f"Actualizando {facturas.count()} facturas...")
    
    for factura in facturas:
        # Calcular totales
        totales = factura.calcular_totales()
        
        # Guardar la factura (esto disparará el método save que recalcula)
        factura.save()
        
        actualizadas += 1
        
        print(f"Factura #{factura.id}: Subtotal: ${totales['subtotal']:.2f}, "
              f"IVA: ${totales['iva']:.2f}, Total: ${totales['total']:.2f}")
    
    print(f"\n✅ {actualizadas} facturas actualizadas exitosamente.")

if __name__ == "__main__":
    actualizar_facturas_existentes()
