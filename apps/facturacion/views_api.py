from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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
