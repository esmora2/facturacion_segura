from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Factura
from .serializers import FacturaSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def facturas_cliente_token(request):
    """
    Obtener facturas del cliente autenticado.
    Usa autenticación estándar de Django REST Framework.
    """
    try:
        cliente = request.user  # Usuario autenticado (debe ser un Cliente)
        
        # Verificar que el usuario sea un cliente
        if not hasattr(cliente, 'role') or cliente.role != 'Cliente':
            return Response({'error': 'Solo accesible para clientes'}, status=403)
        
        facturas = Factura.objects.filter(cliente=cliente)
        serializer = FacturaSerializer(facturas, many=True)
        return Response({
            'cliente_id': cliente.id,
            'cliente_nombre': cliente.nombre,
            'facturas': serializer.data
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)
