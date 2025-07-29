
"""Vistas para la app de facturación."""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from apps.usuarios.decorators import role_required
from .models import Factura


@role_required('Ventas', 'Administrador')
def lista_facturas(request):
    """Vista para listar todas las facturas."""
    facturas = Factura.objects.all()
    for factura in facturas:
        factura.puede_eliminar_usuario = factura.puede_eliminar(request.user)
    return render(request, 'facturacion/lista_facturas.html', {
        'facturas': facturas,
    })



@role_required('Ventas', 'Administrador')
def eliminar_factura(request, factura_id):
    """Vista para eliminar una factura si el usuario tiene permisos."""
    factura = get_object_or_404(Factura, id=factura_id)
    if not factura.puede_eliminar(request.user):
        return HttpResponseForbidden("No estás autorizado para eliminar esta factura.")
    if request.method == "POST":
        factura.delete()
        return redirect('lista_facturas')
    return HttpResponseForbidden("Acción no permitida.")

