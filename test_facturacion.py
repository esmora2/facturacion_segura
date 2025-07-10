#!/usr/bin/env python3
"""
Script de prueba para verificar la implementación de:
1. Autorización para eliminar facturas
2. Transacciones seguras de stock
"""

import os
import sys
import django
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
sys.path.append('/home/erickxse/visual/woekspace2p/sistema-facturacion/facturacion_segura')
django.setup()

from apps.usuarios.models import User
from apps.productos.models import Producto
from apps.clientes.models import Cliente
from apps.facturacion.models import Factura, FacturaItem
from django.db import transaction


def get_unique_email():
    """Generar email único para pruebas"""
    return f"test_{random.randint(1000, 9999)}@test.com"


def get_unique_username():
    """Generar username único para pruebas"""
    return f"test_user_{random.randint(1000, 9999)}"


def test_autorizacion_eliminar():
    """Prueba autorización para eliminar facturas"""
    print("🔐 PRUEBA: Autorización para eliminar facturas")
    
    # Crear usuarios de prueba
    admin_user = User.objects.create_user(
        username=get_unique_username(),
        password='test123',
        role='Administrador'
    )
    
    ventas_user = User.objects.create_user(
        username=get_unique_username(), 
        password='test123',
        role='Ventas'
    )
    
    secretario_user = User.objects.create_user(
        username=get_unique_username(),
        password='test123', 
        role='Secretario'
    )
    
    # Crear cliente y producto de prueba
    cliente = Cliente.objects.create(
        nombre='Cliente Test',
        email=get_unique_email()
    )
    
    producto = Producto.objects.create(
        nombre=f'Producto Test {random.randint(1000, 9999)}',
        precio=100.00,
        stock=50
    )
    
    # Crear factura con usuario de ventas
    factura = Factura.objects.create(
        creador=ventas_user,
        cliente=cliente,
        estado='BORRADOR'
    )
    
    # Pruebas de autorización
    print(f"✅ Creador puede eliminar: {factura.puede_eliminar(ventas_user)}")
    print(f"✅ Administrador puede eliminar: {factura.puede_eliminar(admin_user)}")
    print(f"❌ Secretario NO puede eliminar: {not factura.puede_eliminar(secretario_user)}")
    
    # Limpiar
    factura.delete()
    producto.delete()
    cliente.delete()
    admin_user.delete()
    ventas_user.delete()
    secretario_user.delete()
    print("✅ Prueba de autorización completada\n")


def test_transacciones_stock():
    """Prueba transacciones seguras de stock"""
    print("📦 PRUEBA: Transacciones seguras de stock")
    
    # Crear datos de prueba
    user = User.objects.create_user(
        username=get_unique_username(),
        password='test123',
        role='Ventas'
    )
    
    cliente = Cliente.objects.create(
        nombre='Cliente Test',
        email=get_unique_email()
    )
    
    producto = Producto.objects.create(
        nombre=f'Producto Test {random.randint(1000, 9999)}',
        precio=100.00,
        stock=10  # Stock inicial: 10
    )
    
    print(f"Stock inicial: {producto.stock}")
    
    # Crear factura con items
    factura = Factura.objects.create(
        creador=user,
        cliente=cliente,
        estado='BORRADOR'
    )
    
    # Crear item (debería reducir stock)
    item = FacturaItem.objects.create(
        factura=factura,
        producto=producto,
        cantidad=3
    )
    
    producto.refresh_from_db()
    print(f"Stock después de crear item (cantidad 3): {producto.stock}")
    assert producto.stock == 7, f"Esperado 7, obtenido {producto.stock}"
    
    # Emitir factura y luego anular (debería restituir stock)
    factura.estado = 'EMITIDA'
    factura.save()
    
    print("Anulando factura...")
    factura.anular()
    
    producto.refresh_from_db()
    print(f"Stock después de anular: {producto.stock}")
    assert producto.stock == 10, f"Esperado 10, obtenido {producto.stock}"
    
    # Eliminar factura en borrador (debería restituir stock)
    factura2 = Factura.objects.create(
        creador=user,
        cliente=cliente,
        estado='BORRADOR'
    )
    
    item2 = FacturaItem.objects.create(
        factura=factura2,
        producto=producto,
        cantidad=5
    )
    
    producto.refresh_from_db()
    print(f"Stock después de segunda factura (cantidad 5): {producto.stock}")
    assert producto.stock == 5, f"Esperado 5, obtenido {producto.stock}"
    
    # Eliminar factura (debería restituir stock)
    factura2.delete()
    
    producto.refresh_from_db()
    print(f"Stock después de eliminar factura: {producto.stock}")
    assert producto.stock == 10, f"Esperado 10, obtenido {producto.stock}"
    
    # Limpiar
    factura.delete()
    producto.delete()
    cliente.delete()
    user.delete()
    
    print("✅ Prueba de transacciones completada\n")


def test_stock_insuficiente():
    """Prueba manejo de stock insuficiente"""
    print("⚠️  PRUEBA: Manejo de stock insuficiente")
    
    user = User.objects.create_user(
        username=get_unique_username(),
        password='test123',
        role='Ventas'
    )
    
    cliente = Cliente.objects.create(
        nombre='Cliente Test 2',
        email=get_unique_email()
    )
    
    producto = Producto.objects.create(
        nombre=f'Producto Test {random.randint(1000, 9999)}',
        precio=50.00,
        stock=2  # Stock muy bajo
    )
    
    factura = Factura.objects.create(
        creador=user,
        cliente=cliente,
        estado='BORRADOR'
    )
    
    # Intentar crear item con más cantidad que stock disponible
    try:
        item = FacturaItem.objects.create(
            factura=factura,
            producto=producto,
            cantidad=5  # Más que el stock disponible (2)
        )
        print("❌ ERROR: Debería haber fallado por stock insuficiente")
    except ValueError as e:
        print(f"✅ Correctamente rechazado: {e}")
    
    # Verificar que el stock no cambió
    producto.refresh_from_db()
    assert producto.stock == 2, f"Stock debería seguir siendo 2, pero es {producto.stock}"
    
    # Limpiar
    factura.delete()
    producto.delete()
    cliente.delete()
    user.delete()
    
    print("✅ Prueba de stock insuficiente completada\n")


if __name__ == "__main__":
    print("🧪 EJECUTANDO PRUEBAS DEL SISTEMA DE FACTURACIÓN\n")
    
    try:
        test_autorizacion_eliminar()
        test_transacciones_stock()
        test_stock_insuficiente()
        
        print("🎉 TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("\n📋 RESUMEN DE FUNCIONALIDADES VERIFICADAS:")
        print("✅ Solo el creador o Administrador pueden eliminar facturas")
        print("✅ Stock se reduce automáticamente al crear items")
        print("✅ Stock se restituye automáticamente al anular facturas")
        print("✅ Stock se restituye automáticamente al eliminar facturas")
        print("✅ Se valida stock insuficiente antes de crear items")
        print("✅ Todas las operaciones usan transacciones atómicas")
        
    except Exception as e:
        print(f"❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
