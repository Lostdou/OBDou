import tkinter as tk


class ConexionMenu(tk.Frame):
    def __init__(self, parent, on_autoconfigurar, on_toggle_conexion):
        super().__init__(parent, bg="#f0f0f0")

        tk.Label(self, text="1. Preparar OBS", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(pady=(15, 5))
        self.btn_auto = tk.Button(
            self, text="Autoconfigurar OBS (Cerrar antes)", bg="#2196F3", fg="white",
            relief="flat", cursor="hand2", command=on_autoconfigurar
        )
        self.btn_auto.pack(pady=5, ipadx=10, ipady=3)

        tk.Frame(self, height=2, bd=1, relief="sunken").pack(fill="x", padx=20, pady=10)

        tk.Label(self, text="2. Iniciar Servicios", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(pady=(5, 5))

        self.btn_conectar = tk.Button(
            self, text="▶ Conectar a OBS y Esperar", bg="#4CAF50", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", command=on_toggle_conexion
        )
        self.btn_conectar.pack(pady=15, ipadx=10, ipady=3)

        self.modo_prueba_var = tk.BooleanVar(value=False)
        self.chk_modo_prueba = tk.Checkbutton(
            self,
            text="Modo prueba (iniciar TTS sin transmitir)",
            variable=self.modo_prueba_var,
            bg="#f0f0f0", font=("Segoe UI", 8), fg="#555",
            activebackground="#f0f0f0"
        )
        self.chk_modo_prueba.pack(pady=(0, 5))

        self.lbl_estado = tk.Label(self, text="Desconectado", fg="red", bg="#f0f0f0")
        self.lbl_estado.pack()

    def modo_prueba_activo(self):
        return self.modo_prueba_var.get()

    def actualizar_estado(self, mensaje, color):
        """Callback pasado al thread del listener para reportar estado."""
        self.lbl_estado.config(text=mensaje, fg=color)

    def set_conectar_habilitado(self, habilitado):
        self.btn_conectar.config(state=tk.NORMAL if habilitado else tk.DISABLED)

    def set_conectado_ui(self, conectado):
        """Refleja en la UI si la conexión está activa o no."""
        estado_widgets = tk.DISABLED if conectado else tk.NORMAL
        self.btn_auto.config(state=estado_widgets)
        self.chk_modo_prueba.config(state=estado_widgets)

        if conectado:
            self.btn_conectar.config(text="■ Detener Conexión", bg="#f44336")
            self.actualizar_estado("Conectando...", "orange")
        else:
            self.btn_conectar.config(text="▶ Conectar a OBS y Esperar", bg="#4CAF50")
            self.actualizar_estado("Desconectado", "red")