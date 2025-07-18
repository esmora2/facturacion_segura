# Generated by Django 5.2.4 on 2025-07-09 01:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('Administrador', 'Administrador'), ('Secretario', 'Secretario'), ('Bodega', 'Bodega'), ('Ventas', 'Ventas')], max_length=20, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='cliente',
            name='roles',
        ),
        migrations.AddField(
            model_name='cliente',
            name='roles',
            field=models.ManyToManyField(to='clientes.role'),
        ),
    ]
