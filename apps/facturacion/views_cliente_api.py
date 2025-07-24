from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.clientes.authentication import ClienteTokenAuthentication
from .models import Factura
from .serializers import FacturaSerializer

@api_view(['GET'])
@authentication_classes([ClienteTokenAuthentication])
@permission_classes([IsAuthenticated])
def facturas_cliente_token(request):
    try:
        cliente = request.user  # El autenticador retorna el cliente
        facturas = Factura.objects.filter(cliente=cliente)
        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
