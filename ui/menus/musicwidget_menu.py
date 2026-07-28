import tkinter as tk
from tkinter import messagebox


class MusicWidgetMenu(tk.Frame):

    def __init__(self, parent, config_data, on_toggle_music):
        super().__init__(parent, bg="#f0f0f0")

        header_musica = tk.Frame(self, bg="#f0f0f0")
        header_musica.pack(fill="x", padx=20, pady=(15, 0))
        tk.Label(header_musica, text="Credenciales de Last.fm", font=("Segoe UI", 12, "bold"), bg="#f0f0f0").pack(side="left")
        tk.Button(
            header_musica, text="ℹ", bg="#e0e0e0", fg="#333",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
            width=2, activebackground="#cfcfcf",
            command=self.mostrar_info_musica
        ).pack(side="right")

        tk.Label(self, text="Usuario:", font=("Segoe UI", 9, "bold"), bg="#f0f0f0").pack()
        self.entry_lf_user = tk.Entry(self, width=30)
        self.entry_lf_user.insert(0, config_data.get("lastfm_user", ""))
        self.entry_lf_user.pack(pady=2)

        tk.Label(self, text="API Key:", font=("Segoe UI", 9, "bold"), bg="#f0f0f0").pack(pady=(10, 0))
        self.entry_lf_api = tk.Entry(self, width=30)
        self.entry_lf_api.insert(0, config_data.get("lastfm_api", ""))
        self.entry_lf_api.pack(pady=2)

        self.btn_launch_music = tk.Button(
            self, text="  Iniciar Widget Música", bg="#FF9800", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=on_toggle_music
        )
        self.btn_launch_music.pack(pady=(20, 5), ipadx=10, ipady=3)

        # Bloque con la URL para el navegador de OBS, oculto hasta que el widget arranque
        self.music_url_frame = tk.Frame(self, bg="#f0f0f0")

        tk.Label(
            self.music_url_frame, text="Agregala como Fuente de Navegador en OBS:",
            font=("Segoe UI", 8, "bold"), bg="#f0f0f0", fg="#555"
        ).pack()

        fila_url = tk.Frame(self.music_url_frame, bg="#f0f0f0")
        fila_url.pack(pady=4)

        self.entry_music_url = tk.Entry(fila_url, width=28, justify="center", font=("Segoe UI", 9))
        self.entry_music_url.insert(0, "http://localhost:6767/music")
        self.entry_music_url.config(state="readonly", readonlybackground="white")
        self.entry_music_url.pack(side="left", padx=(0, 5))

        self.btn_copy_music_url = tk.Button(
            fila_url, text="Copiar", bg="#e0e0e0", fg="#333",
            font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
            activebackground="#cfcfcf", command=self.copiar_url_music
        )
        self.btn_copy_music_url.pack(side="left")

        tk.Label(
            self.music_url_frame, text="Resolución recomendada: 400 x 150 px",
            font=("Segoe UI", 8), bg="#f0f0f0", fg="#777"
        ).pack(pady=(2, 10))


    def obtener_credenciales(self):
        return self.entry_lf_user.get().strip(), self.entry_lf_api.get().strip()

    def set_running_ui(self, corriendo):
        if corriendo:
            self.btn_launch_music.config(text="  Detener Widget Música", bg="#f44336")
            self.music_url_frame.pack(pady=(0, 10))
        else:
            self.btn_launch_music.config(text="  Iniciar Widget Música", bg="#FF9800")
            self.music_url_frame.pack_forget()


    def copiar_url_music(self):
        self.clipboard_clear()
        self.clipboard_append("http://localhost:6767/music")
        texto_original = self.btn_copy_music_url.cget("text")
        self.btn_copy_music_url.config(text="✓ Copiado")
        self.after(1200, lambda: self.btn_copy_music_url.config(text=texto_original))

    def mostrar_info_musica(self):
        messagebox.showinfo(
            "Cómo obtener tus credenciales de Last.fm",
            "Necesitás una cuenta de Last.fm y crear tu API key acá:\n\n"
            "https://www.last.fm/api/account/create\n\n"
            "En el formulario solo hace falta completar el nombre de la "
            "app. En 'Application page' podés poner cualquier URL, por "
            "ejemplo: https://lostdou.dev\n\n"
            "Una vez creada, copiá el Usuario y la API Key acá al lado."
        )