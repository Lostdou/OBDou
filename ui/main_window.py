import tkinter as tk
from tkinter import ttk, messagebox
import threading
import json
import os
import configparser
import subprocess
import sys

from main import iniciar_obs_listener, detener_obs_listener
from app_paths import get_base_dir

from ui.menus.conexion_menu import ConexionMenu
from ui.menus.tts_menu import TTSMenu
from ui.menus.avatar_menu import AvatarMenu
from ui.menus.musicwidget_menu import MusicWidgetMenu


def _config_path():
    return os.path.join(get_base_dir(), "config.json")


def load_config():
    config_file = _config_path()
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                data = json.load(f)
                if "lastfm_user" not in data: data["lastfm_user"] = ""
                if "lastfm_api" not in data: data["lastfm_api"] = ""
                return data
        except:
            pass
    return {"channel": "", "comando": "!s", "lastfm_user": "", "lastfm_api": ""}


def save_config(channel, comando, lastfm_user, lastfm_api):
    with open(_config_path(), "w") as f:
        json.dump({
            "channel": channel,
            "comando": comando,
            "lastfm_user": lastfm_user,
            "lastfm_api": lastfm_api
        }, f)


def is_obs_configured():
    """Verifica si el WebSocket de OBS ya está configurado correctamente leyendo el .ini."""
    appdata = os.getenv('APPDATA')
    if not appdata: return False
    obs_path = os.path.join(appdata, 'obs-studio', 'global.ini')
    if not os.path.exists(obs_path): return False

    config = configparser.ConfigParser(strict=False)
    config.read(obs_path, encoding='utf-8-sig')
    try:
        enabled = config.get('OBSWebSocket', 'ServerEnabled') == 'true'
        no_auth = config.get('OBSWebSocket', 'AuthRequired') == 'false'
        return enabled and no_auth
    except:
        return False


def forzar_obs_websocket_sin_pass():
    appdata = os.getenv('APPDATA')
    if not appdata:
        return False, "No se encontró AppData."

    obs_path = os.path.join(appdata, 'obs-studio', 'global.ini')

    if not os.path.exists(obs_path):
        return False, "No se encontró OBS instalado."

    config = configparser.ConfigParser(strict=False)
    config.optionxform = str
    config.read(obs_path, encoding='utf-8-sig')

    if not config.has_section('OBSWebSocket'):
        config.add_section('OBSWebSocket')

    config.set('OBSWebSocket', 'ServerEnabled', 'true')
    config.set('OBSWebSocket', 'ServerPort', '4455')
    config.set('OBSWebSocket', 'AuthRequired', 'false')

    try:
        with open(obs_path, 'w', encoding='utf-8-sig') as configfile:
            config.write(configfile, space_around_delimiters=False)
        return True, "OBS configurado con éxito. Ya puedes abrirlo."
    except Exception as e:
        return False, str(e)


class AppOBDOU:
    """Ventana principal: arma las pestañas (una clase de UI por cada una) y
    concentra toda la lógica que no es puramente visual: config, OBS,
    lanzamiento de subprocesos y su muestreo (polling) periódico.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("OBDou")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        base_dir = get_base_dir()
        icon_path = os.path.join(base_dir, "assets", "common", "icon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(default=icon_path)

        config_data = load_config()

        # --- Estado y muestreo de subprocesos (vive acá, no en las UIs) ---
        self.avatar_process = None
        self._avatar_monitor_job = None
        self.music_process = None
        self._music_monitor_job = None
        self.conexion_activa = False

        # Rutas usadas por la lógica de subprocesos.
        # En modo compilado (frozen), sys.executable ES el intérprete: para
        # relanzar la propia app con una bandera (--run-avatar/--run-music)
        # no hace falta pasarle un .py, alcanza con el flag. En desarrollo,
        # en cambio, hay que decirle a python qué script correr.
        self.app_path = os.path.join(base_dir, "app.py")
        self.assets_dir = os.path.join(base_dir, "assets", "reactivekb")

        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', padding=[15, 5], font=('Segoe UI', 9))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        self.notebook.bind("<<NotebookTabChanged>>", self.al_cambiar_pestana)

        # --- Cada pestaña es su propia clase de UI; solo se le inyectan ---
        # --- los callbacks para disparar la lógica de esta clase.       ---
        self.tab_conexion = ConexionMenu(
            self.notebook,
            on_autoconfigurar=self.configurar_obs,
            on_toggle_conexion=self.toggle_conexion,
        )
        self.tab_tts = TTSMenu(
            self.notebook,
            config_data=config_data,
        )
        self.tab_avatar = AvatarMenu(
            self.notebook,
            assets_dir=self.assets_dir,
            on_toggle_avatar=self.toggle_avatar,
            on_avatar_running=self._avatar_corriendo,
        )
        self.tab_musica = MusicWidgetMenu(
            self.notebook,
            config_data=config_data,
            on_toggle_music=self.toggle_music,
        )

        self.notebook.add(self.tab_conexion, text="Conexión")
        self.notebook.add(self.tab_tts, text="TTS")
        self.notebook.add(self.tab_avatar, text="Avatar")
        self.notebook.add(self.tab_musica, text="Música")

    # ------------------------------------------------------------------
    # Comando para relanzarse a sí misma con una bandera (avatar / música)
    # ------------------------------------------------------------------
    def _comando_relanzar(self, flag):
        if getattr(sys, 'frozen', False):
            return [sys.executable, flag]
        return [sys.executable, self.app_path, flag]

    # ------------------------------------------------------------------
    # Navegación entre pestañas
    # ------------------------------------------------------------------
    def al_cambiar_pestana(self, event):
        pestana_actual = self.notebook.index(self.notebook.select())
        if pestana_actual == 2:  # Avatar
            self.tab_avatar.actualizar_labels_assets()

    # ------------------------------------------------------------------
    # OBS
    # ------------------------------------------------------------------
    def configurar_obs(self):
        respuesta = messagebox.askyesno("Confirmación", "¿OBS Studio está cerrado completamente?")
        if respuesta:
            exito, msj = forzar_obs_websocket_sin_pass()
            if exito:
                messagebox.showinfo("Éxito", msj)
                self.desbloquear_interfaz()  # Se liberan las pestañas tras el éxito
            else:
                messagebox.showerror("Error", f"No se pudo configurar: {msj}")

    def validar_estado_inicial(self):
        """Bloquea las pestañas de addons si OBS no está configurado."""
        if not is_obs_configured():
            self.notebook.tab(1, state="disabled")
            self.notebook.tab(2, state="disabled")
            self.tab_conexion.set_conectar_habilitado(False)
            self.tab_conexion.actualizar_estado("⚠️ Requiere Autoconfigurar OBS primero", "#FF9800")
        else:
            self.desbloquear_interfaz()

    def desbloquear_interfaz(self):
        """Libera la UI una vez que OBS está configurado correctamente."""
        self.notebook.tab(1, state="normal")
        self.notebook.tab(2, state="normal")
        self.tab_conexion.set_conectar_habilitado(True)
        self.tab_conexion.actualizar_estado("Desconectado", "red")

    # ------------------------------------------------------------------
    # Conexión a Twitch/OBS
    # ------------------------------------------------------------------
    def toggle_conexion(self):
        if self.conexion_activa:
            self.detener_conexion()
        else:
            self.iniciar_conexion()

    def iniciar_conexion(self):
        if self.music_process is not None and self.music_process.poll() is None:
            self.music_process.terminate()

        canal, comando = self.tab_tts.obtener_valores()
        if not canal or not comando:
            messagebox.showwarning("Faltan datos", "Completa los datos de Twitch en la pestaña TTS.")
            return

        lf_user, lf_api = self.tab_musica.obtener_credenciales()
        save_config(canal, comando, lf_user, lf_api)

        modo_prueba = self.tab_conexion.modo_prueba_activo()
        self.conexion_activa = True

        self.tab_conexion.set_conectado_ui(True)
        self.tab_tts.set_enabled(False)

        threading.Thread(
            target=iniciar_obs_listener,
            args=(canal, comando, self.tab_conexion.actualizar_estado, modo_prueba),
            daemon=True
        ).start()

    def detener_conexion(self):
        detener_obs_listener()
        self.conexion_activa = False

        self.tab_conexion.set_conectado_ui(False)
        self.tab_tts.set_enabled(True)

    def on_closing(self):
        detener_obs_listener()
        if self.avatar_process is not None and self.avatar_process.poll() is None:
            self.avatar_process.terminate()
        if self.music_process is not None and self.music_process.poll() is None:
            self.music_process.terminate()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Avatar: lanzamiento del subproceso y muestreo periódico de su estado
    # ------------------------------------------------------------------
    def _avatar_corriendo(self):
        return self.avatar_process is not None and self.avatar_process.poll() is None

    def toggle_avatar(self, opciones):
        if self._avatar_corriendo():
            self.detener_avatar()
        else:
            self.lanzar_avatar(opciones)

    def lanzar_avatar(self, opciones):
        comando = self._comando_relanzar("--run-avatar")

        if not opciones.get("usar_mouse", True): comando.append("no-mouse")
        if not opciones.get("teclado_completo", False): comando.append("simple-kb")
        if opciones.get("speak_head", False): comando.append("speak-head")

        try:
            self.avatar_process = subprocess.Popen(comando)
            self.tab_avatar.set_running_ui(True)
            self._monitorear_avatar()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el avatar: {e}")

    def detener_avatar(self):
        """Cierra la ventana del avatar y vuelve la UI al estado anterior."""
        if self._avatar_monitor_job is not None:
            self.root.after_cancel(self._avatar_monitor_job)
            self._avatar_monitor_job = None

        if self.avatar_process is not None and self.avatar_process.poll() is None:
            self.avatar_process.terminate()

        self.avatar_process = None
        self.tab_avatar.set_running_ui(False)

    def _monitorear_avatar(self):
        """Muestreo periódico: si el proceso murió solo, refleja el cambio en la UI."""
        if self.avatar_process is None:
            return
        if self.avatar_process.poll() is None:
            self._avatar_monitor_job = self.root.after(500, self._monitorear_avatar)
        else:
            self.avatar_process = None
            self._avatar_monitor_job = None
            self.tab_avatar.set_running_ui(False)

    # ------------------------------------------------------------------
    # Widget de música: lanzamiento del subproceso y muestreo periódico
    # ------------------------------------------------------------------
    def toggle_music(self):
        """Alterna el servidor de música y guarda las credenciales."""
        self.guardar_estado_general()

        music_corriendo = self.music_process is not None and self.music_process.poll() is None
        if music_corriendo:
            self.detener_music()
        else:
            self.lanzar_music()

    def lanzar_music(self):
        comando = self._comando_relanzar("--run-music")
        try:
            self.music_process = subprocess.Popen(comando)
            self.tab_musica.set_running_ui(True)
            self._monitorear_music()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar el widget de música: {e}")

    def detener_music(self):
        if self._music_monitor_job is not None:
            self.root.after_cancel(self._music_monitor_job)
            self._music_monitor_job = None
        if self.music_process is not None and self.music_process.poll() is None:
            self.music_process.terminate()
        self.music_process = None
        self.tab_musica.set_running_ui(False)

    def _monitorear_music(self):
        if self.music_process is None:
            return
        if self.music_process.poll() is None:
            self._music_monitor_job = self.root.after(500, self._monitorear_music)
        else:
            self.music_process = None
            self._music_monitor_job = None
            self.tab_musica.set_running_ui(False)

    def guardar_estado_general(self):
        """Guarda toda la configuración de las pestañas al archivo config."""
        canal, comando = self.tab_tts.obtener_valores()
        lf_user, lf_api = self.tab_musica.obtener_credenciales()
        save_config(canal, comando, lf_user, lf_api)