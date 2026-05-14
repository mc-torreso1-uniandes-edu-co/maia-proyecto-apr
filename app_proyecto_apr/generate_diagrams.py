#!/usr/bin/env python3
"""Genera PNG a partir de archivos .mmd usando Mermaid CLI (mmdc).

Uso:
  python generate_diagrams.py            # procesa .mmd en el mismo directorio
  python generate_diagrams.py --dir docs  # procesa .mmd en carpeta `docs`

Requiere: `mmdc` en PATH (instalar: `npm install -g @mermaid-js/mermaid-cli`).
"""
import argparse
import subprocess
from pathlib import Path
import shutil
import sys


def find_mmdc():
    return shutil.which("mmdc")


def generate(mmd_path: Path, mmdc_cmd: str):
    out = mmd_path.with_suffix(".png")
    try:
        subprocess.run([mmdc_cmd, "-i", str(mmd_path), "-o", str(out)], check=True)
        print(f"✓ Generado: {out.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error generando {mmd_path.name}: {e}")
        return False


def main():
    p = argparse.ArgumentParser(description="Generar PNGs desde archivos .mmd usando mmdc")
    p.add_argument("--dir", "-d", default='.', help="Directorio donde buscar archivos .mmd")
    args = p.parse_args()

    mmdc_cmd = find_mmdc()
    if not mmdc_cmd:
        print("Error: no se encontró `mmdc` en PATH. Instala con: npm install -g @mermaid-js/mermaid-cli")
        sys.exit(2)

    workdir = Path(args.dir)
    if not workdir.exists() or not workdir.is_dir():
        print(f"Error: directorio no válido: {workdir}")
        sys.exit(2)

    mmd_files = sorted(workdir.glob("*.mmd"))
    if not mmd_files:
        print(f"No se encontraron archivos .mmd en {workdir}")
        return

    failures = 0
    for m in mmd_files:
        ok = generate(m, mmdc_cmd)
        if not ok:
            failures += 1

    if failures:
        print(f"Terminado con {failures} errores")
        sys.exit(1)
    else:
        print("Todos los diagramas generados correctamente.")


if __name__ == '__main__':
    main()
