"""URLs para el sistema de pagos."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_pagos import (
    PagoViewSet,
    pagos_pendientes
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'pagos', PagoViewSet, basename='pago')

urlpatterns = [
    # Endpoints específicos para usuarios con rol pagos/administradores
    path('pagos/pendientes/', pagos_pendientes, name='pagos_pendientes'),

    # ViewSet de pagos (VA AL FINAL para evitar conflictos)
    path('', include(router.urls)),
]
