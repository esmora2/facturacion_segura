# Generated by Django 5.2.4 on 2025-07-09 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0003_alter_factura_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='estado',
            field=models.CharField(choices=[('BORRADOR', 'Borrador'), ('EMITIDA', 'Emitida'), ('PAGADA', 'Pagada'), ('ANULADA', 'Anulada')], default='BORRADOR', max_length=20),
        ),
        migrations.AddField(
            model_name='factura',
            name='numero_factura',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
