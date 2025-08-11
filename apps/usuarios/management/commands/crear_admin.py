"""
Comando de Django para crear un usuario administrador
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Crear un usuario administrador para gestionar el sistema'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Nombre de usuario')
        parser.add_argument('email', type=str, help='Email del usuario')
        parser.add_argument('--password', type=str, default='admin123', help='Contraseña (default: admin123)')
        parser.add_argument('--first_name', type=str, default='Admin', help='Nombre (default: Admin)')
        parser.add_argument('--last_name', type=str, default='Sistema', help='Apellido (default: Sistema)')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.ERROR(f'El usuario "{username}" ya existe')
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.ERROR(f'El email "{email}" ya está en uso')
            )
            return

        # Crear el usuario
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_staff=True,
                is_superuser=True
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Usuario administrador creado exitosamente:\n'
                    f'   - Username: {username}\n'
                    f'   - Email: {email}\n'
                    f'   - Password: {password}\n'
                    f'   - Nombre: {first_name} {last_name}\n'
                    f'   - Rol: admin\n'
                    f'   - Staff: Sí\n'
                    f'   - Superuser: Sí\n'
                    f'\n🔑 Este usuario tiene acceso completo al sistema.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear usuario: {str(e)}')
            )
