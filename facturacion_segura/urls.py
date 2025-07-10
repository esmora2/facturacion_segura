from django.contrib import admin
from django.urls import path, include

# Vistas HTML tradicionales
from apps.usuarios.views import home
from apps.clientes.views import lista_clientes
from apps.productos.views import lista_productos
from apps.facturacion.views import lista_facturas, eliminar_factura

# Django REST Framework
from rest_framework import routers
from apps.clientes.views_api import ClienteViewSet
from apps.productos.views_api import ProductoViewSet
from apps.facturacion.views_api import FacturaViewSet
from apps.usuarios.views_api import me_view, UserViewSet

from rest_framework.authtoken.views import obtain_auth_token

# DRF Router
router = routers.DefaultRouter()
router.register(r'api/clientes', ClienteViewSet)
router.register(r'api/productos', ProductoViewSet)
router.register(r'api/facturas', FacturaViewSet)
router.register(r'api/usuarios', UserViewSet)  # Solo para administradores

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Auth
    path('accounts/', include('django.contrib.auth.urls')),

    # Vistas HTML tradicionales
    path('', home, name='home'),
    path('clientes/', lista_clientes, name='lista_clientes'),
    path('productos/', lista_productos, name='lista_productos'),
    path('facturacion/', lista_facturas, name='lista_facturas'),
    path('facturacion/eliminar/<int:factura_id>/', eliminar_factura, name='eliminar_factura'),

    # Endpoint para obtener token
    path('api/token/', obtain_auth_token, name='api_token_auth'),

    # Endpoint para obtener datos del usuario autenticado
    path('api/me/', me_view, name='api_me'),

    # Rutas API REST Framework
    path('', include(router.urls)),
]
