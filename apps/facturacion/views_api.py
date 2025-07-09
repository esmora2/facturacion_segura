from django.core.mail import EmailMessage
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from .models import Factura
from .serializers import FacturaSerializer

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
        cliente = factura.cliente  # Asumiendo que se agrega relación con Cliente

        # Generar PDF
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Factura #{factura.id}")
        p.drawString(100, 730, f"Fecha: {factura.fecha}")
        p.drawString(100, 710, f"Cliente: {cliente.nombre}")
        p.drawString(100, 690, "Items:")
        y = 670
        for item in factura.items.all():
            p.drawString(120, y, f"{item.producto.nombre} x {item.cantidad}")
            y -= 20
        p.showPage()
        p.save()
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