import obsws_python as obs
import time
from addons.tts.tts import TTSBot

bot_tts = None
is_running = False

def on_stream_state_changed(data):
    global bot_tts
    if bot_tts is None:
        return

    if data.output_active:
        print("[OBS] Stream en vivo. Iniciando TTS...")
        bot_tts.start()
    else:
        print("[OBS] Stream apagado. Deteniendo TTS...")
        bot_tts.stop()

def iniciar_obs_listener(channel, comando, callback_ui, modo_prueba=False):
    global bot_tts, is_running
    
    bot_tts = TTSBot(channel=channel, comando=comando)
    is_running = True

    if modo_prueba:
        # Modo prueba: arranca el TTS directo, sin conectar a OBS ni esperar
        # a que la transmisión esté en vivo. Útil para probar el bot de chat
        # sin tener que estar transmitiendo de verdad.
        callback_ui("Modo prueba: TTS iniciado (sin OBS)", "orange")
        print("[*] MODO PRUEBA: iniciando TTS sin esperar transmisión...")
        bot_tts.start()

        while is_running:
            time.sleep(1)
        return
    
    try:
        client = obs.EventClient(host="localhost", port=4455, password="")
        client.callback.register([on_stream_state_changed])
        
        callback_ui("Conectado a OBS. Esperando transmisión...", "green")
        print("[*] Escuchando eventos de OBS...")
        
        while is_running:
            time.sleep(1)
            
    except Exception as e:
        callback_ui(f"Error OBS: ¿Está abierto o configurado?", "red")
        print(f"[!] Error conectando a OBS: {e}")

def detener_obs_listener():
    global is_running, bot_tts
    is_running = False
    if bot_tts:
        bot_tts.stop()