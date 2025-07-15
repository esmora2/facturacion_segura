from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from .models import Factura
from .serializers import FacturaSerializer
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.usuarios.permissions import FacturaPermission
from apps.auditorias.models import LogAuditoria


class FacturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el módulo de Facturación.
    Acceso permitido solo a: Administrador, Ventas
    """
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated, FacturaPermission]

    def _generar_pdf_factura(self, factura):
        """
        Función auxiliar para generar el PDF de una factura.
        Retorna el PDF como bytes.
        """
        if not factura.cliente:
            raise ValueError("No se ha asignado un cliente a esta factura")
        
        cliente = factura.cliente
        
        # Generar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Encabezado de la empresa
        elements.append(Paragraph("Sistema de Facturación Segura", styles['Title']))
        elements.append(Paragraph("RUC: 123456789 | Dirección: Av. Ejemplo 123, Ciudad", styles['Normal']))
        elements.append(Paragraph("Teléfono: (123) 456-7890 | Email: contacto@facturasegura.com", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Información de la factura
        numero_factura = factura.numero_factura if factura.numero_factura else f"#{factura.id}"
        elements.append(Paragraph(f"Factura {numero_factura}", styles['Heading2']))
        elements.append(Paragraph(f"Fecha: {factura.fecha.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"Estado: {factura.get_estado_display()}", styles['Normal']))
        elements.append(Paragraph(f"Cliente: {cliente.nombre}", styles['Normal']))
        elements.append(Paragraph(f"Email: {cliente.email}", styles['Normal']))
        if cliente.telefono:
            elements.append(Paragraph(f"Teléfono: {cliente.telefono}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Tabla de ítems
        data = [['Descripción', 'Cantidad', 'Precio Unitario', 'Subtotal']]
        subtotal = 0
        
        if factura.items.exists():
            for item in factura.items.all():
                precio_unitario = item.producto.precio
                item_subtotal = item.cantidad * precio_unitario
                subtotal += item_subtotal
                data.append([
                    item.producto.nombre,
                    str(item.cantidad),
                    f"${precio_unitario:.2f}",
                    f"${item_subtotal:.2f}"
                ])
        else:
            data.append(['Sin items', '', '', '$0.00'])
        
        # Calcular IVA y total
        iva = subtotal * factura.IVA_PORCENTAJE
        total = subtotal + iva
        
        # Filas de totales
        data.append(['', '', 'Subtotal', f"${subtotal:.2f}"])
        data.append(['', '', 'IVA (15%)', f"${iva:.2f}"])
        data.append(['', '', 'Total', f"${total:.2f}"])

        # Crear y estilizar tabla
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -4), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -4), colors.black),
            ('FONTNAME', (0, 1), (-1, -4), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -4), 10),
            # Estilo para las filas de totales
            ('BACKGROUND', (0, -3), (-1, -3), colors.lightgrey),  # Subtotal
            ('BACKGROUND', (0, -2), (-1, -2), colors.lightgrey),  # IVA
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkgrey),   # Total
            ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Pie de página
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("Gracias por su compra. Contáctenos para cualquier consulta.", styles['Normal']))

        # Generar el PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf

    def get_queryset(self):
        """
        Filtrar queryset basado en el rol del usuario.
        Solo Administradores y personal de Ventas pueden ver facturas.
        """
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Ventas']:
            return Factura.objects.all()
        return Factura.objects.none()

    def list(self, request, *args, **kwargs):
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'Ventas']):
            raise PermissionDenied("No tienes permiso para acceder a las facturas")
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(creador=self.request.user)

    def perform_update(self, serializer):
        """
        Solo permitir actualización si:
        - La factura está en borrador
        - El usuario es el creador o un Administrador
        """
        instance = self.get_object()
        if not instance.puede_editar_usuario(self.request.user):
            if not instance.puede_editar():
                raise PermissionDenied("No se puede editar una factura que ya ha sido emitida")
            else:
                raise PermissionDenied(
                    "Solo el creador de la factura o un Administrador pueden editarla"
                )
        serializer.save()

    def perform_partial_update(self, serializer):
        """
        Solo permitir actualización parcial si:
        - La factura está en borrador
        - El usuario es el creador o un Administrador
        """
        instance = self.get_object()
        if not instance.puede_editar_usuario(self.request.user):
            if not instance.puede_editar():
                raise PermissionDenied("No se puede editar una factura que ya ha sido emitida")
            else:
                raise PermissionDenied(
                    "Solo el creador de la factura o un Administrador pueden editarla"
                )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Eliminar una factura con validaciones de permisos y restauración de stock.
        Solo pueden eliminar:
        - El usuario que la creó
        - Un usuario con rol Administrador
        """
        # Verificar permisos de eliminación
        if not instance.puede_eliminar(self.request.user):
            raise PermissionDenied(
                "Solo el creador de la factura o un Administrador pueden eliminarla"
            )
        
        # Solo se pueden eliminar facturas en borrador
        if not instance.puede_editar():
            raise PermissionDenied(
                "No se puede eliminar una factura que ya ha sido emitida. "
                "Use la función 'anular' en su lugar."
            )
        
        # La eliminación restaurará automáticamente el stock a través del método delete() de FacturaItem
        instance.delete()

    @action(detail=True, methods=['post'])
    def send_pdf(self, request, pk=None):
        """Enviar factura por correo electrónico"""
        factura = self.get_object()
        
        try:
            # Generar PDF usando la función auxiliar
            pdf = self._generar_pdf_factura(factura)
            
            # Enviar correo
            email = EmailMessage(
                subject=f"Factura #{factura.numero_factura or factura.id}",
                body="Adjunto encontrarás tu factura.",
                from_email=settings.EMAIL_HOST_USER,
                to=[factura.cliente.email],
            )
            email.attach(f"factura_{factura.id}.pdf", pdf, "application/pdf")
            email.send()

            return Response({"status": "Factura enviada al correo"})
            
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Error al enviar el correo"}, status=500)

    @action(detail=True, methods=['get'])
    def view_pdf(self, request, pk=None):
        """Visualizar PDF de la factura en el navegador"""
        factura = self.get_object()
        
        try:
            # Generar PDF usando la función auxiliar
            pdf = self._generar_pdf_factura(factura)
            
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

    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """Descargar PDF de la factura"""
        factura = self.get_object()
        
        try:
            # Generar PDF usando la función auxiliar
            pdf = self._generar_pdf_factura(factura)
            
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

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        user = self.request.user
        if not (user.is_superuser or user.role in ['Administrador', 'Ventas']):
            raise PermissionDenied("No tienes permiso para acceder a las métricas de facturas")
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)
        facturas_por_dia = Factura.objects.filter(
            fecha__date__range=[start_date, end_date]
        ).values('fecha__date').annotate(count=Count('id')).order_by('fecha__date')

        labels = []
        data = []
        for entry in facturas_por_dia:
            labels.append(entry['fecha__date'].strftime('%Y-%m-%d'))
            data.append(entry['count'])

        return Response({
            'facturas_por_dia': {
                'labels': labels,
                'data': data
            }
        })

    @action(detail=True, methods=['post'])
    def emitir(self, request, pk=None):
        """
        Emitir una factura (cambiar de BORRADOR a EMITIDA).
        Solo el creador o un Administrador pueden emitir.
        """
        factura = self.get_object()
        
        # Verificar que la factura esté en estado BORRADOR
        if factura.estado != 'BORRADOR':
            return Response({
                "error": f"Solo se pueden emitir facturas en estado borrador. Estado actual: {factura.get_estado_display()}"
            }, status=400)
        
        # Verificar permisos de usuario (solo creador o admin pueden emitir)
        if not factura.puede_editar_usuario(request.user):
            return Response({
                "error": "Solo el creador de la factura o un Administrador pueden emitirla"
            }, status=403)
        
        # Verificar que la factura tenga al menos un item
        if not factura.items.exists():
            return Response({
                "error": "No se puede emitir una factura sin items"
            }, status=400)
        
        # Emitir la factura
        factura.emitir()
        
        return Response({
            "status": "Factura emitida correctamente",
            "factura_id": factura.id,
            "numero_factura": factura.numero_factura,
            "estado": factura.estado,
            "fecha_emision": factura.fecha.isoformat()
        })

    @action(detail=True, methods=['post'])
    def marcar_pagada(self, request, pk=None):
        """Marcar una factura como pagada"""
        factura = self.get_object()
        if factura.estado != 'EMITIDA':
            return Response({"error": "Solo se pueden marcar como pagadas las facturas emitidas"}, status=400)
        factura.marcar_pagada()
        return Response({"status": "Factura marcada como pagada"})

    @action(detail=True, methods=['post'], url_path='eliminar-con-motivo')
    def eliminar_con_motivo(self, request, pk=None):
        """
        Eliminar una factura con motivo, registrando en LogAuditoria.
        Solo el creador o Administrador pueden eliminar facturas en estado BORRADOR.
        """
        factura = self.get_object()
        motivo = request.data.get('motivo')

        if not motivo:
            return Response({'error': 'El motivo es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validaciones ya existentes:
        if not factura.puede_eliminar(request.user):
            return Response({'error': 'Solo el creador o un Administrador pueden eliminar la factura.'}, status=403)

        if not factura.puede_editar():
            return Response({'error': 'No se puede eliminar una factura ya emitida. Usa "anular" en su lugar.'}, status=403)

        # Registrar en auditoría antes de eliminar
        LogAuditoria.objects.create(
            modelo_afectado='Factura',
            objeto_id=factura.id,
            descripcion_objeto=str(factura),
            motivo=motivo,
            usuario=request.user
        )

        factura.delete()
        return Response({'mensaje': 'Factura eliminada y registrada en auditoría.'}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def anular_factura(self, request, pk=None):
        """
        Anular una factura y restituir automáticamente el stock.
        Solo facturas EMITIDAS o PAGADAS pueden anularse.
        Solo el creador o un Administrador pueden anularla.
        """
        factura = self.get_object()
        
        # Verificar permisos de usuario
        if not factura.puede_anular_usuario(request.user):
            if not factura.puede_anular():
                return Response({
                    "error": f"Esta factura no puede ser anulada. Estado actual: {factura.get_estado_display()}"
                }, status=400)
            else:
                return Response({
                    "error": "Solo el creador de la factura o un Administrador pueden anularla"
                }, status=403)
        
        # Obtener información de los productos antes de anular (para el response)
        items_info = []
        for item in factura.items.all():
            items_info.append({
                "producto": item.producto.nombre,
                "cantidad_restituida": item.cantidad,
                "stock_anterior": item.producto.stock,
                "stock_nuevo": item.producto.stock + item.cantidad
            })
        
        # Anular la factura (esto automáticamente restituye el stock)
        if factura.anular():
            return Response({
                "status": "Factura anulada correctamente",
                "factura_id": factura.id,
                "estado": factura.estado,
                "stock_restituido": items_info
            })
        else:
            return Response({
                "error": "No se pudo anular la factura"
            }, status=500)
