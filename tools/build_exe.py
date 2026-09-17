"""
Script para empaquetar Tomatito.exe con PyInstaller.
Ejecutar desde la raíz del proyecto:
    python tools/build_exe.py
"""

import subprocess
import shutil
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist", "Tomatito")

def main():
    print("=" * 50)
    print("  Tomatito — Build Script")
    print("=" * 50)

    # 1. Generar wallpaper si no existe
    wp = os.path.join(ROOT, "assets", "wallpaper", "default.jpg")
    if not os.path.isfile(wp):
        print("\n[1/3] Generando wallpaper genérico...")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "generate_wallpaper.py")], check=True)
    else:
        print("\n[1/3] Wallpaper ya existe. Saltando.")

    # 2. PyInstaller
    print("\n[2/3] Ejecutando PyInstaller...")
    spec = os.path.join(ROOT, "build.spec")
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", spec, "--noconfirm"],
        cwd=ROOT,
        check=True,
    )

    # 3. Copiar assets/
    print("\n[3/3] Copiando assets/ al directorio de distribución...")
    src_assets = os.path.join(ROOT, "assets")
    dst_assets = os.path.join(DIST, "assets")
    if os.path.isdir(dst_assets):
        shutil.rmtree(dst_assets)
    shutil.copytree(src_assets, dst_assets)

    print("\n" + "=" * 50)
    print("  ¡Build completado!")
    print(f"  Ejecutable: {DIST}\\Tomatito.exe")
    print("=" * 50)
    print("\nPara distribuir, copia la carpeta completa:")
    print(f"  {DIST}")

if __name__ == "__main__":
    main()
