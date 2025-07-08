from django.shortcuts import render
from apps.usuarios.decorators import role_required

@role_required('Ventas', 'Administrador')
def home(request):
    return render(request, 'home.html')
