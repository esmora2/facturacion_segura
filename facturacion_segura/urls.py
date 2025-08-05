
"""URL configuration for facturacion_segura project."""

# Django imports
from django.contrib import admin
from django.urls import path, include

# Third-party imports
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

# App imports
from apps.usuarios.views import home
from apps.clientes.views import lista_clientes
from apps.clientes.views_api import generar_token_cliente, ClienteViewSet
from apps.productos.views import lista_productos
from apps.productos.views_api import ProductoViewSet
from apps.facturacion.views import lista_facturas, eliminar_factura
from apps.facturacion.views_api import FacturaViewSet
from apps.usuarios.views_api import me_view, UserViewSet, validate_password, login_api
from apps.usuarios.api_documentation import api_documentation
from apps.auditorias.views_api import LogAuditoriaViewSet

router = routers.DefaultRouter()
router.register(r'api/clientes', ClienteViewSet, basename='cliente')
router.register(r'api/productos', ProductoViewSet, basename='producto')
router.register(r'api/facturas', FacturaViewSet, basename='factura')
router.register(r'api/usuarios', UserViewSet, basename='usuario')  # Solo para administradores
router.register(r'api/logs', LogAuditoriaViewSet, basename='logauditoria')

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('silk/', include('silk.urls', namespace='silk')),
    # Auth
    path('accounts/', include('django.contrib.auth.urls')),

    # Vistas HTML tradicionales
    path('', home, name='home'),
    path('clientes/', lista_clientes, name='lista_clientes'),
    path(
        'clientes/<int:cliente_id>/generar-token/',
        generar_token_cliente,
        name='generar_token_cliente',
    ),
    path('productos/', lista_productos, name='lista_productos'),
    path('facturacion/', lista_facturas, name='lista_facturas'),

    path(
        'facturacion/eliminar/<int:factura_id>/',
        eliminar_factura,
        name='eliminar_factura',
    ),

    # Endpoint para obtener token
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    
    # Endpoint mejorado para login
    path('api/auth/login/', login_api, name='api_login'),
    
    # Documentación de la API
    path('api/docs/', api_documentation, name='api_documentation'),

    # Endpoint para obtener datos del usuario autenticado
    path('api/me/', me_view, name='api_me'),

    # Endpoint para validar contraseña del usuario autenticado
    path('api/auth/validate-password/', validate_password, name='validate_password'),

    # Endpoint protegido para facturas de cliente por token personalizado
    path('api/', include('apps.facturacion.urls_cliente_api')),
    # Rutas API REST Framework
    path('', include(router.urls)),
]
