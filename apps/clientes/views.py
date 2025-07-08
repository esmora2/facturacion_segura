from django.shortcuts import render
from apps.usuarios.decorators import role_required
from .models import Cliente

@role_required('Secretario', 'Administrador')
def lista_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/lista_clientes.html', {'clientes': clientes})
