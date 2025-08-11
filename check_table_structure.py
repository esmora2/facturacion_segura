#!/usr/bin/env python3

import os
import sys
import django

# Configurar Django
sys.path.append('/home/erickxse/visual/woekspace2p/sistema-facturacion/facturacion_segura')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'facturacion_segura.settings')
django.setup()

from django.db import connection

# Obtener estructura de la tabla
cursor = connection.cursor()
cursor.execute("DESCRIBE clientes_cliente")
columns = cursor.fetchall()

print("Estructura actual de la tabla clientes_cliente:")
print("=" * 60)
for column in columns:
    print(f"Campo: {column[0]:<20} Tipo: {column[1]:<30} Null: {column[2]}")
print("=" * 60)
