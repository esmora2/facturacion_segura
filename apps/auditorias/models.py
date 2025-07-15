from django.db import models
from django.conf import settings  # <- IMPORTANTE agregar esto

class LogAuditoria(models.Model):
    modelo_afectado = models.CharField(max_length=100)
    objeto_id = models.IntegerField()
    descripcion_objeto = models.TextField()
    motivo = models.TextField()
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_eliminacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.modelo_afectado} {self.objeto_id} eliminado por {self.usuario}"
