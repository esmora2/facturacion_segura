# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0006_alter_cliente_options_alter_cliente_managers_and_more'),
    ]

    operations = [
        # Agregar campos de autenticación a Cliente
        migrations.AddField(
            model_name='cliente',
            name='username',
            field=models.CharField(blank=True, max_length=150, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='password',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='role',
            field=models.CharField(default='Cliente', max_length=20),
        ),
        migrations.AddField(
            model_name='cliente',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        # Actualizar el campo activo existente como alias para is_active
        migrations.AlterField(
            model_name='cliente',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
