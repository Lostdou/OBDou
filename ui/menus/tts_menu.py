import tkinter as tk


class TTSMenu(tk.Frame):
    def __init__(self, parent, config_data):
        super().__init__(parent, bg="#f0f0f0")

        tk.Label(self, text="Configuración de TTS", font=("Segoe UI", 12, "bold"), bg="#f0f0f0").pack(pady=(15, 5))
        tk.Label(
            self,
            text="El bot se conectará a tu chat de Twitch\ny leerá automáticamente al iniciar stream.",
            bg="#f0f0f0", justify="center"
        ).pack(pady=(0, 15))

        tk.Label(self, text="Canal de Twitch:", font=("Segoe UI", 9, "bold"), bg="#f0f0f0").pack()
        self.entry_canal = tk.Entry(self, width=30)
        self.entry_canal.insert(0, config_data.get("channel", ""))
        self.entry_canal.pack(pady=2)

        tk.Label(self, text="Comando para leer:", font=("Segoe UI", 9, "bold"), bg="#f0f0f0").pack(pady=(10, 0))
        self.entry_comando = tk.Entry(self, width=30)
        self.entry_comando.insert(0, config_data.get("comando", "!s"))
        self.entry_comando.pack(pady=2)

    # ------------------------------------------------------------------
    # API consumida por main_window
    # ------------------------------------------------------------------
    def obtener_valores(self):
        return self.entry_canal.get().strip(), self.entry_comando.get().strip()

    def set_enabled(self, habilitado):
        estado = tk.NORMAL if habilitado else tk.DISABLED
        self.entry_canal.config(state=estado)
        self.entry_comando.config(state=estado)