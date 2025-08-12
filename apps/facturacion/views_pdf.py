"""
Views específicas para PDF de facturas con permisos de cliente.
"""

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

from .models import Factura
from .views_api import FacturaViewSet


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def factura_view_pdf(request, pk):
    """
    Visualizar PDF de la factura en el navegador.
    Permite acceso a:
    - Administradores y personal de Ventas: todas las facturas
    - Clientes: solo sus propias facturas
    """
    try:
        factura = Factura.objects.get(pk=pk)
    except Factura.DoesNotExist:
        return Response({"error": "Factura no encontrada"}, status=404)

    user = request.user

    # Verificar permisos de acceso
    if user.is_superuser or user.role in ['Administrador', 'Ventas']:
        # Administradores y Ventas pueden ver cualquier factura
        pass
    elif user.role == 'Cliente':
        # Los clientes solo pueden ver sus propias facturas
        if factura.cliente != user:
            raise PermissionDenied("Solo puedes acceder al PDF de tus propias facturas")
    else:
        raise PermissionDenied("No tienes permiso para acceder a este recurso")

    try:
        # Usar la función auxiliar del ViewSet para generar PDF
        viewset = FacturaViewSet()
        pdf = viewset.generar_pdf_factura(factura)

        # Crear respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')

        # Configurar headers para visualización en navegador
        filename = f"factura_{factura.numero_factura or factura.id}.pdf"
        response['Content-Disposition'] = f'inline; filename="{filename}"'

        return response

    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": "Error al generar el PDF"}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def factura_download_pdf(request, pk):
    """
    Descargar PDF de la factura.
    Permite acceso a:
    - Administradores y personal de Ventas: todas las facturas
    - Clientes: solo sus propias facturas
    """
    try:
        factura = Factura.objects.get(pk=pk)
    except Factura.DoesNotExist:
        return Response({"error": "Factura no encontrada"}, status=404)

    user = request.user

    # Verificar permisos de acceso
    if user.is_superuser or user.role in ['Administrador', 'Ventas']:
        # Administradores y Ventas pueden descargar cualquier factura
        pass
    elif user.role == 'Cliente':
        # Los clientes solo pueden descargar sus propias facturas
        if factura.cliente != user:
            raise PermissionDenied("Solo puedes descargar el PDF de tus propias facturas")
    else:
        raise PermissionDenied("No tienes permiso para acceder a este recurso")

    try:
        # Usar la función auxiliar del ViewSet para generar PDF
        viewset = FacturaViewSet()
        pdf = viewset.generar_pdf_factura(factura)

        # Crear respuesta HTTP con el PDF
        response = HttpResponse(pdf, content_type='application/pdf')

        # Configurar headers para descarga
        filename = f"factura_{factura.numero_factura or factura.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response

    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    except Exception as e:
        return Response({"error": "Error al generar el PDF"}, status=500)
