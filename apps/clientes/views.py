
"""Vistas para la app de clientes."""

from django.shortcuts import render
from apps.usuarios.decorators import role_required
from .models import Cliente


@role_required('Secretario', 'Administrador')
def lista_clientes(request):
    """Vista para listar todos los clientes."""
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})
