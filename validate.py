"""
SCRIPT DE VALIDACIÓN - MicroExpr
Ejecutar antes de deployar: python validate.py
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Verifica versión de Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print("✅ Python", f"{version.major}.{version.minor}", "- OK")
        return True
    else:
        print("❌ Python 3.9+ requerido. Tienes:", f"{version.major}.{version.minor}")
        return False

def check_files():
    """Verifica archivos principales"""
    required = [
        'src/app.py',
        'src/config.py',
        'src/model.py',
        'src/preprocessing.py',
        'requirements.txt',
        '.streamlit/config.toml',
    ]
    
    all_ok = True
    for file in required:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - FALTA")
            all_ok = False
    
    return all_ok

def check_packages():
    """Verifica paquetes instalados"""
    packages = [
        'streamlit',
        'numpy',
        'pandas',
        'cv2',
        'sklearn',
        'PIL'
    ]
    
    all_ok = True
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg} instalado")
        except ImportError:
            print(f"❌ {pkg} NO instalado")
            all_ok = False
    
    return all_ok

def check_directories():
    """Verifica carpetas necesarias"""
    dirs = [
        'src',
        'models',
        'data',
        '.streamlit'
    ]
    
    all_ok = True
    for d in dirs:
        if Path(d).is_dir():
            print(f"✅ {d}/ existe")
        else:
            print(f"⚠️  {d}/ no existe (crear si es necesario)")
    
    return all_ok

def main():
    print("=" * 60)
    print("VALIDACIÓN DE MICROEXPR")
    print("=" * 60)
    print()
    
    checks = []
    
    print("1. Verificando Python...")
    checks.append(check_python_version())
    print()
    
    print("2. Verificando archivos...")
    checks.append(check_files())
    print()
    
    print("3. Verificando directorios...")
    checks.append(check_directories())
    print()
    
    print("4. Verificando paquetes instalados...")
    checks.append(check_packages())
    print()
    
    print("=" * 60)
    if all(checks):
        print("✅ VALIDACIÓN EXITOSA - Listo para deployar!")
    else:
        print("⚠️  Algunos checks fallaron. Revisar arriba.")
    print("=" * 60)

if __name__ == "__main__":
    main()
