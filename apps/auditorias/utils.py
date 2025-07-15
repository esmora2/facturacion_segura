# apps/auditorias/utils.py

from .models import LogAuditoria

def registrar_log_eliminacion(usuario, modelo_afectado, objeto_id, descripcion_objeto, motivo):
    LogAuditoria.objects.create(
        usuario=usuario,
        modelo_afectado=modelo_afectado,
        objeto_id=objeto_id,
        descripcion_objeto=descripcion_objeto,
        motivo=motivo
    )
