"""Documentación API para el módulo de pagos."""

from django.shortcuts import render
from django.http import JsonResponse

def api_documentation_pagos(request):
    """Documentación de la API de pagos."""
    
    documentation = {
        "title": "API de Pagos - Sistema de Facturación Segura",
        "version": "1.0",
        "description": "Documentación completa de la API para gestión de pagos de facturas",
        
        "autenticacion": {
            "sistema_usuarios": {
                "descripcion": "Para usuarios del sistema (Administrador, Pagos)",
                "header": "Authorization: Token <your_user_token>",
                "endpoints": ["/api/pagos/", "/api/pagos/pendientes/", "/api/pagos/estadisticas/"]
            },
            "clientes": {
                "descripcion": "Para clientes usando token personalizado",
                "header": "Authorization: Token <cliente_token>",
                "endpoints": ["/api/cliente/registrar-pago/", "/api/cliente/mis-pagos/", "/api/cliente/facturas-pendientes/"]
            }
        },
        
        "endpoints": {
            "administracion_pagos": {
                "listar_pagos": {
                    "url": "/api/pagos/",
                    "method": "GET",
                    "descripcion": "Listar todos los pagos",
                    "permisos": "Administrador, Pagos"
                },
                "crear_pago": {
                    "url": "/api/pagos/",
                    "method": "POST",
                    "descripcion": "Crear un nuevo pago (solo para testing)",
                    "permisos": "Administrador, Pagos",
                    "body": {
                        "factura": "int (ID de la factura)",
                        "tipo_pago": "string (efectivo, tarjeta, transferencia, cheque)",
                        "monto": "decimal",
                        "numero_transaccion": "string",
                        "observaciones": "string (opcional)",
                        "pagado_por": "int (ID del cliente)"
                    }
                },
                "detalle_pago": {
                    "url": "/api/pagos/{id}/",
                    "method": "GET",
                    "descripcion": "Obtener detalle completo de un pago",
                    "permisos": "Administrador, Pagos"
                },
                "pagos_pendientes": {
                    "url": "/api/pagos/pendientes/",
                    "method": "GET",
                    "descripcion": "Listar solo pagos pendientes de validación",
                    "permisos": "Administrador, Pagos"
                },
                "validar_pago": {
                    "url": "/api/pagos/{id}/validar/",
                    "method": "POST",
                    "descripcion": "Aprobar o rechazar un pago",
                    "permisos": "Administrador, Pagos",
                    "body": {
                        "accion": "string (aprobar o rechazar)",
                        "motivo": "string (requerido para rechazar)"
                    }
                },
                "estadisticas": {
                    "url": "/api/pagos/estadisticas/",
                    "method": "GET",
                    "descripcion": "Obtener estadísticas de pagos",
                    "permisos": "Administrador, Pagos"
                }
            },
            
            "api_clientes": {
                "registrar_pago": {
                    "url": "/api/cliente/registrar-pago/",
                    "method": "POST",
                    "descripcion": "Registrar un nuevo pago (para clientes)",
                    "autenticacion": "Token de cliente",
                    "body": {
                        "factura": "int (ID de la factura a pagar)",
                        "tipo_pago": "string (efectivo, tarjeta, transferencia, cheque)",
                        "monto": "decimal (debe coincidir con el total de la factura)",
                        "numero_transaccion": "string (código de comprobante)",
                        "observaciones": "string (opcional)"
                    },
                    "validaciones": [
                        "Solo puede pagar sus propias facturas",
                        "La factura debe estar en estado EMITIDA",
                        "El monto debe coincidir con el total de la factura"
                    ]
                },
                "mis_pagos": {
                    "url": "/api/cliente/mis-pagos/",
                    "method": "GET",
                    "descripcion": "Consultar pagos propios del cliente",
                    "autenticacion": "Token de cliente"
                },
                "facturas_pendientes": {
                    "url": "/api/cliente/facturas-pendientes/",
                    "method": "GET",
                    "descripcion": "Obtener facturas del cliente pendientes de pago",
                    "autenticacion": "Token de cliente"
                }
            }
        },
        
        "modelos": {
            "pago": {
                "campos": {
                    "id": "Identificador único del pago",
                    "factura": "ID de la factura asociada",
                    "tipo_pago": "Tipo de pago (efectivo, tarjeta, transferencia, cheque)",
                    "monto": "Monto del pago",
                    "numero_transaccion": "Código o comprobante de la transacción",
                    "observaciones": "Comentarios opcionales",
                    "estado": "Estado del pago (pendiente, aprobado, rechazado)",
                    "pagado_por": "ID del cliente que realizó el pago",
                    "validado_por": "ID del usuario que validó (null si pendiente)",
                    "fecha_pago": "Fecha de registro del pago",
                    "fecha_validacion": "Fecha de validación (null si pendiente)"
                },
                "estados": {
                    "pendiente": "Pago registrado, esperando validación",
                    "aprobado": "Pago aprobado, factura marcada como pagada",
                    "rechazado": "Pago rechazado, factura sigue pendiente"
                }
            }
        },
        
        "ejemplos": {
            "registrar_pago_cliente": {
                "descripcion": "Ejemplo para que un cliente registre un pago",
                "request": {
                    "method": "POST",
                    "url": "/api/cliente/registrar-pago/",
                    "headers": {
                        "Authorization": "Token <cliente_token>",
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "factura": 1,
                        "tipo_pago": "transferencia",
                        "monto": "150.00",
                        "numero_transaccion": "TRF-2025-001234",
                        "observaciones": "Pago realizado desde banco en línea"
                    }
                },
                "response": {
                    "success": True,
                    "message": "Pago registrado exitosamente. Está pendiente de validación.",
                    "pago": {
                        "id": 1,
                        "factura": 1,
                        "tipo_pago": "transferencia",
                        "monto": "150.00",
                        "estado": "pendiente",
                        "fecha_pago": "2025-08-07T10:30:00Z"
                    }
                }
            },
            
            "validar_pago_admin": {
                "descripcion": "Ejemplo para que un administrador apruebe un pago",
                "request": {
                    "method": "POST",
                    "url": "/api/pagos/1/validar/",
                    "headers": {
                        "Authorization": "Token <admin_token>",
                        "Content-Type": "application/json"
                    },
                    "body": {
                        "accion": "aprobar"
                    }
                },
                "response": {
                    "success": True,
                    "message": "Pago #1 aprobado exitosamente",
                    "pago_id": 1,
                    "nuevo_estado": "aprobado",
                    "fecha_validacion": "2025-08-07T11:00:00Z"
                }
            }
        },
        
        "flujo_trabajo": {
            "paso_1": "Cliente registra pago via API con su token personalizado",
            "paso_2": "Pago queda en estado 'pendiente'",
            "paso_3": "Usuario con rol 'Pagos' o 'Administrador' revisa el pago",
            "paso_4": "Usuario valida (aprueba/rechaza) el pago",
            "paso_5": "Si se aprueba: factura pasa a estado 'PAGADA'",
            "paso_6": "Si se rechaza: factura mantiene estado 'EMITIDA'",
            "paso_7": "Cliente recibe notificación por email del resultado"
        },
        
        "codigos_error": {
            "400": "Datos inválidos o faltantes",
            "401": "No autenticado o token inválido",
            "403": "Sin permisos para realizar la acción",
            "404": "Recurso no encontrado",
            "500": "Error interno del servidor"
        }
    }
    
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(documentation)
    
    return render(request, 'pagos/api_documentation.html', {
        'documentation': documentation
    })
