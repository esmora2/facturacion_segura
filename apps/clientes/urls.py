"""URLs para la app de clientes."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, auth_views

router = DefaultRouter()
router.register(r'clientes', views.ClienteViewSet)

urlpatterns = [
    # API REST
    path('api/', include(router.urls)),
    
    # Autenticación de clientes
    path('api/clientes/register/', auth_views.cliente_register, name='cliente-register'),
    path('api/clientes/me/', auth_views.cliente_me, name='cliente-me'),
    
    # Nota: Para login usar /api/token/ (endpoint estándar de Django REST Framework)
]
