# 🏥 Monitor Vital: Dra. Perfinka
## Juego Educativo de Anatomía Clínica

Versión Desktop para Windows/Mac/Linux usando Electron o Python

---

## 📋 Requisitos Previos

### Para Electron (Versión Recomendada - Web/Desktop)
- **Node.js LTS** (descargar de [nodejs.org](https://nodejs.org))
- No requiere experiencia en terminal avanzada

### Para Python (Versión Alternativa - Más Ligera)
- **Python 3.8+** (ya instalado en Windows 10+)
- Solo para usuarios que prefieran Python

---

## 🚀 OPCIÓN A: Electron (Recomendado para Presentación)

### Paso 1: Instalar Node.js
1. Ve a https://nodejs.org y descarga **LTS**
2. Ejecuta el instalador (Next → Next → Finish)
3. Abre PowerShell y verifica: `node -v` (debe mostrar versión)

### Paso 2: Preparar el Proyecto
```powershell
# Ve a la carpeta del proyecto
cd "C:\Users\adria\Desktop\Proyectos Personales"

# Instala dependencias
npm install

# (Opcional) Instala electron-builder para crear .exe
npm install electron-builder --save-dev
```

### Paso 3: Ejecutar en Desarrollo
```powershell
npm start
```
Se abrirá una ventana tipo aplicación de escritorio.

### Paso 4: Crear el Ejecutable (.exe)
```powershell
npm run build-win
```
Encontrarás el instalador en la carpeta `dist/`.

---

## 🐍 OPCIÓN B: Python (Más Fácil y Ligero)

### Paso 1: Instalar PyWebView
```powershell
pip install pywebview
```

### Paso 2: Ejecutar
```powershell
python run_game.py
```
¡Listo! Se abre como app de verdad.

---

## 📁 Estructura del Proyecto

```
Proyectos Personales/
├── index.html              # Interfaz del juego
├── style.css               # Estilos CRT
├── script.js               # Lógica del juego
├── doctor-happy.png        # Sprites
├── doctor-neutral.png
├── doctor-angry.png
├── main.js                 # Lanzador Electron
├── preload.js              # Seguridad Electron
├── package.json            # Configuración Node
├── run_game.py             # Lanzador Python
└── README.md               # Este archivo
```

---

## ⚙️ Cualquier Cosa que Necesites

- **Cambiar tamaño de ventana**: Edita `width` y `height` en `main.js` (línea 5-6)
- **Agregar icono**: Coloca `icon.png` en carpeta `assets/`
- **Modo examen (bloquear salida)**: En `main.js`, descomenta `kiosk: true` (línea 17)
- **Ver consola de errores**: En `main.js`, descomenta `win.webContents.openDevTools();` (línea 24)

---

## 🎮 Controles del Juego

1. Click en **"INICIAR TURNO"** para comenzar
2. Lee la pregunta
3. Selecciona opción (A/B/C/D)
4. Mira el ECG cambiar y escucha los sonidos
5. Dra. Perfinka reacciona con sus sprites

---

## 📦 Distribución

### Windows:
- **Instalador NSIS** (Setup.exe): `dist/Monitor Vital - Dra. Perfinka Setup 1.0.0.exe`
- **Portable** (Directo): `dist/Monitor Vital - Dra. Perfinka 1.0.0.exe`

### Mac/Linux:
- Seguir mismo pasos, cambiar `npm run build-win` por `npm run build-mac` o `build-linux`

---

## 🐛 Troubleshooting

| Problema | Solución |
|----------|----------|
| `npm: comando no encontrado` | Reinstalar Node.js, reiniciar PowerShell |
| `main.js not found` | Asegúrate de que main.js existe en la carpeta |
| `doctor-*.png no cargan` | Coloca las imágenes PNG en la misma carpeta que index.html |
| `Audio no funciona` | Click en botón de la app (browsers bloqueaban audio antes) |

---

## 🏆 Notas Finales

- El juego corre **100% offline** - no necesita internet
- Los sonidos se generan con **Web Audio API** (sintetizado, no archivos de audio)
- El ECG es **realista** (patrón P-QRS-T)
- Los sprites de Dra. Perfinka **cambian de expresión** según respuestas

---

**Versión**: 1.0.0  
**Autor**: Adrian  
**Año**: 2026
