
"""Vistas API para la app de auditorías."""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer


class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """API para consultar registros del log de auditoría (solo lectura)."""
    queryset = LogAuditoria.objects.all().order_by('-fecha_eliminacion')
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated]
