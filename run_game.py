#!/usr/bin/env python3
"""
Monitor Vital: Dra. Perfinka - Desktop App Launcher
Alternativa Python con PyWebView (más ligera que Electron)

Instalación:
  pip install pywebview

Uso:
  python run_game.py
"""

import webview
import os
import sys
from pathlib import Path

def main():
    # Obtiene la carpeta donde está este script
    base_path = Path(__file__).parent.absolute()
    html_file = base_path / 'index.html'
    
    # Verifica que el archivo HTML exista
    if not html_file.exists():
        print(f"❌ Error: No se encuentra {html_file}")
        sys.exit(1)
    
    print("🏥 Iniciando Monitor Vital: Dra. Perfinka...")
    
    # Crea la ventana de la app
    window = webview.create_window(
        title='Monitor Vital: Dra. Perfinka',
        url=f'file://{html_file}',
        width=1400,
        height=900,
        min_size=(1000, 700),
        fullscreen=False
    )
    
    # Inicia la aplicación
    webview.start(debug=False)

if __name__ == '__main__':
    main()
