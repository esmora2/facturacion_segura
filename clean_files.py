"""Script para limpiar espacios en blanco trailing y añadir newlines finales."""

import os
import re


def clean_file(file_path):
    """Limpia espacios en blanco trailing y añade newline final."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remover trailing whitespace de cada línea
        cleaned_lines = [line.rstrip() + '\n' for line in lines]
        
        # Asegurar que el archivo termine con newline
        if cleaned_lines and not cleaned_lines[-1].endswith('\n'):
            cleaned_lines[-1] += '\n'
        elif cleaned_lines and cleaned_lines[-1].strip() == '':
            # Remover líneas vacías al final
            while cleaned_lines and cleaned_lines[-1].strip() == '':
                cleaned_lines.pop()
            if cleaned_lines:
                cleaned_lines[-1] = cleaned_lines[-1].rstrip() + '\n'
        
        # Si no hay líneas o la última línea no es vacía, añadir newline
        if not cleaned_lines or cleaned_lines[-1].strip() != '':
            if cleaned_lines:
                cleaned_lines[-1] = cleaned_lines[-1].rstrip() + '\n'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        print(f"Limpiado: {file_path}")
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")


def main():
    """Función principal."""
    # Lista de archivos para limpiar
    files_to_clean = [
        'apps/clientes/serializers.py',
        'apps/clientes/views_api.py',
        'apps/facturacion/models.py',
        'apps/facturacion/serializers.py',
        'apps/facturacion/urls_cliente_api.py',
        'apps/facturacion/views_api.py',
        'apps/facturacion/views_cliente_api.py',
        'apps/productos/views_api.py',
        'apps/usuarios/models.py',
        'apps/usuarios/permissions.py',
        'apps/usuarios/serializers.py',
        'apps/usuarios/views_api.py',
        'apps/usuarios/test_validate_password.py',
        'apps/usuarios/middleware.py',
    ]
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            clean_file(file_path)
        else:
            print(f"Archivo no encontrado: {file_path}")


if __name__ == "__main__":
    main()
