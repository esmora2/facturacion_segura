"""URLs para la app de pagos."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_api
from .api_documentation import api_documentation_pagos

# Router para las APIs
router = DefaultRouter()
router.register(r'pagos', views_api.PagoViewSet, basename='pago')

urlpatterns = [
    # Vistas web para validación de pagos
    path('pagos/pendientes/', views.lista_pagos_pendientes, name='lista_pagos_pendientes'),
    path('pagos/<int:pago_id>/', views.detalle_pago, name='detalle_pago'),
    path('pagos/<int:pago_id>/validar/', views.validar_pago, name='validar_pago'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),
    
    # Documentación de la API
    path('api/pagos/docs/', api_documentation_pagos, name='api_documentation_pagos'),
    
    # APIs REST
    path('api/', include(router.urls)),
    
    # APIs específicas para clientes (con autenticación por token de cliente)
    path('api/cliente/registrar-pago/', views_api.registrar_pago_cliente, name='registrar_pago_cliente'),
    path('api/cliente/mis-pagos/', views_api.mis_pagos_api, name='mis_pagos_api'),
    path('api/cliente/facturas-pendientes/', views_api.facturas_pendientes_pago, name='facturas_pendientes_pago'),
]
