"""Script para crear datos de prueba para el sistema de pagos."""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.usuarios.models import User
from apps.clientes.models import Cliente, ClienteToken
from apps.productos.models import Producto
from apps.facturacion.models import Factura, FacturaItem
from pagos.models import Pago
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Crear datos de prueba para el sistema de pagos'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Creando datos de prueba para el sistema de pagos...')
        
        # 1. Crear usuarios con diferentes roles
        self.stdout.write('👥 Creando usuarios...')
        
        # Usuario administrador
        admin_user, created = User.objects.get_or_create(
            username='admin_pagos',
            defaults={
                'email': 'admin@facturacion.com',
                'first_name': 'Admin',
                'last_name': 'Pagos',
                'role': 'Administrador',
                'is_staff': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'✅ Usuario administrador creado: {admin_user.username}')
        
        # Usuario con rol Pagos
        pagos_user, created = User.objects.get_or_create(
            username='validador_pagos',
            defaults={
                'email': 'validador@facturacion.com',
                'first_name': 'Validador',
                'last_name': 'Pagos',
                'role': 'Pagos',
                'is_staff': True
            }
        )
        if created:
            pagos_user.set_password('pagos123')
            pagos_user.save()
            self.stdout.write(f'✅ Usuario validador de pagos creado: {pagos_user.username}')
        
        # Usuario vendedor
        vendedor_user, created = User.objects.get_or_create(
            username='vendedor1',
            defaults={
                'email': 'vendedor@facturacion.com',
                'first_name': 'Juan',
                'last_name': 'Vendedor',
                'role': 'Ventas'
            }
        )
        if created:
            vendedor_user.set_password('vendedor123')
            vendedor_user.save()
            self.stdout.write(f'✅ Usuario vendedor creado: {vendedor_user.username}')
        
        # 2. Crear clientes
        self.stdout.write('👤 Creando clientes...')
        
        cliente1, created = Cliente.objects.get_or_create(
            email='cliente1@email.com',
            defaults={
                'nombre': 'María García',
                'telefono': '+1234567890',
                'activo': True
            }
        )
        if created:
            self.stdout.write(f'✅ Cliente creado: {cliente1.nombre}')
        
        cliente2, created = Cliente.objects.get_or_create(
            email='cliente2@email.com',
            defaults={
                'nombre': 'Carlos López',
                'telefono': '+0987654321',
                'activo': True
            }
        )
        if created:
            self.stdout.write(f'✅ Cliente creado: {cliente2.nombre}')
        
        # Crear tokens para clientes
        token1, created = ClienteToken.objects.get_or_create(cliente=cliente1)
        if created:
            self.stdout.write(f'✅ Token de cliente creado: {token1.key}')
        
        token2, created = ClienteToken.objects.get_or_create(cliente=cliente2)
        if created:
            self.stdout.write(f'✅ Token de cliente creado: {token2.key}')
        
        # 3. Crear productos
        self.stdout.write('📦 Creando productos...')
        
        producto1, created = Producto.objects.get_or_create(
            nombre='Laptop Dell',
            defaults={
                'descripcion': 'Laptop Dell Inspiron 15',
                'stock': 10,
                'precio': Decimal('1200.00')
            }
        )
        if created:
            self.stdout.write(f'✅ Producto creado: {producto1.nombre}')
        
        producto2, created = Producto.objects.get_or_create(
            nombre='Mouse Inalámbrico',
            defaults={
                'descripcion': 'Mouse inalámbrico Logitech',
                'stock': 50,
                'precio': Decimal('25.00')
            }
        )
        if created:
            self.stdout.write(f'✅ Producto creado: {producto2.nombre}')
        
        # 4. Crear facturas
        self.stdout.write('🧾 Creando facturas...')
        
        # Factura 1 para cliente 1
        factura1, created = Factura.objects.get_or_create(
            cliente=cliente1,
            creador=vendedor_user,
            defaults={
                'estado': 'EMITIDA',
                'numero_factura': 'FAC-000001'
            }
        )
        if created:
            # Agregar items a la factura
            FacturaItem.objects.create(
                factura=factura1,
                producto=producto1,
                cantidad=1
            )
            factura1.calcular_totales()
            factura1.save()
            self.stdout.write(f'✅ Factura creada: {factura1.numero_factura} - Total: ${factura1.total}')
        
        # Factura 2 para cliente 2
        factura2, created = Factura.objects.get_or_create(
            cliente=cliente2,
            creador=vendedor_user,
            defaults={
                'estado': 'EMITIDA',
                'numero_factura': 'FAC-000002'
            }
        )
        if created:
            # Agregar items a la factura
            FacturaItem.objects.create(
                factura=factura2,
                producto=producto2,
                cantidad=3
            )
            factura2.calcular_totales()
            factura2.save()
            self.stdout.write(f'✅ Factura creada: {factura2.numero_factura} - Total: ${factura2.total}')
        
        # 5. Crear pagos de ejemplo
        self.stdout.write('💳 Creando pagos de ejemplo...')
        
        # Pago pendiente 1
        pago1, created = Pago.objects.get_or_create(
            factura=factura1,
            pagado_por=cliente1,
            defaults={
                'tipo_pago': 'transferencia',
                'monto': factura1.total,
                'numero_transaccion': 'TRF-2025-001',
                'observaciones': 'Transferencia bancaria desde cuenta corriente',
                'estado': 'pendiente'
            }
        )
        if created:
            self.stdout.write(f'✅ Pago pendiente creado: #{pago1.id} - ${pago1.monto}')
        
        # Pago pendiente 2
        pago2, created = Pago.objects.get_or_create(
            factura=factura2,
            pagado_por=cliente2,
            defaults={
                'tipo_pago': 'tarjeta',
                'monto': factura2.total,
                'numero_transaccion': 'CARD-2025-002',
                'observaciones': 'Pago con tarjeta de crédito terminada en 1234',
                'estado': 'pendiente'
            }
        )
        if created:
            self.stdout.write(f'✅ Pago pendiente creado: #{pago2.id} - ${pago2.monto}')
        
        # Resumen final
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMEN DE DATOS CREADOS:')
        self.stdout.write('='*50)
        self.stdout.write(f'👥 Usuarios: {User.objects.count()}')
        self.stdout.write(f'👤 Clientes: {Cliente.objects.count()}')
        self.stdout.write(f'🔑 Tokens de cliente: {ClienteToken.objects.count()}')
        self.stdout.write(f'📦 Productos: {Producto.objects.count()}')
        self.stdout.write(f'🧾 Facturas: {Factura.objects.count()}')
        self.stdout.write(f'💳 Pagos: {Pago.objects.count()}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('🔐 CREDENCIALES DE ACCESO:')
        self.stdout.write('='*50)
        self.stdout.write('Admin: admin_pagos / admin123')
        self.stdout.write('Validador: validador_pagos / pagos123')
        self.stdout.write('Vendedor: vendedor1 / vendedor123')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('🔑 TOKENS DE CLIENTES:')
        self.stdout.write('='*50)
        for token in ClienteToken.objects.all():
            self.stdout.write(f'{token.cliente.nombre}: {token.key}')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('🚀 ENDPOINTS PARA TESTING:')
        self.stdout.write('='*50)
        self.stdout.write('📊 Panel admin: http://localhost:8000/admin/')
        self.stdout.write('🏠 Home: http://localhost:8000/')
        self.stdout.write('💳 Pagos pendientes: http://localhost:8000/pagos/pendientes/')
        self.stdout.write('📚 API Docs: http://localhost:8000/api/pagos/docs/')
        self.stdout.write('🔗 API Pagos: http://localhost:8000/api/pagos/')
        
        self.stdout.write('\n✅ ¡Datos de prueba creados exitosamente!')
        self.stdout.write('🧪 Ahora puedes probar el sistema de pagos completo.')
