import tkinter as tk
from tkinter import messagebox, filedialog
import os


class AvatarMenu(tk.Frame):
    def __init__(self, parent, assets_dir, on_toggle_avatar, on_avatar_running):
        super().__init__(parent, bg="#f0f0f0")
        self.assets_dir = assets_dir
        self._on_toggle_avatar = on_toggle_avatar
        self._on_avatar_running = on_avatar_running

        avatar_frame = tk.LabelFrame(self, text="Configuración de Assets", padx=10, pady=10, bg="#f0f0f0")
        avatar_frame.pack(fill="x", padx=20, pady=20)

        header_avatar = tk.Frame(avatar_frame, bg="#f0f0f0")
        header_avatar.pack(fill="x")
        tk.Label(header_avatar, text="Assets cargados:", font=("Segoe UI", 9), bg="#f0f0f0", fg="#555").pack(side="left")
        tk.Button(
            header_avatar, text="ℹ", bg="#e0e0e0", fg="#333",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
            width=2, activebackground="#cfcfcf", command=self.mostrar_info_avatar
        ).pack(side="right")

        self.lbl_char = tk.Label(avatar_frame, text=self.check_asset("mainchar.png", "Personaje principal"), bg="#f0f0f0")
        self.lbl_char.pack(anchor="w", padx=10, pady=2)

        self.lbl_mouse = tk.Label(avatar_frame, text=self.check_asset("mouse.png", "Brazo/Mouse"), bg="#f0f0f0")
        self.lbl_mouse.pack(anchor="w", padx=10, pady=2)

        self.lbl_kb = tk.Label(avatar_frame, text=self.check_asset("keyboard.png", "Teclado base (centro)"), bg="#f0f0f0")
        self.lbl_kb.pack(anchor="w", padx=10, pady=2)

        self.lbl_head = tk.Label(avatar_frame, text=self.check_asset("headspeak.png", "Cabeza Hablando"), bg="#f0f0f0")
        self.lbl_head.pack(anchor="w", padx=10, pady=2)

        self.buttons_container = tk.Frame(avatar_frame)
        self.buttons_container.pack(pady=(10, 5))

        tk.Button(
            self.buttons_container, text="📁 Ver y Gestionar Assets", bg="#009688", fg="white",
            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
            command=self.abrir_gestor_assets
        ).pack(side="left", padx=5, ipadx=5, ipady=2)

        # --- SISTEMA DESPLEGABLE DE AJUSTES ---
        self.ajustes_visibles = False

        self.btn_toggle_ajustes = tk.Button(
            self.buttons_container, text="⚙️ Ajustes ▼", bg="#e0e0e0", fg="#333333",
            font=("Segoe UI", 9), relief="flat", cursor="hand2", command=self._toggle_ajustes
        )
        self.btn_toggle_ajustes.pack(side="left", padx=5, ipadx=5, ipady=2)

        self.frame_ajustes = tk.Frame(avatar_frame, bg="#f9f9f9", bd=1, relief="solid")

        self.var_usar_mouse = tk.BooleanVar(value=True)
        self.chk_mouse = tk.Checkbutton(
            self.frame_ajustes, text="Habilitar brazo y mouse",
            variable=self.var_usar_mouse, bg="#f9f9f9", font=("Segoe UI", 9),
            activebackground="#f9f9f9", command=self.actualizar_labels_assets
        )
        self.chk_mouse.pack(anchor="w", padx=10, pady=(5, 2))

        self.var_teclado_completo = tk.BooleanVar(value=False)
        self.chk_teclado = tk.Checkbutton(
            self.frame_ajustes, text="Detectar todo el teclado (5 assets)",
            variable=self.var_teclado_completo, bg="#f9f9f9", font=("Segoe UI", 9),
            activebackground="#f9f9f9", command=self.actualizar_labels_assets
        )
        self.chk_teclado.pack(anchor="w", padx=10, pady=2)

        self.var_speak_head = tk.BooleanVar(value=False)
        self.chk_speak_head = tk.Checkbutton(
            self.frame_ajustes, text="Detectar micrófono (headspeak.png)",
            variable=self.var_speak_head, bg="#f9f9f9", font=("Segoe UI", 9),
            activebackground="#f9f9f9", command=self.actualizar_labels_assets
        )
        self.chk_speak_head.pack(anchor="w", padx=10, pady=(2, 5))
        # --------------------------------------

        self.btn_launch_avatar = tk.Button(
            avatar_frame, text="▶ Iniciar Avatar", bg="#9C27B0", fg="white",
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
            command=self._toggle_avatar
        )
        self.btn_launch_avatar.pack(pady=10, ipadx=10, ipady=3)

    # ------------------------------------------------------------------
    # Ajustes desplegables
    # ------------------------------------------------------------------
    def _toggle_ajustes(self):
        if self.ajustes_visibles:
            self.frame_ajustes.pack_forget()
            self.btn_toggle_ajustes.config(text="⚙️ Ajustes ▼")
            self.ajustes_visibles = False
        else:
            self.frame_ajustes.pack(fill="x", padx=30, pady=5, before=self.btn_launch_avatar)
            self.btn_toggle_ajustes.config(text="⚙️ Ajustes ▲")
            self.ajustes_visibles = True

    # ------------------------------------------------------------------
    # API consumida por main_window
    # ------------------------------------------------------------------
    def _toggle_avatar(self):
        opciones = {
            "usar_mouse": self.var_usar_mouse.get(),
            "teclado_completo": self.var_teclado_completo.get(),
            "speak_head": self.var_speak_head.get(),
        }
        self._on_toggle_avatar(opciones)

    def set_running_ui(self, corriendo):
        """main_window llama esto cuando el subproceso arrancó, se detuvo
        o murió solo (detectado por su muestreo periódico)."""
        if corriendo:
            self.btn_launch_avatar.config(text="■ Terminar Avatar", bg="#f44336")
        else:
            self.btn_launch_avatar.config(text="▶ Iniciar Avatar", bg="#9C27B0")

    # ------------------------------------------------------------------
    # Validación de assets (lógica de UI/disco, no de proceso)
    # ------------------------------------------------------------------
    def check_asset(self, filename, label_text):
        path = os.path.join(self.assets_dir, filename)
        if os.path.exists(path):
            try:
                img_tmp = tk.PhotoImage(file=path)
                return f"✅ {label_text} ({filename}) - {img_tmp.width()}x{img_tmp.height()}px"
            except Exception:
                return f"✅ {label_text} ({filename})"
        return f"❌ Falta {label_text} ({filename})"

    def actualizar_labels_assets(self):
        """Refresca los textos y valida si se puede iniciar el avatar según los booleanos."""
        char_ok = os.path.exists(os.path.join(self.assets_dir, "mainchar.png"))
        mouse_ok = os.path.exists(os.path.join(self.assets_dir, "mouse.png"))
        head_ok = os.path.exists(os.path.join(self.assets_dir, "headspeak.png"))
        kb_idle_ok = os.path.exists(os.path.join(self.assets_dir, "keyboard.png"))
        kb_mid_ok = os.path.exists(os.path.join(self.assets_dir, "keyboard+middle.png"))
        kb_left_ok = os.path.exists(os.path.join(self.assets_dir, "keyboard+left.png"))
        kb_right_ok = os.path.exists(os.path.join(self.assets_dir, "keyboard+right.png"))
        kb_space_ok = os.path.exists(os.path.join(self.assets_dir, "keyboard+spacebar.png"))

        self.lbl_char.config(text=self.check_asset("mainchar.png", "Personaje principal"))

        if self.var_usar_mouse.get():
            self.lbl_mouse.config(text=self.check_asset("mouse.png", "Brazo/Mouse"))
            req_mouse = mouse_ok
        else:
            self.lbl_mouse.config(text="⚪ Brazo/Mouse (Deshabilitado)")
            req_mouse = True

        if self.var_speak_head.get():
            self.lbl_head.config(text=self.check_asset("headspeak.png", "Cabeza Hablando"))
            req_head = head_ok
        else:
            self.lbl_head.config(text="⚪ Cabeza Hablando (Deshabilitado)")
            req_head = True

        if self.var_teclado_completo.get():
            if kb_idle_ok and kb_mid_ok and kb_left_ok and kb_right_ok and kb_space_ok:
                self.lbl_kb.config(text="✅ Teclado Completo (5/5 assets)")
                req_kb = True
            else:
                self.lbl_kb.config(text="❌ Teclado Completo (Faltan assets)")
                req_kb = False
        else:
            if kb_idle_ok and kb_mid_ok:
                self.lbl_kb.config(text="✅ Teclado Simple (Base + Centro)")
                req_kb = True
            else:
                self.lbl_kb.config(text="❌ Teclado Simple (Falta base o centro)")
                req_kb = False

        if not self._on_avatar_running():
            if char_ok and req_mouse and req_kb and req_head:
                self.btn_launch_avatar.config(state=tk.NORMAL, bg="#9C27B0")
            else:
                self.btn_launch_avatar.config(state=tk.DISABLED, bg="#CCCCCC")

    # ------------------------------------------------------------------
    # Diálogos informativos
    # ------------------------------------------------------------------
    def mostrar_info_avatar(self):
        messagebox.showinfo(
            "Cómo agregar el Avatar a OBS",
            "Cuando se abra la ventana del Avatar:\n\n"
            "1. Andá a OBS y agregá una fuente 'Captura de ventana' "
            "(Window Capture) apuntando a la ventana del Avatar.\n\n"
            "2. Agregale un filtro de Chroma Key (Clave de croma) a esa "
            "fuente, usando el verde de fondo del avatar.\n\n"
            "3. No minimices la ventana del Avatar mientras transmitís: "
            "podés dejarla de fondo (detrás de otras ventanas), pero "
            "minimizada la captura puede dejar de actualizarse."
        )

    # ------------------------------------------------------------------
    # Gestor de assets (ventana secundaria)
    # ------------------------------------------------------------------
    def abrir_gestor_assets(self):
        thumb_refs = []
        gestor_win = tk.Toplevel(self)
        gestor_win.title("Administrador de Assets")
        gestor_win.geometry("480x520")
        gestor_win.minsize(480, 360)
        gestor_win.config(bg="#f0f0f0")

        tk.Label(gestor_win, text="Listado de Assets Actuales", font=("Segoe UI", 11, "bold"), bg="#f0f0f0").pack(pady=(15, 10))

        contenedor = tk.Frame(gestor_win, bg="#f0f0f0")
        contenedor.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        canvas_lista = tk.Canvas(contenedor, bg="white", bd=1, relief="solid", highlightthickness=0)
        scrollbar = tk.Scrollbar(contenedor, orient="vertical", command=canvas_lista.yview)
        canvas_lista.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas_lista.pack(side="left", fill="both", expand=True)

        frame_lista = tk.Frame(canvas_lista, bg="white")
        ventana_frame = canvas_lista.create_window((0, 0), window=frame_lista, anchor="nw")

        def _actualizar_scrollregion(event=None):
            canvas_lista.configure(scrollregion=canvas_lista.bbox("all"))

        def _ajustar_ancho_frame(event):
            canvas_lista.itemconfig(ventana_frame, width=event.width)

        frame_lista.bind("<Configure>", _actualizar_scrollregion)
        canvas_lista.bind("<Configure>", _ajustar_ancho_frame)

        def _en_scroll_rueda(event):
            canvas_lista.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas_lista.bind_all("<MouseWheel>", _en_scroll_rueda)
        gestor_win.bind("<Destroy>", lambda e: canvas_lista.unbind_all("<MouseWheel>") if e.widget == gestor_win else None)

        assets_mapeo = {
            "Personaje Principal": "mainchar.png",
            "Cabeza Hablando (Mic)": "headspeak.png",
            "Brazo / Mouse": "mouse.png",
            "Teclado Base (Idle/Centro)": "keyboard.png",
            "Teclado Zona Izquierda": "keyboard+left.png",
            "Teclado Zona Media": "keyboard+middle.png",
            "Teclado Zona Derecha": "keyboard+right.png",
            "Teclado Barra Espaciadora": "keyboard+spacebar.png"
        }

        assets_recomendaciones = {
            "mainchar.png": (
                "Personaje Principal\n\n"
                "Tamaño recomendado: ~300 x 350 px\n\n"
                "Es el cuerpo base del avatar. Se dibuja fijo en pantalla, "
                "así que no necesita coincidir con nada más, pero sí debe "
                "dejar espacio libre donde luego se van a superponer el "
                "teclado y el mouse."
            ),
            "mouse.png": (
                "Brazo / Mouse\n\n"
                "Tamaño recomendado: ~250 x 250 px a 300 x 300 px\n\n"
                "El padding transparente dentro del lienzo importa tanto "
                "como el tamaño total: la imagen se ancla por su esquina "
                "superior izquierda, así que la mano/brazo debe estar "
                "ubicada dentro del lienzo en el punto donde querés que "
                "toque el mouse."
            ),
            "__keyboard__": (
                "Teclado (todos los estados)\n\n"
                "Tamaño recomendado: ~450 x 300 px\n\n"
                "MUY IMPORTANTE: keyboard.png, keyboard+left.png, "
                "keyboard+middle.png, keyboard+right.png y "
                "keyboard+spacebar.png deben compartir EXACTAMENTE el "
                "mismo tamaño de lienzo. Si uno tiene una resolución "
                "distinta, el teclado se va a ver \"vibrar\" o saltar de "
                "posición cada vez que cambia de estado."
            ),
        }

        def obtener_recomendacion(nombre_tecnico):
            if nombre_tecnico.startswith("keyboard"):
                return assets_recomendaciones["__keyboard__"]
            return assets_recomendaciones.get(nombre_tecnico, "No hay recomendación disponible para este asset.")

        def mostrar_recomendacion(nombre_tecnico):
            messagebox.showinfo("Medidas recomendadas", obtener_recomendacion(nombre_tecnico))

        def cargar_elementos():
            nonlocal thumb_refs
            thumb_refs = []

            for widget in frame_lista.winfo_children():
                widget.destroy()

            for etiqueta_amigable, nombre_tecnico in assets_mapeo.items():
                ruta_completa = os.path.join(self.assets_dir, nombre_tecnico)
                existe = os.path.exists(ruta_completa)

                info_res = "No encontrado"
                img_preview = None

                if existe:
                    try:
                        p_img = tk.PhotoImage(file=ruta_completa)
                        info_res = f"{p_img.width()} x {p_img.height()} px"

                        factor_w = max(1, p_img.width() // 40)
                        factor_h = max(1, p_img.height() // 40)
                        factor = max(factor_w, factor_h)

                        img_preview = p_img.subsample(factor, factor)
                        thumb_refs.append(img_preview)
                    except Exception:
                        info_res = "Formato no compatible"

                row = tk.Frame(frame_lista, bg="white", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
                row.pack(fill="x", padx=8, pady=4)

                thumb_holder = tk.Frame(row, bg="#f5f5f5", width=60, height=60,
                                         highlightthickness=1, highlightbackground="#d5d5d5")
                thumb_holder.pack(side="left", padx=12, pady=10)
                thumb_holder.pack_propagate(False)

                lbl_thumb = tk.Label(thumb_holder, bg="#f5f5f5")
                lbl_thumb.pack(fill="both", expand=True)
                if img_preview:
                    lbl_thumb.config(image=img_preview)
                else:
                    lbl_thumb.config(text="Sin\nimagen", fg="#999", font=("Segoe UI", 7), justify="center")

                info_frame = tk.Frame(row, bg="white")
                info_frame.pack(side="left", fill="both", expand=True, padx=(4, 5), pady=10)

                tk.Label(info_frame, text=etiqueta_amigable, font=("Segoe UI", 9, "bold"),
                         bg="white", fg="#222", anchor="w", justify="left").pack(fill="x")
                tk.Label(info_frame, text=nombre_tecnico, font=("Segoe UI", 8),
                         bg="white", fg="#999", anchor="w", justify="left").pack(fill="x")

                color_estado = "#2e7d32" if existe else "#c62828"
                tk.Label(info_frame, text=info_res, font=("Segoe UI", 8, "bold"),
                         bg="white", fg=color_estado, anchor="w").pack(fill="x", pady=(4, 0))

                btn_subir = tk.Button(row, text="Subir / Cambiar", bg="#FF9800", fg="white",
                                       font=("Segoe UI", 8, "bold"), relief="flat", cursor="hand2",
                                       activebackground="#FB8C00", activeforeground="white",
                                       command=lambda t=etiqueta_amigable, n=nombre_tecnico: reemplazar_asset(n, t))
                btn_subir.pack(side="right", padx=(4, 12), ipadx=6, ipady=4)

                btn_info = tk.Button(row, text="i", bg="#e0e0e0", fg="#333",
                                      font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2",
                                      width=2, activebackground="#cfcfcf",
                                      command=lambda t=etiqueta_amigable, n=nombre_tecnico: mostrar_recomendacion(n))
                btn_info.pack(side="right", padx=(0, 4), ipady=2)

        def reemplazar_asset(nombre_tecnico, desc):
            tipo_archivo = [("Archivos PNG", "*.png")]
            archivo_seleccionado = filedialog.askopenfilename(title=f"Seleccionar asset para: {desc}", filetypes=tipo_archivo)

            if archivo_seleccionado:
                try:
                    os.makedirs(self.assets_dir, exist_ok=True)
                    destino = os.path.join(self.assets_dir, nombre_tecnico)

                    with open(archivo_seleccionado, 'rb') as f_orig:
                        with open(destino, 'wb') as f_dest:
                            f_dest.write(f_orig.read())

                    messagebox.showinfo("Éxito", f"Asset actualizado correctamente como:\n{nombre_tecnico}")

                    cargar_elementos()
                    self.actualizar_labels_assets()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

        cargar_elementos()