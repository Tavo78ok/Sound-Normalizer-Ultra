## 🎧 Sound Normalizer Ultra v1.0.0

Una herramienta potente y ligera diseñada para entusiastas del audio que buscan el volumen perfecto sin sacrificar la dinámica.

🚀 Características Principales:

Análisis Dual: Detecta el Mean Volume (volumen medio) en dB para conocer el estado real de tus archivos antes de procesarlos.

Normalización Inteligente (LUFS): Utiliza el estándar EBU R128, el mismo que emplean gigantes como Spotify y YouTube, para asegurar que todas tus canciones suenen con la misma intensidad percibida.

Control de Carátulas: Permite incrustar manualmente imágenes (.jpg, .png) directamente en los metadatos de tus MP3.

Motor Robusto: Basado en comandos directos de FFmpeg, garantizando estabilidad y compatibilidad con múltiples formatos (MP3, WAV, FLAC).

⚙️ Cómo funciona la tecnología:

A diferencia de la normalización de picos tradicional que solo evita que el audio "sature", este programa analiza la sonoridad (Loudness). Al establecer un objetivo de -14 LUFS (ajustable por el usuario), el software equilibra la potencia de salida para que no tengas que subir o bajar el volumen entre canciones de distintos álbumes.

### 📦 Instalación
1. Descarga el archivo `.deb` adjunto abajo.
2. Instálalo abriéndolo con tu gestor de software o vía terminal:
   ```bash
   sudo dpkg -i sound-normalizer-ultra_1.0_amd64.deb
   sudo apt install -f

🛠 Requisitos:
FFmpeg instalado en el sistema.

<img width="1440" height="900" alt="Captura de pantalla_2026-03-07_21-20-40" src="https://github.com/user-attachments/assets/f1fb6aed-65a4-4549-8d67-377b501921fa" />


