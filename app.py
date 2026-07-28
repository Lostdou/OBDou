import sys
import tkinter as tk
from ui.main_window import AppOBDOU

if __name__ == "__main__":
    if "--run-avatar" in sys.argv:
        from addons.reactivekb import reactivekb
        reactivekb.main()

    elif "--run-music" in sys.argv:
        import uvicorn
        from addons.music_widget.music_widget import app as music_app
        uvicorn.run(music_app, host="127.0.0.1", port=6767, log_config=None)

    else:
        ventana = tk.Tk()
        app = AppOBDOU(ventana)
        ventana.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.validar_estado_inicial()
        ventana.mainloop()