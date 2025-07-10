#!/usr/bin/env python3
"""
Script para listar automáticamente todos los endpoints disponibles
en el sistema de facturación.
"""

import os
import sys
import django
from django.urls import get_resolver
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
sys.path.append('/home/erickxse/visual/woekspace2p/sistema-facturacion/facturacion_segura')
django.setup()

def print_urls(urlpatterns, prefix=''):
    """Imprime recursivamente todas las URLs del proyecto"""
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            # Es un include(), recursión
            new_prefix = prefix + str(pattern.pattern)
            print_urls(pattern.url_patterns, new_prefix)
        else:
            # Es una URL individual
            url = prefix + str(pattern.pattern)
            name = getattr(pattern, 'name', 'sin_nombre')
            
            # Obtener métodos HTTP permitidos
            methods = []
            if hasattr(pattern, 'callback'):
                callback = pattern.callback
                if hasattr(callback, 'cls'):  # ViewSet
                    # Es un ViewSet de DRF
                    viewset = callback.cls
                    if hasattr(viewset, 'http_method_names'):
                        # Mapear acciones a métodos HTTP
                        actions = ['list', 'create', 'retrieve', 'update', 'partial_update', 'destroy']
                        method_map = {
                            'list': 'GET',
                            'create': 'POST', 
                            'retrieve': 'GET',
                            'update': 'PUT',
                            'partial_update': 'PATCH',
                            'destroy': 'DELETE'
                        }
                        
                        for action in actions:
                            if hasattr(viewset, action):
                                methods.append(method_map.get(action, 'GET'))
                        
                        # Buscar @actions personalizadas
                        for attr_name in dir(viewset):
                            attr = getattr(viewset, attr_name)
                            if hasattr(attr, 'mapping'):  # Es un @action
                                for method in attr.mapping.keys():
                                    methods.append(method.upper())
                    
                elif hasattr(callback, 'view_class'):  # Vista basada en clase
                    view = callback.view_class
                    if hasattr(view, 'http_method_names'):
                        methods = [m.upper() for m in view.http_method_names if m != 'options']
                else:  # Vista basada en función
                    methods = ['GET', 'POST']  # Por defecto
            
            methods = list(set(methods)) if methods else ['GET']
            methods_str = ', '.join(sorted(methods))
            
            print(f"{methods_str:20} {url:50} {name}")

def main():
    print("🔗 LISTA COMPLETA DE ENDPOINTS DEL SISTEMA")
    print("=" * 80)
    print(f"{'MÉTODOS':20} {'URL':50} {'NOMBRE'}")
    print("-" * 80)
    
    resolver = get_resolver()
    print_urls(resolver.url_patterns)
    
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE ENDPOINTS:")
    
    # Contar endpoints por categoría
    from rest_framework import routers
    router = routers.DefaultRouter()
    
    print(f"\n🌐 Vistas Web:")
    print(f"   • Autenticación: /accounts/login/, /accounts/logout/")
    print(f"   • Página principal: /")
    print(f"   • Clientes: /clientes/")
    print(f"   • Productos: /productos/")
    print(f"   • Facturación: /facturacion/")
    print(f"   • Admin: /admin/")
    
    print(f"\n🔌 API REST:")
    print(f"   • Autenticación: /api/token/, /api/me/")
    print(f"   • Usuarios: /api/usuarios/ (CRUD + toggle_active, change_role, roles)")
    print(f"   • Clientes: /api/clientes/ (CRUD)")
    print(f"   • Productos: /api/productos/ (CRUD)")
    print(f"   • Facturas: /api/facturas/ (CRUD + send_pdf, emitir, marcar_pagada, anular_factura, metrics)")
    
    print(f"\n🔐 Control de Acceso:")
    print(f"   • Públicos: /api/token/, /accounts/login/")
    print(f"   • Autenticados: /api/me/, /")
    print(f"   • Admin: /api/usuarios/, /admin/")
    print(f"   • Admin + Secretario: /api/clientes/, /clientes/")
    print(f"   • Admin + Bodega: /api/productos/, /productos/")
    print(f"   • Admin + Ventas: /api/facturas/, /facturacion/")

if __name__ == "__main__":
    main()
