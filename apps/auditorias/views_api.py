from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer

class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API para consultar registros del log de auditoría.
    Solo lectura.
    """
    queryset = LogAuditoria.objects.all().order_by('-fecha_eliminacion')  # ✅ corregido
    serializer_class = LogAuditoriaSerializer
    permission_classes = [IsAuthenticated]
