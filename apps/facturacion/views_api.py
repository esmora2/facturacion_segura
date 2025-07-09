from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework import viewsets
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

class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in ['Administrador', 'Ventas']:
            return Factura.objects.all()
        return Factura.objects.none()

    def perform_create(self, serializer):
        serializer.save(creador=self.request.user)

    def perform_destroy(self, instance):
        if not instance.puede_eliminar(self.request.user):
            raise PermissionDenied("No tienes permiso para eliminar esta factura")
        instance.delete()

    @action(detail=True, methods=['post'])
    def send_pdf(self, request, pk=None):
        factura = self.get_object()
        if not factura.cliente:
            return Response({"error": "No se ha asignado un cliente a esta factura"}, status=400)
        cliente = factura.cliente

        # Generar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Encabezado
        elements.append(Paragraph("Sistema de Facturación Segura", styles['Title']))
        elements.append(Paragraph("RUC: 123456789 | Dirección: Av. Ejemplo 123, Ciudad", styles['Normal']))
        elements.append(Paragraph("Teléfono: (123) 456-7890 | Email: contacto@facturasegura.com", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Información de la factura
        elements.append(Paragraph(f"Factura #{factura.id}", styles['Heading2']))
        elements.append(Paragraph(f"Fecha: {factura.fecha.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"Cliente: {cliente.nombre}", styles['Normal']))
        elements.append(Paragraph(f"Email: {cliente.email}", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Tabla de ítems
        data = [['Descripción', 'Cantidad', 'Precio Unitario', 'Subtotal']]
        total = 0
        for item in factura.items.all():
            precio_unitario = item.producto.precio  # Asume que Producto tiene un campo precio
            subtotal = item.cantidad * precio_unitario
            total += subtotal
            data.append([
                item.producto.nombre,
                str(item.cantidad),
                f"${precio_unitario:.2f}",
                f"${subtotal:.2f}"
            ])
        data.append(['', '', 'Total', f"${total:.2f}"])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -2), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
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

        # Enviar correo
        email = EmailMessage(
            subject=f"Factura #{factura.id}",
            body="Adjunto encontrarás tu factura.",
            from_email=settings.EMAIL_HOST_USER,
            to=[cliente.email],
        )
        email.attach(f"factura_{factura.id}.pdf", pdf, "application/pdf")
        email.send()

        return Response({"status": "Factura enviada al correo"})

    @action(detail=False, methods=['get'])
    def metrics(self, request):
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