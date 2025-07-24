from django.urls import path
from .views_cliente_api import facturas_cliente_token

urlpatterns = [
    path('facturas/cliente/', facturas_cliente_token, name='facturas_cliente_token'),
]
