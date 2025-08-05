"""
Vista para documentar todos los endpoints de la API.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_documentation(request):
    """
    Endpoint que documenta todas las rutas disponibles en la API.
    """
    documentation = {
        "message": "API de Facturación Segura - Documentación",
        "version": "1.0",
        "endpoints": {
            "autenticacion": {
                "login": {
                    "url": "/api/auth/login/",
                    "method": "POST",
                    "description": "Login con username y password",
                    "body": {
                        "username": "string",
                        "password": "string"
                    },
                    "response": {
                        "token": "string",
                        "user": {
                            "id": "integer",
                            "username": "string",
                            "email": "string",
                            "role": "string",
                            "is_active": "boolean"
                        }
                    }
                },
                "token": {
                    "url": "/api/token/",
                    "method": "POST",
                    "description": "Obtener token (endpoint estándar de DRF)",
                    "body": {
                        "username": "string",
                        "password": "string"
                    }
                },
                "me": {
                    "url": "/api/me/",
                    "method": "GET",
                    "description": "Obtener información del usuario autenticado",
                    "headers": {
                        "Authorization": "Token <your_token>"
                    }
                }
            },
            "clientes": {
                "list": {
                    "url": "/api/clientes/",
                    "method": "GET",
                    "description": "Listar todos los clientes",
                    "permission": "Administrador, Secretario, Ventas"
                },
                "create": {
                    "url": "/api/clientes/",
                    "method": "POST",
                    "description": "Crear nuevo cliente",
                    "permission": "Administrador, Secretario"
                },
                "detail": {
                    "url": "/api/clientes/{id}/",
                    "methods": ["GET", "PUT", "PATCH", "DELETE"],
                    "description": "Operaciones sobre un cliente específico"
                },
                "eliminar_con_motivo": {
                    "url": "/api/clientes/{id}/eliminar-con-motivo/",
                    "method": "POST",
                    "description": "Eliminar cliente con motivo de auditoría",
                    "body": {
                        "motivo": "string (requerido)"
                    }
                }
            },
            "productos": {
                "list": {
                    "url": "/api/productos/",
                    "method": "GET",
                    "description": "Listar todos los productos"
                },
                "create": {
                    "url": "/api/productos/",
                    "method": "POST",
                    "description": "Crear nuevo producto"
                },
                "detail": {
                    "url": "/api/productos/{id}/",
                    "methods": ["GET", "PUT", "PATCH", "DELETE"],
                    "description": "Operaciones sobre un producto específico"
                }
            },
            "facturas": {
                "list": {
                    "url": "/api/facturas/",
                    "method": "GET",
                    "description": "Listar todas las facturas",
                    "permission": "Administrador, Ventas"
                },
                "create": {
                    "url": "/api/facturas/",
                    "method": "POST",
                    "description": "Crear nueva factura"
                },
                "detail": {
                    "url": "/api/facturas/{id}/",
                    "methods": ["GET", "PUT", "PATCH", "DELETE"],
                    "description": "Operaciones sobre una factura específica"
                },
                "anular": {
                    "url": "/api/facturas/{id}/anular/",
                    "method": "POST",
                    "description": "Anular una factura (restituye stock automáticamente)",
                    "note": "Solo facturas EMITIDAS o PAGADAS pueden anularse"
                },
                "marcar_pagada": {
                    "url": "/api/facturas/{id}/marcar_pagada/",
                    "method": "POST",
                    "description": "Marcar factura como pagada"
                },
                "emitir": {
                    "url": "/api/facturas/{id}/emitir/",
                    "method": "POST",
                    "description": "Emitir factura (descontar stock)"
                },
                "generar_pdf": {
                    "url": "/api/facturas/{id}/generar_pdf/",
                    "method": "GET",
                    "description": "Generar PDF de la factura"
                }
            },
            "usuarios": {
                "list": {
                    "url": "/api/usuarios/",
                    "method": "GET",
                    "description": "Listar usuarios",
                    "permission": "Solo Administradores"
                },
                "manage": {
                    "url": "/api/usuarios/{id}/",
                    "methods": ["GET", "PUT", "PATCH", "DELETE"],
                    "description": "Gestión de usuarios",
                    "permission": "Solo Administradores"
                }
            },
            "auditorias": {
                "logs": {
                    "url": "/api/logs/",
                    "method": "GET",
                    "description": "Ver logs de auditoría",
                    "permission": "Administrador"
                }
            }
        },
        "authentication": {
            "type": "Token Authentication",
            "header": "Authorization: Token <your_token>",
            "note": "Obtén tu token usando /api/auth/login/ o /api/token/"
        },
        "common_errors": {
            "401": "No autenticado - Falta token o token inválido",
            "403": "Sin permisos - El usuario no tiene permisos para esta acción",
            "404": "No encontrado - El recurso no existe o la URL es incorrecta",
            "400": "Datos inválidos - Revisa el formato de los datos enviados"
        }
    }
    
    return Response(documentation, status=status.HTTP_200_OK)
