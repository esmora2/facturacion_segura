# Generated by Django 5.2.4 on 2025-07-10 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0002_role_remove_cliente_roles_cliente_roles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='roles',
            field=models.ManyToManyField(blank=True, to='clientes.role'),
        ),
    ]
