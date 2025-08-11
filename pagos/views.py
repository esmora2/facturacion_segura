"""Vistas para la app de pagos."""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.usuarios.decorators import role_required
from .models import Pago


@login_required
@role_required('Administrador', 'Pagos')  # Administradores y usuarios con rol Pagos
def lista_pagos_pendientes(request):
    """Vista web para mostrar pagos pendientes de validación."""
    pagos_pendientes = Pago.objects.filter(estado='pendiente').select_related(
        'factura', 'pagado_por'
    ).order_by('-fecha_pago')
    
    context = {
        'pagos_pendientes': pagos_pendientes,
        'total_pendientes': pagos_pendientes.count()
    }
    
    return render(request, 'pagos/lista_pagos_pendientes.html', context)


@login_required
@role_required('Administrador', 'Pagos')
def detalle_pago(request, pago_id):
    """Vista web para mostrar detalle de un pago."""
    pago = get_object_or_404(Pago, id=pago_id)
    
    context = {
        'pago': pago,
        'puede_validar': pago.puede_validar_usuario(request.user) and pago.esta_pendiente
    }
    
    return render(request, 'pagos/detalle_pago.html', context)


@login_required
@role_required('Administrador', 'Pagos')
@require_POST
def validar_pago(request, pago_id):
    """Vista para aprobar o rechazar un pago."""
    pago = get_object_or_404(Pago, id=pago_id)
    
    if not pago.puede_validar_usuario(request.user):
        messages.error(request, "No tienes permisos para validar este pago.")
        return JsonResponse({'error': 'Permisos insuficientes'}, status=403)
    
    if not pago.esta_pendiente:
        messages.error(request, "Este pago ya ha sido validado.")
        return JsonResponse({'error': 'Pago ya validado'}, status=400)
    
    accion = request.POST.get('accion')
    motivo = request.POST.get('motivo', '')
    
    try:
        if accion == 'aprobar':
            pago.aprobar(request.user)
            messages.success(request, f'Pago #{pago.id} aprobado exitosamente.')
            
            # Enviar notificación por email al cliente
            _enviar_notificacion_aprobacion(pago)
            
            return JsonResponse({
                'success': True, 
                'message': 'Pago aprobado exitosamente',
                'nuevo_estado': 'aprobado'
            })
            
        elif accion == 'rechazar':
            if not motivo.strip():
                messages.error(request, "El motivo es requerido para rechazar un pago.")
                return JsonResponse({'error': 'Motivo requerido'}, status=400)
            
            pago.rechazar(request.user, motivo)
            messages.success(request, f'Pago #{pago.id} rechazado.')
            
            # Enviar notificación por email al cliente
            _enviar_notificacion_rechazo(pago, motivo)
            
            return JsonResponse({
                'success': True, 
                'message': 'Pago rechazado',
                'nuevo_estado': 'rechazado'
            })
            
        else:
            messages.error(request, "Acción no válida.")
            return JsonResponse({'error': 'Acción no válida'}, status=400)
            
    except Exception as e:
        messages.error(request, f"Error al validar el pago: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def mis_pagos(request):
    """Vista para que los usuarios vean sus propios pagos."""
        # Verificar que el usuario sea un cliente
    if not hasattr(request.user, 'role') or request.user.role != 'Cliente':
        return render(request, 'pagos/mis_pagos.html', {
            'error': 'Esta página es solo para clientes.'
        })
    
    # El cliente es el usuario autenticado
    cliente = request.user
    pagos = Pago.objects.filter(pagado_por=cliente).select_related(
        'factura', 'validado_por'
    ).order_by('-fecha_pago')
    
    context = {
        'pagos': pagos,
        'cliente': cliente
    }
    
    return render(request, 'pagos/mis_pagos.html', context)


def _enviar_notificacion_aprobacion(pago):
    """Enviar notificación de aprobación al cliente."""
    try:
        asunto = f"Pago Aprobado - Factura #{pago.factura.numero_factura or pago.factura.id}"
        mensaje = f"""
Estimado/a {pago.pagado_por.nombre},

Su pago ha sido APROBADO exitosamente.

Detalles del pago:
- Pago ID: #{pago.id}
- Factura: #{pago.factura.numero_factura or pago.factura.id}
- Monto: ${pago.monto}
- Tipo de pago: {pago.get_tipo_pago_display()}
- Número de transacción: {pago.numero_transaccion}
- Fecha de aprobación: {pago.fecha_validacion.strftime('%d/%m/%Y %H:%M')}

La factura ahora aparece como PAGADA en el sistema.

Gracias por su pago.

Sistema de Facturación Segura
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            [pago.pagado_por.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Error enviando email de aprobación: {e}")


def _enviar_notificacion_rechazo(pago, motivo):
    """Enviar notificación de rechazo al cliente."""
    try:
        asunto = f"Pago Rechazado - Factura #{pago.factura.numero_factura or pago.factura.id}"
        mensaje = f"""
Estimado/a {pago.pagado_por.nombre},

Su pago ha sido RECHAZADO.

Detalles del pago:
- Pago ID: #{pago.id}
- Factura: #{pago.factura.numero_factura or pago.factura.id}
- Monto: ${pago.monto}
- Tipo de pago: {pago.get_tipo_pago_display()}
- Número de transacción: {pago.numero_transaccion}
- Fecha de rechazo: {pago.fecha_validacion.strftime('%d/%m/%Y %H:%M')}

Motivo del rechazo:
{motivo}

Por favor, revise la información y vuelva a intentar el pago o contacte con nuestro equipo de soporte.

Sistema de Facturación Segura
        """
        
        send_mail(
            asunto,
            mensaje,
            settings.EMAIL_HOST_USER,
            [pago.pagado_por.email],
            fail_silently=True
        )
    except Exception as e:
        print(f"Error enviando email de rechazo: {e}")
