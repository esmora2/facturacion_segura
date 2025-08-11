
"""Vistas para la app de clientes."""

from django.shortcuts import render
from django.contrib.auth import get_user_model
from apps.usuarios.decorators import role_required

User = get_user_model()


@role_required('Secretario', 'Administrador')
def lista_clientes(request):
    """Vista para listar todos los clientes."""
    clientes = User.objects.filter(role='Cliente')
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})
