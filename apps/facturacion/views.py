from django.shortcuts import render
from apps.usuarios.decorators import role_required
from .models import Factura
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden

@role_required('Ventas', 'Administrador')
def lista_facturas(request):
    facturas = Factura.objects.all()

    for factura in facturas:
        factura.puede_eliminar_usuario = factura.puede_eliminar(request.user)

    return render(request, 'facturacion/lista_facturas.html', {
        'facturas': facturas,
    })


@role_required('Ventas', 'Administrador')
def eliminar_factura(request, factura_id):
    factura = get_object_or_404(Factura, id=factura_id)

    if not factura.puede_eliminar(request.user):
        return HttpResponseForbidden("No estás autorizado para eliminar esta factura.")

    if request.method == "POST":
        factura.delete()
        return redirect('lista_facturas')

    return HttpResponseForbidden("Acción no permitida.")

