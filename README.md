# OBDou

Una utilidad diseñada para streamers de Twitch. Se conecta directamente a OBS Studio a través de WebSockets para automatizar e inicializar módulos interactivos en el momento exacto en que comenzás tu transmisión.

## Características Principales (Addons)

*   **Avatar Reactivo (`addons/reactivekb`)**: Un personaje estilo VTuber (renderizado en ventana con fondo croma) que reacciona a tus acciones en tiempo real.
    *   Seguimiento del mouse en pantalla.
    *   Detección de pulsaciones de teclado (teclado simple o completo direccional).
    *   *Novedad:* Detección de micrófono (volumen RMS) para animar la cabeza cuando hablás.
*   **TTS de Chat (`addons/tts`)**: Un bot de texto a voz que lee en voz alta los mensajes del chat de Twitch de tus espectadores, activado mediante un comando personalizable (ej. `!s`). Se inicia y detiene automáticamente con tu stream de OBS.
*   **Widget de Música (`addons/music_widget`)**: Un servidor web local impulsado por FastAPI y Uvicorn que obtiene tu pista actual desde Last.fm y la expone como una fuente de navegador lista para usar en OBS.

---

## Cómo empezar (Desarrollo)

Asegurate de tener Python 3.11 o superior instalado en tu sistema.

1.  Cloná el repositorio.
    ```bash
    git clone https://github.com/Lostdou/OBDou
    cd OBDou
    ```

2.  **(Recomendado)** Creá y activá un entorno virtual para aislar las dependencias:
    ```bash
    python -m venv venv
    
    # En Windows:
    venv\Scripts\activate
    
    # En macOS/Linux:
    source venv/bin/activate
    ```
3.  Instalá todas las dependencias necesarias utilizando el archivo `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```
4.  Ejecutá la aplicación principal:
    ```bash
    python app.py
    ```
5.  Configurá tu canal de Twitch, el comando de TTS, tus preferencias del avatar y las credenciales de Last.fm desde la interfaz gráfica. El archivo `config.json` se generará automáticamente en la raíz del proyecto para guardar tus preferencias.

---

## Estructura del Proyecto

El proyecto está diseñado de forma modular para separar la interfaz gráfica de la lógica de fondo:

```text
OBDou/
├── app.py                  # Entry point principal de la aplicación y enrutador de subprocesos
├── app_paths.py            # Gestor de rutas absolutas (compatible con PyInstaller)
├── main.py                 # Listener de eventos y conexión WebSocket con OBS
├── requirements.txt        # Lista de dependencias del proyecto
├── config.json             # Archivo autogenerado con la configuración del usuario
├── ui/                     # Interfaz gráfica (Tkinter)
│   ├── main_window.py      # Controlador principal de navegación de la UI
│   └── menus/              # Vistas modulares (Conexión, TTS, Avatar, Música)
├── addons/                 # Módulos lógicos independientes
│   ├── reactivekb/         # Lógica de Pygame y sensores del avatar
│   ├── tts/                # Bot IRC de Twitch y motor gTTS
│   └── music_widget/       # Servidor web local de Last.fm
└── assets/                 # Recursos estáticos
    ├── common/             # Iconos de la app
    ├── reactivekb/         # Sprites y partes del avatar
    └── music_widget/       # HTML y CSS del widget
```

---

## Compilación

Si querés generar un ejecutable independiente (portátil) para no tener que depender de la consola de Python ni del entorno virtual, podés usar **PyInstaller**. 

El siguiente comando empaqueta la aplicación en modo ventana (`--windowed`) y se asegura de incluir todas las dependencias ocultas que `uvicorn` necesita para levantar el widget de música asíncrono sin lanzar errores:

```bash
pyinstaller --noconfirm --onedir --windowed --icon "assets\common\icon.ico" --name "OBDou" --hidden-import "uvicorn.loops.auto" --hidden-import "uvicorn.loops.asyncio" --hidden-import "uvicorn.protocols.http.auto" --hidden-import "uvicorn.protocols.http.h11_impl" --hidden-import "uvicorn.protocols.websockets.auto" --hidden-import "uvicorn.protocols.websockets.websockets_impl" --hidden-import "uvicorn.lifespan.on" "app.py"
```

> **Nota:** La compilación generará una carpeta `output/OBDou`. Recordá copiar tu carpeta `assets/` dentro de esa carpeta compilada para que el ejecutable encuentre las imágenes y el archivo HTML.

---

## Requisitos y Configuración de OBS

*   **Python:** 3.11 o superior.
*   **OBS Studio:** la app se encarga de configurar el apartado de WebSockets.
*   Para capturar el **Avatar**, añadí una fuente de captura de ventana en OBS apuntando a la ventana "Avatar" y aplicá un filtro de "Fondo Croma" al color verde.
*   Para capturar el **Widget de Música**, añadí una fuente de navegador apuntando a: [http://127.0.0.1:6767/music](http://127.0.0.1:6767/music).