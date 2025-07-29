
"""Vistas para la app de productos."""

from django.shortcuts import render
from apps.usuarios.decorators import role_required
from .models import Producto


@role_required('Bodega', 'Administrador')
def lista_productos(request):
    """Vista para listar todos los productos."""
    productos = Producto.objects.all()
    return render(request, 'productos/lista_productos.html', {'productos': productos})
