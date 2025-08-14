#!/usr/bin/env python3
"""
Script para limpiar archivos de profiling antiguos de Silk
"""
import os
import glob
import time
from pathlib import Path

def clean_old_profiles(days=1, max_files=100):
    """
    Limpia archivos de profiling antiguos
    
    Args:
        days: Archivos más antiguos de X días serán eliminados
        max_files: Máximo número de archivos a mantener
    """
    profiles_dir = Path("profiles")
    
    if not profiles_dir.exists():
        print("Directorio profiles/ no encontrado")
        return
    
    # Obtener todos los archivos .prof
    prof_files = list(profiles_dir.glob("*.prof"))
    print(f"Encontrados {len(prof_files)} archivos de profiling")
    
    # Eliminar archivos antiguos
    cutoff_time = time.time() - (days * 24 * 60 * 60)
    deleted_count = 0
    
    for prof_file in prof_files:
        if prof_file.stat().st_mtime < cutoff_time:
            prof_file.unlink()
            deleted_count += 1
    
    print(f"Eliminados {deleted_count} archivos antiguos")
    
    # Si aún hay demasiados archivos, eliminar los más antiguos
    remaining_files = list(profiles_dir.glob("*.prof"))
    if len(remaining_files) > max_files:
        # Ordenar por fecha de modificación
        remaining_files.sort(key=lambda x: x.stat().st_mtime)
        # Eliminar los más antiguos
        to_delete = remaining_files[:-max_files]
        for prof_file in to_delete:
            prof_file.unlink()
        print(f"Eliminados {len(to_delete)} archivos adicionales para mantener máximo {max_files}")
    
    final_count = len(list(profiles_dir.glob("*.prof")))
    print(f"Archivos de profiling restantes: {final_count}")

if __name__ == "__main__":
    clean_old_profiles()
