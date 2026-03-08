#!/usr/bin/env python3
import sys
import os

def diagnostico():
    print("--- AUTO-DIAGNÓSTICO SISTEMAS DE SOPORTE VITAL OOP ---")
    try:
        import pygame
        print("[OK] Motor Pygame interactivo detectado.")
    except ImportError:
        print("[FAIL] Pygame no está instalado. Ejecute: pip install -r requirements.txt")
        sys.exit(1)

    try:
        from database import base_de_datos
        print(f"[OK] Base de datos persistente vinculada. ({len(base_de_datos)} registros vitales)")
    except ImportError as e:
        print(f"[FAIL] Error vinculando Database: {e}")
        sys.exit(1)

    try:
        from engine import Engine
        print("[OK] Engine Core gameloop ensamblado e instanciado.")
    except ImportError as e:
        print(f"[FAIL] Error vinculando Engine: {e}")
        sys.exit(1)

    try:
        from entities import Entity, ECGMonitor, TimerBar
        print("[OK] Entities (UI Componentes matemáticos) listos para Renderizaddo.")
    except ImportError as e:
        print(f"[FAIL] Error vinculando Entidades: {e}")
        sys.exit(1)

    try:
        from assets import Assets
        print("[OK] Módulo Assets con Auto-Generación visual procedural listos.")
    except ImportError as e:
        print(f"[FAIL] Error vinculando Assets: {e}")
        sys.exit(1)
        
    print("--- DIAGNÓSTICO EXITOSO. INICIANDO JUEGO OOP... ---")

if __name__ == "__main__":
    if "pygame" not in sys.modules:
        diagnostico()
    from engine import Engine
    # Resolutions at native HD matching standard desktop sizes nicely
    juego = Engine(1200, 800)
    juego.run()
